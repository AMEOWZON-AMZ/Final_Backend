import os
from services.message_service.apps.msg_service.repositories.outbox_repo import OutboxRepository
from services.message_service.apps.push_worker.outbox.reader import fetch_ready_events, claim_event
from services.message_service.apps.push_worker.fcm.client import send_fcm
from services.message_service.shared.time import now_utc_iso, utc_iso_after_seconds

MAX_ATTEMPTS = 8
BASE_BACKOFF_SECONDS = 5
MAX_BACKOFF_SECONDS = 300


def process_outbox():
    # Outbox 이벤트를 조회해 처리.
    events = fetch_ready_events(limit=10)
    for event in events:
        if not claim_event(event):
            continue
        handle_event(event, already_claimed=True)


def handle_event(event: dict, already_claimed: bool = False):
    # 단일 이벤트 처리(FCM 전송 후 상태 전이).
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
    token = payload.get("receiver_token") or os.getenv("TEST_RECEIVER_FCM_TOKEN", "")
    # TODO: replace with UserDevices table lookup
    if not token:
        _mark_retry(repo, event_id, item, "missing receiver token")
        return

    ok, error = send_fcm(token, payload)
    if ok:
        repo.mark_sent(event_id=event_id, now_iso=now_utc_iso())
    else:
        _mark_retry(repo, event_id, item, error)


def _mark_retry(repo: OutboxRepository, event_id: str, item: dict, error: str | None):
    # 실패 시 RETRY 상태로 전환하고 재시도 시각 설정.
    attempt_count = int(item.get("attempt_count", 0)) + 1
    backoff_seconds = _compute_backoff_seconds(attempt_count)
    next_retry_at = utc_iso_after_seconds(backoff_seconds)
    repo.mark_retry(
        event_id=event_id,
        attempt_count=attempt_count,
        next_retry_at=next_retry_at,
        last_error=error,
    )


def _compute_backoff_seconds(attempt_count: int) -> int:
    # 시도 횟수 기반 지수 백오프 계산.
    return min(BASE_BACKOFF_SECONDS * (2 ** (attempt_count - 1)), MAX_BACKOFF_SECONDS)


def _extract_event_id(event: dict) -> str | None:
    # 이벤트 dict에서 event_id 추출.
    return event.get("event_id") or event.get("message_id") or event.get("ref_id")
