"""
챌린지 스키마
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import date, datetime


class ChallengeDayBase(BaseModel):
    """챌린지 기본 스키마"""
    challenge_date: date
    title: str
    description: Optional[str] = None


class ChallengeDayCreate(ChallengeDayBase):
    """챌린지 생성 (관리자용)"""
    pass


class ChallengeDayResponse(ChallengeDayBase):
    """챌린지 응답"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime


class UserSubmissionInfo(BaseModel):
    """사용자 제출 정보"""
    submitted: bool
    image_url: Optional[str] = None
    submitted_at: Optional[datetime] = None


class ChallengeDayDetailResponse(BaseModel):
    """특정 날짜 챌린지 상세 응답"""
    id: int
    date: date
    title: str
    description: Optional[str] = None
    is_active: bool  # 오늘 날짜인지 여부 (서버에서 계산)
    user_submission: Optional[UserSubmissionInfo] = None


class SubmissionCreate(BaseModel):
    """챌린지 제출 생성"""
    user_id: str


class SubmissionResponse(BaseModel):
    """챌린지 제출 응답"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    challenge_day_id: int
    user_id: str
    image_url: str
    created_at: datetime


class UserChallengeHistory(BaseModel):
    """사용자 챌린지 참여 이력"""
    challenge_day_id: int
    date: date
    title: str
    image_url: str
    submitted_at: datetime


class UserChallengeHistoryResponse(BaseModel):
    """사용자 챌린지 이력 응답"""
    total: int
    submissions: List[UserChallengeHistory]


class FriendSubmissionInfo(BaseModel):
    """친구 제출 정보"""
    user_id: str
    nickname: str
    image_url: str
    submitted_at: datetime


class ChallengeFriendsImagesResponse(BaseModel):
    """특정 날짜 챌린지의 친구들 이미지 응답"""
    challenge: str  # 챌린지 제목
    date: date
    images: List[str]  # 이미지 URL 목록
    friends: List[FriendSubmissionInfo]  # 친구 상세 정보
