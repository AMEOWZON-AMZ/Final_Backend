import httpx
import jwt
import json
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger

from app.core.config import settings
from app.schemas.user import SocialProvider, SocialUserInfo


class SocialAuthService:
    """소셜 로그인 서비스"""
    
    @staticmethod
    async def get_user_info(provider: SocialProvider, access_token: str) -> SocialUserInfo:
        """소셜 플랫폼에서 사용자 정보 가져오기"""
        
        if provider == SocialProvider.KAKAO:
            return await SocialAuthService._get_kakao_user_info(access_token)
        elif provider == SocialProvider.GOOGLE:
            return await SocialAuthService._get_google_user_info(access_token)
        elif provider == SocialProvider.NAVER:
            return await SocialAuthService._get_naver_user_info(access_token)
        elif provider == SocialProvider.APPLE:
            return await SocialAuthService._get_apple_user_info(access_token)
        else:
            raise ValueError(f"Unsupported social provider: {provider}")
    
    @staticmethod
    async def _get_kakao_user_info(access_token: str) -> SocialUserInfo:
        """카카오 사용자 정보 조회"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://kapi.kakao.com/v2/user/me",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                
                if response.status_code != 200:
                    logger.error(f"Kakao API error: {response.status_code} - {response.text}")
                    raise ValueError("Invalid Kakao access token")
                
                data = response.json()
                kakao_account = data.get("kakao_account", {})
                profile = kakao_account.get("profile", {})
                
                return SocialUserInfo(
                    social_id=str(data["id"]),
                    email=kakao_account.get("email", ""),
                    name=profile.get("nickname", ""),
                    nickname=profile.get("nickname", ""),
                    profile_image=profile.get("profile_image_url", ""),
                    provider=SocialProvider.KAKAO
                )
                
        except Exception as e:
            logger.error(f"Kakao user info fetch failed: {e}")
            raise ValueError("Failed to fetch Kakao user info")
    
    @staticmethod
    async def _get_google_user_info(access_token: str) -> SocialUserInfo:
        """구글 사용자 정보 조회"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://www.googleapis.com/oauth2/v2/userinfo",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                
                if response.status_code != 200:
                    logger.error(f"Google API error: {response.status_code} - {response.text}")
                    raise ValueError("Invalid Google access token")
                
                data = response.json()
                
                return SocialUserInfo(
                    social_id=data["id"],
                    email=data.get("email", ""),
                    name=data.get("name", ""),
                    nickname=data.get("name", ""),
                    profile_image=data.get("picture", ""),
                    provider=SocialProvider.GOOGLE
                )
                
        except Exception as e:
            logger.error(f"Google user info fetch failed: {e}")
            raise ValueError("Failed to fetch Google user info")
    
    @staticmethod
    async def _get_naver_user_info(access_token: str) -> SocialUserInfo:
        """네이버 사용자 정보 조회"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://openapi.naver.com/v1/nid/me",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                
                if response.status_code != 200:
                    logger.error(f"Naver API error: {response.status_code} - {response.text}")
                    raise ValueError("Invalid Naver access token")
                
                data = response.json()
                
                if data.get("resultcode") != "00":
                    raise ValueError("Invalid Naver access token")
                
                user_data = data.get("response", {})
                
                return SocialUserInfo(
                    social_id=user_data["id"],
                    email=user_data.get("email", ""),
                    name=user_data.get("name", ""),
                    nickname=user_data.get("nickname", ""),
                    profile_image=user_data.get("profile_image", ""),
                    provider=SocialProvider.NAVER
                )
                
        except Exception as e:
            logger.error(f"Naver user info fetch failed: {e}")
            raise ValueError("Failed to fetch Naver user info")
    
    @staticmethod
    async def _get_apple_user_info(identity_token: str) -> SocialUserInfo:
        """애플 사용자 정보 조회 (Identity Token 디코딩)"""
        try:
            # Apple Identity Token은 JWT 형태
            # 실제 환경에서는 Apple의 공개키로 검증해야 함
            # 여기서는 간단히 디코딩만 수행 (검증 없이)
            
            # JWT 디코딩 (검증 없이 - 개발용)
            decoded_token = jwt.decode(
                identity_token, 
                options={"verify_signature": False}
            )
            
            return SocialUserInfo(
                social_id=decoded_token["sub"],
                email=decoded_token.get("email", ""),
                name=decoded_token.get("name", ""),
                nickname=decoded_token.get("name", ""),
                profile_image="",  # Apple은 프로필 이미지 제공 안함
                provider=SocialProvider.APPLE
            )
            
        except Exception as e:
            logger.error(f"Apple user info fetch failed: {e}")
            raise ValueError("Failed to fetch Apple user info")
    
    @staticmethod
    def generate_oauth_url(provider: SocialProvider) -> str:
        """OAuth 인증 URL 생성 (웹용)"""
        
        if provider == SocialProvider.KAKAO:
            return (
                f"https://kauth.kakao.com/oauth/authorize"
                f"?client_id={settings.KAKAO_CLIENT_ID}"
                f"&redirect_uri={settings.KAKAO_REDIRECT_URI}"
                f"&response_type=code"
            )
        elif provider == SocialProvider.GOOGLE:
            return (
                f"https://accounts.google.com/oauth2/auth"
                f"?client_id={settings.GOOGLE_CLIENT_ID}"
                f"&redirect_uri={settings.GOOGLE_REDIRECT_URI}"
                f"&response_type=code"
                f"&scope=openid email profile"
            )
        elif provider == SocialProvider.NAVER:
            return (
                f"https://nid.naver.com/oauth2.0/authorize"
                f"?client_id={settings.NAVER_CLIENT_ID}"
                f"&redirect_uri={settings.NAVER_REDIRECT_URI}"
                f"&response_type=code"
            )
        else:
            raise ValueError(f"OAuth URL not supported for provider: {provider}")
    
    @staticmethod
    async def exchange_code_for_token(provider: SocialProvider, code: str) -> str:
        """Authorization Code를 Access Token으로 교환"""
        
        if provider == SocialProvider.KAKAO:
            return await SocialAuthService._exchange_kakao_code(code)
        elif provider == SocialProvider.GOOGLE:
            return await SocialAuthService._exchange_google_code(code)
        elif provider == SocialProvider.NAVER:
            return await SocialAuthService._exchange_naver_code(code)
        else:
            raise ValueError(f"Code exchange not supported for provider: {provider}")
    
    @staticmethod
    async def _exchange_kakao_code(code: str) -> str:
        """카카오 Authorization Code를 Access Token으로 교환"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://kauth.kakao.com/oauth/token",
                    data={
                        "grant_type": "authorization_code",
                        "client_id": settings.KAKAO_CLIENT_ID,
                        "client_secret": settings.KAKAO_CLIENT_SECRET,
                        "redirect_uri": settings.KAKAO_REDIRECT_URI,
                        "code": code
                    }
                )
                
                if response.status_code != 200:
                    raise ValueError("Failed to exchange Kakao code")
                
                data = response.json()
                return data["access_token"]
                
        except Exception as e:
            logger.error(f"Kakao code exchange failed: {e}")
            raise ValueError("Failed to exchange Kakao code")
    
    @staticmethod
    async def _exchange_google_code(code: str) -> str:
        """구글 Authorization Code를 Access Token으로 교환"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://oauth2.googleapis.com/token",
                    data={
                        "grant_type": "authorization_code",
                        "client_id": settings.GOOGLE_CLIENT_ID,
                        "client_secret": settings.GOOGLE_CLIENT_SECRET,
                        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                        "code": code
                    }
                )
                
                if response.status_code != 200:
                    raise ValueError("Failed to exchange Google code")
                
                data = response.json()
                return data["access_token"]
                
        except Exception as e:
            logger.error(f"Google code exchange failed: {e}")
            raise ValueError("Failed to exchange Google code")
    
    @staticmethod
    async def _exchange_naver_code(code: str) -> str:
        """네이버 Authorization Code를 Access Token으로 교환"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://nid.naver.com/oauth2.0/token",
                    data={
                        "grant_type": "authorization_code",
                        "client_id": settings.NAVER_CLIENT_ID,
                        "client_secret": settings.NAVER_CLIENT_SECRET,
                        "redirect_uri": settings.NAVER_REDIRECT_URI,
                        "code": code
                    }
                )
                
                if response.status_code != 200:
                    raise ValueError("Failed to exchange Naver code")
                
                data = response.json()
                return data["access_token"]
                
        except Exception as e:
            logger.error(f"Naver code exchange failed: {e}")
            raise ValueError("Failed to exchange Naver code")