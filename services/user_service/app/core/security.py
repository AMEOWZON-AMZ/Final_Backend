from passlib.context import CryptContext
import secrets
import string
import hashlib
from datetime import datetime, timedelta
from jose import jwt
from typing import Dict, Any, Optional
from app.core.config import settings

# 비밀번호 해시 컨텍스트 - bcrypt 대신 pbkdf2_sha256 사용
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    """비밀번호 해시 처리"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호 검증"""
    return pwd_context.verify(plain_password, hashed_password)


def generate_sub() -> str:
    """로컬 사용자용 Google/Cognito sub 생성"""
    return f"local_{secrets.token_urlsafe(16)}"


def validate_password_strength(password: str) -> bool:
    """비밀번호 강도 검증"""
    if len(password) < 8 or len(password) > 50:  # 길이 제한 추가
        return False
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    
    return has_upper and has_lower and has_digit


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    JWT 액세스 토큰 생성 (테스트용)
    
    Args:
        data: 토큰에 포함할 데이터 (sub, email 등)
        expires_delta: 토큰 만료 시간 (기본: 30분)
    
    Returns:
        JWT 토큰 문자열
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "token_use": "access",
        "client_id": settings.COGNITO_CLIENT_ID
    })
    
    # JWT 토큰 생성
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt