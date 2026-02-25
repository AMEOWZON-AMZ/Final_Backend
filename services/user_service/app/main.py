from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from starlette.types import Message
import time
import uuid
from loguru import logger

from app.core.config import settings
from app.core.database import init_db
from app.api.v1.api import api_router
from app.api.health import health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting User Pod Backend Service")
    
    try:
        await init_db()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
    
    # DynamoDB 서비스 초기화 (환경변수에 따라 자동으로 로컬/AWS 선택)
    try:
        from app.services.dynamodb_service import dynamodb_service
        import os
        use_local = os.getenv("USE_LOCAL_DYNAMODB", "false").lower() == "true"
        
        if use_local:
            logger.info("🔧 Using DynamoDB Local (port 8008)")
        else:
            logger.info("🔧 Using AWS DynamoDB (Pod Identity)")
        
        if dynamodb_service.dynamodb:
            logger.info("✅ DynamoDB connected successfully")
            try:
                # 테이블 존재 확인으로 연결 테스트
                if dynamodb_service.friends_table:
                    dynamodb_service.friends_table.load()
                    logger.info(f"📋 DynamoDB 테이블 연결 성공: {dynamodb_service.friends_table_name}")
                else:
                    if use_local:
                        logger.warning("⚠️  DynamoDB Local 연결 실패 - Docker Desktop이 실행 중인지 확인하세요")
                        logger.info("💡 친구 관계 기능은 사용할 수 없지만, 다른 기능은 정상 작동합니다")
                    else:
                        logger.warning("⚠️  DynamoDB 테이블이 초기화되지 않았습니다")
            except Exception as e:
                logger.warning(f"⚠️  DynamoDB 테이블 로드 실패: {e}")
                if use_local:
                    logger.info("💡 DynamoDB Local 시작 방법: docker run -d -p 8008:8000 amazon/dynamodb-local")
        else:
            logger.warning("⚠️  DynamoDB connection failed - service will continue without DynamoDB")
    except Exception as e:
        logger.error(f"❌ DynamoDB service initialization failed: {e}")
        logger.info("⚠️  Service will continue without DynamoDB")
    
    yield
    # Shutdown
    logger.info("Shutting down User Pod Backend Service")


app = FastAPI(
    title="User Pod Backend API",
    description="FastAPI backend service for User Pod in EKS environment",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    # OpenAPI에서 JWT 토큰 입력 가능하도록 설정
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": True,
    },
    # Bearer 토큰 인증 스키마 정의
    openapi_tags=[
        {"name": "users", "description": "사용자 관리"},
        {"name": "friends", "description": "친구 관리"},
        {"name": "health", "description": "헬스 체크"},
    ]
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Safe headers to log (exclude sensitive information)
SAFE_HEADERS = {
    "user-agent",
    "content-type",
    "content-length",
    "accept",
    "accept-encoding",
    "accept-language",
    "host",
    "connection"
}


# Request ID middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add unique request ID for tracking"""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    
    return response


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    request_id = getattr(request.state, "request_id", "unknown")
    
    # Filter safe headers only
    safe_headers = {
        k: v for k, v in request.headers.items()
        if k.lower() in SAFE_HEADERS
    }
    
    # Log request details
    logger.info(f"[{request_id}] ==== Incoming Request ====")
    logger.info(f"[{request_id}] URL: {request.url}")
    logger.info(f"[{request_id}] Method: {request.method}")
    logger.info(f"[{request_id}] Headers: {safe_headers}")
    
    # For POST/PUT/PATCH requests, log body safely
    body_log = ""
    if request.method in ["POST", "PUT", "PATCH"]:
        content_type = request.headers.get("content-type", "")
        
        # Skip body logging for multipart/form-data (file uploads)
        if content_type.startswith("multipart/form-data"):
            logger.info(f"[{request_id}] Body: [multipart/form-data - file upload, skipped]")
        else:
            try:
                # Read body
                body_bytes = await request.body()
                body_log = body_bytes.decode('utf-8') if body_bytes else ''
                
                # Log body only in DEBUG mode
                if settings.DEBUG:
                    logger.info(f"[{request_id}] Body: {body_log}")
                else:
                    logger.debug(f"[{request_id}] Body: {body_log}")
                
                # Restore body for downstream processing
                async def receive() -> Message:
                    return {"type": "http.request", "body": body_bytes}
                
                # Create new request with restored body
                request = Request(request.scope, receive)
            except Exception as e:
                logger.warning(f"[{request_id}] Could not read request body: {e}")
    else:
        logger.info(f"[{request_id}] Body: ")
    
    # Process request
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(f"[{request_id}] ==== Response ====")
    logger.info(f"[{request_id}] Status: {response.status_code}")
    
    # Log error response body for debugging
    if response.status_code >= 400:
        try:
            # Read response body for error logging
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk
            
            # Decode and log error response
            error_detail = response_body.decode('utf-8')
            logger.error(f"[{request_id}] Error Response Body: {error_detail}")
            
            # Recreate response with body
            from fastapi.responses import Response
            response = Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
        except Exception as e:
            logger.warning(f"[{request_id}] Could not read error response body: {e}")
    
    logger.info(f"[{request_id}] Process Time: {process_time:.4f}s")
    logger.info(f"[{request_id}] " + "=" * 50)
    
    return response


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(f"[{request_id}] Global exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An error occurred",
            "request_id": request_id
        }
    )


# Include routers
app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(api_router, prefix="/api/v1")

# Quick register router (QR code)
from app.api.routes.quick_register import router as quick_register_router
app.include_router(quick_register_router, prefix="/api/v1/quick", tags=["quick-register"])


@app.get("/")
async def root():
    return {
        "message": "User Pod Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )