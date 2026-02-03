from sqlalchemy.orm import Session
from sqlalchemy import text
import time
import os
from typing import Dict, Any

from app.core.database import get_db
from app.core.config import settings
from app.schemas.response import success_response, error_response

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

health_router = APIRouter()


@health_router.get("/")
async def health_check():
    """기본 헬스체크 - 통일된 응답 구조"""
    return success_response(
        data={
            "service": "user-pod-backend",
            "version": "1.0.0",
            "uptime": int(time.time()),
            "environment": settings.ENVIRONMENT
        }
    )


@health_router.get("/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """상세 헬스체크 - DB 연결 포함, HTTP 503 반환"""
    checks = {}
    overall_status = "healthy"
    
    # 데이터베이스 연결 확인
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = {
            "status": "healthy",
            "message": "Connected successfully",
            "type": "sqlite" if "sqlite" in settings.DATABASE_URL else "postgresql"
        }
    except Exception as e:
        overall_status = "unhealthy"
        checks["database"] = {
            "status": "unhealthy",
            "message": f"Connection failed: {str(e)}",
            "type": "sqlite" if "sqlite" in settings.DATABASE_URL else "postgresql"
        }
    
    if overall_status == "healthy":
        return success_response(
            data={
                "service": "user-pod-backend",
                "version": "1.0.0",
                "environment": settings.ENVIRONMENT,
                "checks": checks
            }
        )
    else:
        # Unhealthy 시 HTTP 503 반환
        return JSONResponse(
            status_code=503,
            content=error_response(
                message="Some systems are unhealthy",
                error_code="HEALTH_CHECK_FAILED",
                details={"checks": checks}
            )
        )


@health_router.get("/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """Kubernetes Readiness Probe - HTTP 503 반환"""
    try:
        # 데이터베이스 연결 확인
        db.execute(text("SELECT 1"))
        return success_response(
            data={"status": "ready"}
        )
    except Exception as e:
        # Not Ready 시 HTTP 503 반환
        return JSONResponse(
            status_code=503,
            content=error_response(
                message="Service is not ready",
                error_code="SERVICE_NOT_READY",
                details={"error": str(e)}
            )
        )


@health_router.get("/live")
async def liveness_check():
    """Kubernetes Liveness Probe - 통일된 응답 구조"""
    return success_response(
        data={
            "status": "alive",
            "uptime": int(time.time())
        }
    )