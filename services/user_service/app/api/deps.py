from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.auth import extract_user_info_from_token
from app.models.user import User
from app.schemas.user import TokenInfo

# OpenAPI에서 "Authorize" 버튼 표시를 위한 설정
security = HTTPBearer(
    scheme_name="Bearer Token",
    description="JWT Bearer 토큰을 입력하세요 (예: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...)"
)


async def get_current_user_info(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenInfo:
    """JWT 토큰에서 사용자 정보 추출"""
    try:
        token = credentials.credentials
        user_info = extract_user_info_from_token(token)
        return TokenInfo(**user_info)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    token_info: TokenInfo = Depends(get_current_user_info),
    db: Session = Depends(get_db)
) -> User:
    """
    현재 로그인한 사용자 정보 가져오기 (DB에서)
    
    개발/테스트 환경에서 더미 토큰 사용 시:
    - TEST_TOKEN_12345678 → user_id로 직접 조회
    """
    # 테스트 토큰인 경우 user_id로 직접 조회
    if hasattr(token_info, 'is_test_token') and getattr(token_info, 'is_test_token', False):
        test_user_id = getattr(token_info, 'test_user_id', None)
        if test_user_id:
            user = db.query(User).filter(User.user_id == test_user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Test user not found: {test_user_id}"
                )
            return user
    
    # 실제 JWT 토큰인 경우 sub로 조회 (user_id = sub)
    user = db.query(User).filter(User.user_id == token_info.sub).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found. Please sync your profile first."
        )
    
    return user


async def get_optional_current_user(
    db: Session = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[User]:
    """선택적 인증 (토큰이 없어도 됨)"""
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        user_info = extract_user_info_from_token(token)
        user = db.query(User).filter(User.user_id == user_info["sub"]).first()
        return user
    except:
        return None