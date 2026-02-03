"""
Inference Pod 메인 애플리케이션
AI/ML 모델 추론 서비스
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from common.config.base_config import base_config
from common.utils.logger import get_logger
from inference_pod.api.v1.api import api_router
from inference_pod.api.health import health_router

logger = get_logger("inference_pod")

app = FastAPI(
    title="Inference Pod API",
    description="AI/ML 모델 추론 서비스",
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
    logger.info("Inference Pod 시작됨")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Inference Pod 종료됨")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=base_config.DEBUG
    )