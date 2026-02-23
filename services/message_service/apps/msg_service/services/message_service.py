from services.message_service.apps.msg_service.repositories.message_repo import MessageRepository
from services.message_service.apps.msg_service.repositories.friend_repo import FriendRepository
from services.message_service.apps.msg_service.repositories.audit_repo import AuditRepository
from services.message_service.shared.id import new_id
from services.message_service.shared.time import now_utc_iso
from services.message_service.shared.models import OutboxEvent
from services.message_service.shared.push_templates import random_message_push_text


class MessageService:
    def __init__(self):
        self.messages = MessageRepository()
        self.friends = FriendRepository()
        self.audit = AuditRepository()

    async def create_message(self, payload):
        # Friend-only check
        # if not self.friends.is_accepted(payload.from_user_id, payload.to_user_id):
        #     raise ValueError("Not friends")

        message_id = new_id()
        created_at = now_utc_iso()

        message_item = self.messages.build_message_item(
            message_id=message_id,
            from_user_id=payload.from_user_id,
            to_user_id=payload.to_user_id,
            body=payload.body,
            created_at=created_at,
            nickname=payload.nickname
        )
        title, body = random_message_push_text(payload.body)

        # Push worker resolves device token from DeviceTokens table using to_user_id.
        event = OutboxEvent(
            event_id=message_id,
            event_type="PUSH_SEND",
            status="PENDING",
            attempt_count=0,
            next_retry_at=created_at,
            created_at=created_at,
            payload={
                "title": title,
                "body": body,
                "message_id": message_id,
                "from_user_id": payload.from_user_id,
                "to_user_id": payload.to_user_id,
            },
        )

        self.messages.put_message_with_outbox(
            message_item=message_item,
            outbox_item=event.to_item(),
        )

        return {"message_id": message_id, "created_at": created_at}

    async def get_inbox(self, to_user_id: str, limit: int = 20):
        return self.messages.query_inbox(to_user_id=to_user_id, limit=limit)
