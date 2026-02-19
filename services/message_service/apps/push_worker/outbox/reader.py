from services.message_service.apps.msg_service.repositories.outbox_repo import OutboxRepository
from services.message_service.shared.time import now_utc_iso


def fetch_ready_events(limit=10):
    # 처리 가능한 Outbox 이벤트 목록 조회.
    repo = OutboxRepository()
    return repo.query_ready(limit=limit, now_iso=now_utc_iso())


def claim_event(event) -> bool:
    # 이벤트를 PROCESSING으로 선점 시도.
    event_id = event.get("event_id")
    if not event_id:
        return False
    repo = OutboxRepository()
    return repo.try_mark_processing(event_id=event_id, now_iso=now_utc_iso())
