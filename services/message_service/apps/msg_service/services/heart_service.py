from services.message_service.apps.msg_service.repositories.heart_repo import HeartRepository
from services.message_service.apps.msg_service.repositories.outbox_repo import OutboxRepository
from services.message_service.apps.msg_service.repositories.friend_repo import FriendRepository
from services.message_service.apps.msg_service.repositories.audit_repo import AuditRepository
from services.message_service.shared.id import new_id
from services.message_service.shared.time import now_utc_iso
from services.message_service.shared.models import OutboxEvent
from services.message_service.shared.sqs import send_sqs_job

class HeartService:
    def __init__(self):
        self.hearts = HeartRepository()
        self.outbox = OutboxRepository()
        self.friends = FriendRepository()
        self.audit = AuditRepository()

    async def create_heart(self, payload):
        if not self.friends.is_accepted(payload.from_user_id, payload.to_user_id):
            raise ValueError("Not friends")

        heart_id = new_id()
        created_at = now_utc_iso()

        self.hearts.put_heart(
            heart_id=heart_id,
            from_user_id=payload.from_user_id,
            to_user_id=payload.to_user_id,
            created_at=created_at,
        )

        event = OutboxEvent(
            event_type="HEART",
            from_user_id=payload.from_user_id,
            to_user_id=payload.to_user_id,
            ref_id=heart_id,
            created_at=created_at,
            status="PENDING",
            retries=0,
        )
        self.outbox.put_event(event)
        send_sqs_job(event)

        self.audit.put_event(
            event_type="HEART",
            ref_id=heart_id,
            from_user_id=payload.from_user_id,
            to_user_id=payload.to_user_id,
            created_at=created_at,
        )

        return {"heart_id": heart_id, "created_at": created_at}

    async def get_received(self, to_user_id: str, limit: int = 20):
        return self.hearts.query_received(to_user_id=to_user_id, limit=limit)
