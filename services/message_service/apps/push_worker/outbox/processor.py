from services.message_service.apps.msg_service.repositories.outbox_repo import OutboxRepository
from services.message_service.apps.msg_service.repositories.device_token_repo import DeviceTokenRepository
from services.message_service.apps.push_worker.outbox.reader import fetch_ready_events, claim_event
from services.message_service.apps.push_worker.fcm.client import send_fcm
from services.message_service.shared.time import now_utc_iso, utc_iso_after_seconds

MAX_ATTEMPTS = 8
BASE_BACKOFF_SECONDS = 5
MAX_BACKOFF_SECONDS = 300


def process_outbox():
    events = fetch_ready_events(limit=10)
    for event in events:
        if not claim_event(event):
            continue
        handle_event(event, already_claimed=True)


def handle_event(event: dict, already_claimed: bool = False):
    event_id = _extract_event_id(event)
    if not event_id:
        return

    repo = OutboxRepository()

    if not already_claimed:
        if not repo.try_mark_processing(event_id=event_id, now_iso=now_utc_iso()):
            return

    item = event
    if "payload" not in item or "attempt_count" not in item:
        item = repo.get_event(event_id)
        if not item:
            return

    if item.get("status") == "SENT":
        return

    payload = item.get("payload") or {}
    attempt_count = int(item.get("attempt_count", 0))
    target_user_ids = _extract_target_user_ids(payload)
    if not target_user_ids:
        _mark_retry_or_failed(repo, event_id, attempt_count, "missing target user id(s)")
        return

    token_repo = DeviceTokenRepository()
    errors = []
    sent_count = 0

    for user_id in target_user_ids:
        token_item = token_repo.get_token(user_id)
        token = token_item.get("token") if token_item else None
        if not token:
            errors.append(f"missing token:{user_id}")
            continue

        ok, error = send_fcm(token, payload)
        if ok:
            sent_count += 1
        else:
            errors.append(f"send failed:{user_id}:{error}")

    if errors:
        summary = "; ".join(errors[:5])
        _mark_retry_or_failed(repo, event_id, attempt_count, summary)
        return

    if sent_count == 0:
        _mark_retry_or_failed(repo, event_id, attempt_count, "no recipients sent")
        return

    repo.mark_sent(event_id=event_id, now_iso=now_utc_iso())


def _mark_retry_or_failed(repo: OutboxRepository, event_id: str, attempt_count: int, error: str | None):
    next_attempt = attempt_count + 1
    if next_attempt >= MAX_ATTEMPTS:
        repo.mark_failed(event_id=event_id, attempt_count=next_attempt, last_error=error)
        return

    backoff_seconds = _compute_backoff_seconds(next_attempt)
    next_retry_at = utc_iso_after_seconds(backoff_seconds)
    repo.mark_retry(
        event_id=event_id,
        attempt_count=next_attempt,
        next_retry_at=next_retry_at,
        last_error=error,
    )


def _compute_backoff_seconds(attempt_count: int) -> int:
    return min(BASE_BACKOFF_SECONDS * (2 ** (attempt_count - 1)), MAX_BACKOFF_SECONDS)


def _extract_event_id(event: dict) -> str | None:
    return event.get("event_id") or event.get("message_id") or event.get("ref_id")


def _extract_target_user_ids(payload: dict) -> list[str]:
    multi = payload.get("to_user_ids")
    if isinstance(multi, list):
        deduped = []
        seen = set()
        for value in multi:
            if not isinstance(value, str):
                continue
            user_id = value.strip()
            if not user_id or user_id in seen:
                continue
            seen.add(user_id)
            deduped.append(user_id)
        if deduped:
            return deduped

    single = payload.get("to_user_id")
    if isinstance(single, str) and single.strip():
        return [single.strip()]
    return []
