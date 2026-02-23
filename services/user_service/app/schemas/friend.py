from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class FriendBase(BaseModel):
    friend_id: str


class FriendCreate(FriendBase):
    pass


class FriendUpdate(BaseModel):
    status: Optional[str] = None


class UserInFriend(BaseModel):
    """친구 관계에서 사용되는 간단한 사용자 정보"""
    model_config = ConfigDict(from_attributes=True)
    
    user_id: str  # Google/Cognito sub
    email: str
    nickname: str
    provider: str
    profile_image_url: Optional[str] = None


class FriendResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: str
    friend_id: str
    status: str
    created_at: datetime
    friend: Optional[UserInFriend] = None
    user: Optional[UserInFriend] = None