from fastapi import FastAPI
from dotenv import load_dotenv
from pathlib import Path

from services.inference_service.app.routes.health import router as health_router
from services.inference_service.app.routes.inference import router as inference_router

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

app = FastAPI(title="inference-status-service", version="1.0.0")

app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(inference_router, tags=["events"])
