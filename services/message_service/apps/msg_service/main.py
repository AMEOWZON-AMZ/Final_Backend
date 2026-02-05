from fastapi import FastAPI
import os
from services.message_service.shared.config import settings
from dotenv import load_dotenv
from pathlib import Path
from services.message_service.apps.msg_service.routers.messages import router as messages_router
from services.message_service.apps.msg_service.routers.hearts import router as hearts_router
from services.message_service.apps.msg_service.routers.device_token import router as device_token_router
from services.message_service.apps.msg_service.routers.health import router as health_router

app = FastAPI(title="msg-service", version="1.0.0")

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(messages_router, tags=["messages"])
app.include_router(hearts_router, tags=["hearts"])
app.include_router(device_token_router, tags=["device-token"])

# 리전 확인
print("AWS_REGION =", settings.aws_region)
print("DDB_TABLE  =", os.getenv("DDB_MESSAGES_TABLE"))