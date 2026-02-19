from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.message_service.apps.msg_service.services.message_service import MessageService

router = APIRouter()

class MessageCreate(BaseModel):
    from_user_id: str
    to_user_id: str
    body: str = Field(..., min_length=1, max_length=4000)

@router.post("/messages")
async def post_message(payload: MessageCreate):
    service = MessageService()
    try:
        created = await service.create_message(payload)
        return {"ok": True, "message_id": created["message_id"], "created_at": created["created_at"]}
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc))

@router.get("/messages/inbox")
async def inbox(to_user_id: str, limit: int = 20):
    service = MessageService()
    items = await service.get_inbox(to_user_id=to_user_id, limit=limit)
    return {"ok": True, "items": items}
