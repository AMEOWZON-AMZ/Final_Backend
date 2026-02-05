from fastapi import APIRouter
from pydantic import BaseModel

from services.message_service.apps.msg_service.services.device_token_service import DeviceTokenService

router = APIRouter()

class DeviceTokenUpsert(BaseModel):
    user_id: str
    token: str
    platform: str = "fcm"

@router.post("/device-token")
async def upsert_device_token(payload: DeviceTokenUpsert):
    service = DeviceTokenService()
    await service.upsert_token(payload)
    return {"ok": True}
