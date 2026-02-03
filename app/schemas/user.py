from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class SocialProvider(str, Enum):
    KAKAO = "kakao"
    GOOGLE = "google"
    NAVER = "naver"
    APPLE = "apple"


class UserBase(BaseModel):
    email: EmailStr
    username: Optional[str] = None
    full_name: Optional[str] = None
    nickname: Optional[str] = None
    bio: Optional[str] = None
    phone_number: Optional[str] = None


class UserCreate(UserBase):
    social_provider: SocialProvider
    social_id: str = Field(..., description="Social platform unique ID")


class UserUpdate(BaseModel):
    username: Optional[str] = None
    full_name: Optional[str] = None
    nickname: Optional[str] = None
    bio: Optional[str] = None
    phone_number: Optional[str] = None
    profile_image_url: Optional[str] = None


class UserResponse(UserBase):
    id: int
    social_provider: SocialProvider
    social_id: str
    nickname: Optional[str] = None
    profile_image_url: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
    page: int
    limit: int
    has_next: bool


# Friend related schemas
class FriendBase(BaseModel):
    friend_id: str


class FriendCreate(FriendBase):
    pass


class FriendResponse(BaseModel):
    user_id: str
    friend_id: str
    friend_name: Optional[str] = None
    friend_email: Optional[str] = None
    friend_profile_image: Optional[str] = None
    created_at: datetime
    status: str = "active"


class FriendListResponse(BaseModel):
    friends: List[FriendResponse]
    total: int


# Social Login schemas
class SocialLoginRequest(BaseModel):
    provider: SocialProvider
    access_token: str = Field(..., description="Social platform access token")
    
    class Config:
        json_schema_extra = {
            "example": {
                "provider": "kakao",
                "access_token": "your_social_access_token"
            }
        }


class SocialUserInfo(BaseModel):
    social_id: str
    email: str
    name: Optional[str] = None
    nickname: Optional[str] = None
    profile_image: Optional[str] = None
    provider: SocialProvider


# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_info: UserResponse


class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None


# Development only
class DevTokenRequest(BaseModel):
    user_id: str
    email: Optional[EmailStr] = None
    provider: SocialProvider = SocialProvider.KAKAO
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "test-user-123",
                "email": "test@example.com",
                "provider": "kakao"
            }
        }