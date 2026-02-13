from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.message_service.apps.msg_service.services.heart_service import HeartService

router = APIRouter()

class HeartCreate(BaseModel):
    from_user_id: str
    to_user_id: str
    nickname: str

@router.post("/hearts")
async def post_heart(payload: HeartCreate):
    service = HeartService()
    try:
        created = await service.create_heart(payload)
        return {"ok": True, "heart_id": created["heart_id"], "created_at": created["created_at"]}
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc))

@router.get("/hearts/received")
async def received(to_user_id: str, limit: int = 20):
    service = HeartService()
    items = await service.get_received(to_user_id=to_user_id, limit=limit)
    return {"ok": True, "items": items}
