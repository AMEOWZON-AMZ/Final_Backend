from jose import jwt
import requests
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from functools import lru_cache
import json
from app.core.config import settings


class CognitoJWTValidator:
    def __init__(self):
        self.region = settings.COGNITO_REGION
        self.user_pool_id = settings.COGNITO_USER_POOL_ID
        self.client_id = settings.COGNITO_CLIENT_ID
        self.issuer = settings.COGNITO_ISSUER
        self._jwks = None
    
    @lru_cache(maxsize=1)
    def get_jwks(self) -> Dict[str, Any]:
        """Cognito JWKS 키 가져오기 (캐시됨)"""
        if self._jwks is None:
            jwks_url = f"{self.issuer}/.well-known/jwks.json"
            try:
                response = requests.get(jwks_url, timeout=10)
                response.raise_for_status()
                self._jwks = response.json()
            except Exception as e:
                # 개발 환경에서는 JWKS 검증을 건너뛰고 토큰 내용만 디코딩
                if settings.DEBUG:
                    print(f"Warning: JWKS fetch failed, using debug mode: {e}")
                    return {}
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to fetch JWKS keys"
                )
        return self._jwks
    
    def get_public_key(self, token_header: Dict[str, Any]) -> Optional[str]:
        """토큰 헤더에서 공개 키 추출"""
        kid = token_header.get('kid')
        if not kid:
            return None
        
        jwks = self.get_jwks()
        if not jwks:  # Debug mode
            return None
            
        for key in jwks.get('keys', []):
            if key.get('kid') == kid:
                return jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
        return None
    
    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """JWT 토큰 검증"""
        try:
            # 토큰 헤더 디코딩 (검증 없이)
            header = jwt.get_unverified_header(token)
            
            if settings.DEBUG:
                # 개발 환경에서는 검증 없이 페이로드만 디코딩
                payload = jwt.decode(token, options={"verify_signature": False})
                print(f"Debug: Token payload: {payload}")
                return payload
            
            # 프로덕션 환경에서는 완전한 검증
            public_key = self.get_public_key(header)
            if not public_key:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Unable to find appropriate key"
                )
            
            # JWT 토큰 검증
            payload = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                audience=self.client_id,
                issuer=self.issuer
            )
            
            # 토큰 타입 검증
            if token_type == "access" and payload.get("token_use") != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            elif token_type == "id" and payload.get("token_use") != "id":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token validation failed: {str(e)}"
            )


# 전역 JWT 검증기 인스턴스
jwt_validator = CognitoJWTValidator()


def extract_user_info_from_token(token: str) -> Dict[str, Any]:
    """
    토큰에서 사용자 정보 추출
    
    개발/테스트 환경에서는 더미 토큰 허용:
    - TEST_TOKEN_google-sub-user1 → sub: google-sub-user1
    - TEST_TOKEN_google-sub-user2 → sub: google-sub-user2
    """
    # 개발/테스트 환경에서 더미 토큰 허용
    if settings.DEBUG and token.startswith("TEST_TOKEN_"):
        user_id = token.replace("TEST_TOKEN_", "")
        
        # user_id 유효성 검증 (비어있지 않은지만 확인)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid test token format. Use: TEST_TOKEN_<user_id>"
            )
        
        # 더미 사용자 정보 반환
        # sub 값만 저장, email/nickname은 DB에서 관리
        return {
            "sub": user_id,  # Cognito sub 값 (저장만 함)
            "email": None,  # DB에서 관리
            "groups": [],
            "token_use": "access",
            "client_id": "test-client",
            "is_test_token": True
        }
    
    # 실제 JWT 토큰 검증
    payload = jwt_validator.verify_token(token, "access")
    
    return {
        "sub": payload.get("sub"),
        "email": payload.get("email"),
        "groups": payload.get("cognito:groups", payload.get("groups", [])),
        "token_use": payload.get("token_use"),
        "client_id": payload.get("client_id") or payload.get("aud"),
        "is_test_token": False
    }