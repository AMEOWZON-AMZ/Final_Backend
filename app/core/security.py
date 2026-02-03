from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from loguru import logger

from app.core.config import settings

# JWT token scheme
security = HTTPBearer()


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """JWT 액세스 토큰 생성"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # datetime을 timestamp로 변환
    to_encode.update({"exp": int(expire.timestamp())})
    # 간단한 토큰 생성 (실제로는 JWT 라이브러리 사용)
    import json
    import base64
    token_str = json.dumps(to_encode)
    encoded_jwt = base64.b64encode(token_str.encode()).decode()
    return encoded_jwt


def verify_token(token: str) -> Dict[str, Any]:
    """JWT 토큰 검증"""
    try:
        import json
        import base64
        decoded_str = base64.b64decode(token.encode()).decode()
        payload = json.loads(decoded_str)
        
        # 만료 시간 확인
        if "exp" in payload:
            exp_time = datetime.fromtimestamp(payload["exp"])
            if datetime.utcnow() > exp_time:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        
        return payload
    except Exception as e:
        logger.error(f"JWT verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """현재 사용자 정보 가져오기"""
    token = credentials.credentials
    
    # JWT 토큰 검증
    try:
        payload = verify_token(token)
        return payload
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """활성 사용자 확인"""
    # 여기서 사용자 상태 확인 로직 추가 가능
    return current_user


# 개발용 토큰 생성 함수
def create_dev_token(user_id: str, email: str = None, provider: str = "kakao") -> str:
    """개발용 JWT 토큰 생성"""
    if settings.ENVIRONMENT != "development":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Development tokens only available in development environment"
        )
    
    token_data = {
        "user_id": user_id,
        "social_id": user_id,
        "email": email,
        "provider": provider,
        "token_type": "development"
    }
    
    return create_access_token(token_data)