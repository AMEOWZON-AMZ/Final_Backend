from services.message_service.apps.msg_service.repositories.message_repo import MessageRepository
from services.message_service.apps.msg_service.repositories.outbox_repo import OutboxRepository
from services.message_service.apps.msg_service.repositories.friend_repo import FriendRepository
from services.message_service.apps.msg_service.repositories.audit_repo import AuditRepository
from services.message_service.shared.id import new_id
from services.message_service.shared.time import now_utc_iso
from services.message_service.shared.models import OutboxEvent
from services.message_service.shared.sqs import send_sqs_job

class MessageService:
    def __init__(self):
        self.messages = MessageRepository()
        self.outbox = OutboxRepository()
        self.friends = FriendRepository()
        self.audit = AuditRepository()

    async def create_message(self, payload):
        # Friend-only check
        # if not self.friends.is_accepted(payload.from_user_id, payload.to_user_id):
        #     raise ValueError("Not friends")

        message_id = new_id()
        created_at = now_utc_iso()

        # 1) Write message first
        self.messages.put_message(
            message_id=message_id,
            from_user_id=payload.from_user_id,
            to_user_id=payload.to_user_id,
            body=payload.body,
            created_at=created_at,
        )

        # # 2) Write outbox event
        # event = OutboxEvent(
        #     event_type="MESSAGE",
        #     from_user_id=payload.from_user_id,
        #     to_user_id=payload.to_user_id,
        #     ref_id=message_id,
        #     created_at=created_at,
        #     status="PENDING",
        #     retries=0,
        # )
        # self.outbox.put_event(event)

        # # 3) Optional SQS enqueue (minimal payload)
        # send_sqs_job(event)

        # # 4) Audit event (TTL handled by table policy)
        # self.audit.put_event(
        #     event_type="MESSAGE",
        #     ref_id=message_id,
        #     from_user_id=payload.from_user_id,
        #     to_user_id=payload.to_user_id,
        #     created_at=created_at,
        # )

        return {"message_id": message_id, "created_at": created_at}

    async def get_inbox(self, to_user_id: str, limit: int = 20):
        return self.messages.query_inbox(to_user_id=to_user_id, limit=limit)
