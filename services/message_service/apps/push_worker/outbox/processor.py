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

    to_user_id = payload.get("to_user_id")
    token = None
    if to_user_id:
        token_repo = DeviceTokenRepository()
        token_item = token_repo.get_token(to_user_id)
        if token_item:
            token = token_item.get("token")

    if not token:
        _mark_retry_or_failed(repo, event_id, attempt_count, "missing device token")
        return

    ok, error = send_fcm(token, payload)
    if ok:
        repo.mark_sent(event_id=event_id, now_iso=now_utc_iso())
    else:
        _mark_retry_or_failed(repo, event_id, attempt_count, error)


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
