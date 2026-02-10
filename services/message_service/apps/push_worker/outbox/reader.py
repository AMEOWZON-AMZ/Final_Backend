from services.message_service.apps.msg_service.repositories.outbox_repo import OutboxRepository
from services.message_service.shared.time import now_utc_iso


def fetch_ready_events(limit=10):
    repo = OutboxRepository()
    return repo.query_ready(limit=limit, now_iso=now_utc_iso())


def claim_event(event) -> bool:
    event_id = event.get("event_id")
    if not event_id:
        return False
    repo = OutboxRepository()
    return repo.try_mark_processing(event_id=event_id, now_iso=now_utc_iso())
