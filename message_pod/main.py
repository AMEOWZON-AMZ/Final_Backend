"""
Message Pod 메인 애플리케이션
실시간 메시징 및 채팅 서비스
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from common.config.base_config import base_config
from common.utils.logger import get_logger
from message_pod.api.v1.api import api_router
from message_pod.api.health import health_router

logger = get_logger("message_pod")

app = FastAPI(
    title="Message Pod API",
    description="실시간 메시징 및 채팅 서비스",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=base_config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=base_config.ALLOWED_METHODS,
    allow_headers=base_config.ALLOWED_HEADERS,
)

# 라우터 등록
app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    logger.info("Message Pod 시작됨")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Message Pod 종료됨")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8003,
        reload=base_config.DEBUG
    )