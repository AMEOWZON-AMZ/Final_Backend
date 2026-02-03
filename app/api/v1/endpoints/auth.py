from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from loguru import logger

from app.core.database import get_db
from app.core.security import create_access_token, get_current_user
from app.core.config import settings
from app.schemas.user import (
    Token, SocialLoginRequest, DevTokenRequest, 
    SocialProvider, SocialUserInfo
)
from app.schemas.response import success_response, error_response
from app.services.user_service import UserService
from app.services.social_auth_service import SocialAuthService

router = APIRouter()


@router.post("/social")
async def social_login(
    login_data: SocialLoginRequest,
    db: Session = Depends(get_db)
):
    """소셜 로그인 (모바일 앱용)"""
    try:
        # 소셜 플랫폼에서 사용자 정보 가져오기
        social_user_info = await SocialAuthService.get_user_info(
            login_data.provider, 
            login_data.access_token
        )
        
        # 사용자 정보를 데이터베이스에 저장/업데이트
        user_service = UserService(db)
        user = await user_service.get_or_create_user_from_social(social_user_info)
        
        # JWT 토큰 생성
        token_data = {
            "user_id": str(user.id),
            "social_id": user.social_id,
            "email": user.email,
            "provider": user.social_provider.value
        }
        
        access_token = create_access_token(token_data)
        
        logger.info(f"User logged in via {login_data.provider.value}: {user.email}")
        
        return success_response(
            data={
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "nickname": user.nickname,
                    "profile_image_url": user.profile_image_url,
                    "provider": user.social_provider.value
                }
            },
            message="Login successful"
        )
        
    except Exception as e:
        logger.error(f"Social login failed: {e}")
        return error_response(
            message="Social login failed",
            error_code="SOCIAL_LOGIN_ERROR",
            details={"provider": login_data.provider.value, "error": str(e)}
        )


# OAuth 웹 플로우 (선택적)
@router.get("/oauth/{provider}")
async def oauth_login(provider: SocialProvider):
    """OAuth 로그인 시작 (웹용)"""
    try:
        auth_url = SocialAuthService.generate_oauth_url(provider)
        return RedirectResponse(url=auth_url)
    except Exception as e:
        logger.error(f"OAuth URL generation failed: {e}")
        return error_response(
            message="OAuth not supported",
            error_code="OAUTH_NOT_SUPPORTED",
            details={"provider": provider.value}
        )


@router.get("/oauth/{provider}/callback")
async def oauth_callback(
    provider: SocialProvider,
    code: str = Query(...),
    db: Session = Depends(get_db)
):
    """OAuth 콜백 처리 (웹용)"""
    try:
        # Authorization Code를 Access Token으로 교환
        access_token = await SocialAuthService.exchange_code_for_token(provider, code)
        
        # 사용자 정보 가져오기
        social_user_info = await SocialAuthService.get_user_info(provider, access_token)
        
        # 사용자 정보를 데이터베이스에 저장/업데이트
        user_service = UserService(db)
        user = await user_service.get_or_create_user_from_social(social_user_info)
        
        # JWT 토큰 생성
        token_data = {
            "user_id": str(user.id),
            "social_id": user.social_id,
            "email": user.email,
            "provider": user.social_provider.value
        }
        
        jwt_token = create_access_token(token_data)
        
        logger.info(f"OAuth login successful: {user.email} via {provider.value}")
        
        return success_response(
            data={
                "access_token": jwt_token,
                "token_type": "bearer",
                "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "nickname": user.nickname,
                    "profile_image_url": user.profile_image_url,
                    "provider": user.social_provider.value
                }
            },
            message="OAuth login successful"
        )
        
    except Exception as e:
        logger.error(f"OAuth callback failed: {e}")
        return error_response(
            message="OAuth callback failed",
            error_code="OAUTH_CALLBACK_ERROR",
            details={"provider": provider.value, "error": str(e)}
        )


@router.post("/dev-token")
async def create_development_token(
    token_request: DevTokenRequest,
    db: Session = Depends(get_db)
):
    """개발용 토큰 생성 (개발 환경에서만 사용)"""
    if settings.ENVIRONMENT != "development":
        return error_response(
            message="Development tokens only available in development environment",
            error_code="DEV_TOKEN_NOT_ALLOWED"
        )
    
    try:
        # 개발용 사용자 생성 또는 조회
        user_service = UserService(db)
        
        # 기존 사용자 조회
        existing_user = await user_service.get_user_by_social_id(
            token_request.provider, 
            token_request.user_id
        )
        
        if not existing_user:
            # 개발용 사용자 생성
            social_user_info = SocialUserInfo(
                social_id=token_request.user_id,
                email=token_request.email or f"{token_request.user_id}@example.com",
                name=f"Test User {token_request.user_id}",
                nickname=f"test_{token_request.user_id}",
                profile_image="",
                provider=token_request.provider
            )
            
            user = await user_service.get_or_create_user_from_social(social_user_info)
        else:
            user = existing_user
        
        # JWT 토큰 생성
        token_data = {
            "user_id": str(user.id),
            "social_id": user.social_id,
            "email": user.email,
            "provider": user.social_provider.value,
            "token_type": "development"
        }
        
        access_token = create_access_token(token_data)
        
        logger.info(f"Development token created for user: {token_request.user_id}")
        
        return success_response(
            data={
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "nickname": user.nickname,
                    "profile_image_url": user.profile_image_url,
                    "provider": user.social_provider.value
                }
            },
            message="Development token created successfully"
        )
        
    except Exception as e:
        logger.error(f"Development token creation failed: {e}")
        return error_response(
            message="Failed to create development token",
            error_code="DEV_TOKEN_ERROR",
            details={"error": str(e)}
        )


@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """현재 로그인한 사용자 정보 조회"""
    return success_response(
        data={
            "user_id": current_user.get("user_id"),
            "social_id": current_user.get("social_id"),
            "email": current_user.get("email"),
            "provider": current_user.get("provider"),
            "token_type": current_user.get("token_type", "social")
        },
        message="User info retrieved successfully"
    )


@router.post("/refresh")
async def refresh_token(current_user: dict = Depends(get_current_user)):
    """토큰 갱신"""
    try:
        # 새 토큰 생성
        new_token_data = {
            "user_id": current_user["user_id"],
            "social_id": current_user.get("social_id"),
            "email": current_user.get("email"),
            "provider": current_user.get("provider"),
            "token_type": current_user.get("token_type", "social")
        }
        
        new_token = create_access_token(new_token_data)
        
        return success_response(
            data={
                "access_token": new_token,
                "token_type": "bearer",
                "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            },
            message="Token refreshed successfully"
        )
        
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        return error_response(
            message="Failed to refresh token",
            error_code="TOKEN_REFRESH_ERROR",
            details={"error": str(e)}
        )


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """로그아웃 (토큰 무효화는 클라이언트에서 처리)"""
    logger.info(f"User logged out: {current_user.get('email')}")
    return success_response(
        message="Logged out successfully"
    )