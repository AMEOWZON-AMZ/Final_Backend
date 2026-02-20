from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    nickname: Optional[str] = None


class UserCreate(UserBase):
    provider: Optional[str] = "cognito"
    profile_image_url: Optional[str] = None
    # 프론트엔드 호환 필드들
    cat_pattern: Optional[str] = None
    cat_color: Optional[str] = None
    duress_code: Optional[str] = None
    meow_audio_url: Optional[str] = None


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    nickname: Optional[str] = None
    full_name: Optional[str] = None  # full_name을 nickname으로 매핑
    phone_number: Optional[str] = None  # 전화번호
    profile_image_url: Optional[str] = None
    # 프론트엔드 호환 필드들
    cat_pattern: Optional[str] = None
    cat_color: Optional[str] = None
    duress_code: Optional[str] = None
    meow_audio_url: Optional[str] = None
    
    def model_dump(self, **kwargs):
        """full_name을 nickname으로 변환"""
        data = super().model_dump(**kwargs)
        # full_name이 있으면 nickname으로 복사
        if 'full_name' in data and data['full_name'] is not None:
            data['nickname'] = data['full_name']
        # full_name 필드 제거 (DB에 없는 필드)
        data.pop('full_name', None)
        return data


class UserSignup(BaseModel):
    """회원가입 요청 (AWS RDS 대응 - Cognito 전용, password 불필요)"""
    user_id: str  # Google/Cognito sub 값 (필수)
    email: EmailStr
    nickname: str
    phone_number: Optional[str] = None  # 전화번호 (선택)
    
    # 고양이 프로필 정보 (필수)
    cat_pattern: str
    cat_color: str
    
    # 음성 파일 정보 (선택)
    meow_audio_url: Optional[str] = None  # 야옹 소리
    duress_code: Optional[str] = None  # 위험 신호 코드
    duress_audio_url: Optional[str] = None  # 위험 신호 소리
    
    # 프로필 이미지 (선택)
    profile_image_url: Optional[str] = None
    
    # FCM 토큰 (선택)
    token: Optional[str] = None  # Firebase Cloud Messaging 토큰
    
    @classmethod
    def model_validate(cls, obj):
        """빈 문자열을 None으로 변환"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                if value == '':
                    obj[key] = None
        return super().model_validate(obj)
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "google-oauth2|123456789",
                "email": "user@example.com",
                "nickname": "고양이집사",
                "phone_number": "010-1234-5678",
                "cat_pattern": "solid",
                "cat_color": "#FF6B6B",
                "meow_audio_url": "https://s3.amazonaws.com/bucket/meow.mp3",
                "duress_code": "HELP123",
                "duress_audio_url": "https://s3.amazonaws.com/bucket/duress.mp3",
                "profile_image_url": "https://s3.amazonaws.com/bucket/profile.jpg",
                "token": "fcm_token_from_firebase..."
            }
        }


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    user_id: str  # Google/Cognito sub 값
    provider: str
    profile_image_url: Optional[str] = None
    phone_number: Optional[str] = None  # 전화번호
    friend_code: str  # 친구 추가용 코드
    # 프론트엔드 호환 필드들
    nickname: Optional[str] = None
    cat_pattern: Optional[str] = None
    cat_color: Optional[str] = None
    duress_code: Optional[str] = None
    meow_audio_url: Optional[str] = None
    duress_audio_url: Optional[str] = None
    # 프론트엔드 타임스탬프
    created_at_timestamp: Optional[int] = None
    updated_at_timestamp: Optional[int] = None
    # 백엔드 전용
    profile_setup_completed: bool = False


class UserProfile(BaseModel):
    """현재 로그인한 사용자 프로필"""
    user_id: str  # Google/Cognito sub 값
    email: str
    nickname: Optional[str] = None
    phone_number: Optional[str] = None  # 전화번호
    provider: str
    profile_image_url: Optional[str] = None
    friend_code: str  # 친구 추가용 코드
    # 프론트엔드 호환 필드들
    cat_pattern: Optional[str] = None
    cat_color: Optional[str] = None
    duress_code: Optional[str] = None
    meow_audio_url: Optional[str] = None
    created_at_timestamp: Optional[int] = None
    updated_at_timestamp: Optional[int] = None


class TokenInfo(BaseModel):
    """토큰에서 추출한 사용자 정보"""
    sub: str  # Google/Cognito sub
    email: Optional[str] = None
    groups: list = []
    token_use: str
    client_id: str


# 고양이 프로필 관련 스키마
class CatProfile(BaseModel):
    """고양이 프로필 정보"""
    pattern: Optional[str] = None
    color: Optional[str] = None
    image_url: Optional[str] = None


class LobbyFriend(BaseModel):
    """로비에서 표시할 친구 정보 (DynamoDB에서 조회)"""
    user_id: str  # 친구의 user_id
    email: str  # 친구의 이메일
    nickname: str  # 친구의 닉네임
    profile_image_url: Optional[str] = None  # 친구의 프로필 이미지
    cat_pattern: Optional[str] = None  # 고양이 패턴
    cat_color: Optional[str] = None  # 고양이 색상
    meow_audio_url: Optional[str] = None  # 야옹 소리 URL
    duress_code: Optional[str] = None  # 위험 신호 코드
    duress_audio_url: Optional[str] = None  # 위험 신호 소리 URL
    daily_status: Optional[str] = None  # 일일 상태 (AI 추론)
    created_at_timestamp: Optional[int] = None  # 생성 시간
    updated_at_timestamp: Optional[int] = None  # 수정 시간


class LoginResponse(BaseModel):
    """로그인 응답 (본인 프로필 + 친구 목록)"""
    user: UserProfile
    friends: List[LobbyFriend]
    total_friends: int


class ProfileSetupData(BaseModel):
    """프로필 설정 데이터"""
    nickname: str
    cat_pattern: Optional[str] = None
    cat_color: Optional[str] = None


class FriendRequestData(BaseModel):
    """친구 요청 데이터"""
    user_id: str
    friend_code: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "google-sub-12345",
                "friend_code": "ABC123"
            }
        }


class FriendActionData(BaseModel):
    """친구 요청 수락/거절/취소 데이터"""
    user_id: str
    friend_user_id: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "google-sub-12345",
                "friend_user_id": "google-sub-67890"
            }
        }


# 프론트엔드 전용 스키마
class FrontendUser(BaseModel):
    """프론트엔드 User 데이터 클래스와 완전 호환"""
    user_id: str  # Google/Cognito sub 값
    email: str
    nickname: str
    profile_image_url: Optional[str] = None  # profileImageUrl
    friend_code: str  # 친구 추가용 코드
    created_at_timestamp: int  # createdAt
    updated_at_timestamp: int  # updatedAt
    cat_pattern: Optional[str] = None  # catPattern
    cat_color: Optional[str] = None  # catColor
    duress_code: Optional[str] = None  # duressCode
    meow_audio_url: Optional[str] = None  # meowAudioUrl


# 친구 관련 스키마
class FriendRequest(BaseModel):
    """친구 요청용 스키마"""
    friend_code: str


class FriendResponse(BaseModel):
    """친구 응답용 스키마"""
    user_id: str  # Google/Cognito sub 값
    nickname: str
    friend_code: str
    cat_profile: CatProfile
    status: str  # accepted


class LoginRequest(BaseModel):
    """로그인 요청"""
    user_id: str  # 사용자 ID (필수)
    token: Optional[str] = None  # FCM 토큰 (선택)
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "12345678",
                "token": "fcm_token_from_firebase..."
            }
        }
