from services.message_service.apps.msg_service.repositories.device_token_repo import DeviceTokenRepository
from services.message_service.shared.time import now_utc_iso

class DeviceTokenService:
    def __init__(self):
        self.tokens = DeviceTokenRepository()

    async def upsert_token(self, payload):
        self.tokens.put_token(
            user_id=payload.user_id,
            token=payload.token,
            platform=payload.platform,
            updated_at=now_utc_iso(),
        )
