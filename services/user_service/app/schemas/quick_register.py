"""
빠른 등록 스키마 (QR 코드용)
"""
from pydantic import BaseModel, Field
from typing import Optional


class QuickRegisterRequest(BaseModel):
    """빠른 등록 요청"""
    nickname: str = Field(..., min_length=1, max_length=50, description="닉네임")
    phone_number: Optional[str] = Field(None, pattern=r'^\d{3}-\d{4}-\d{4}$', description="전화번호 (010-1234-5678)")
    target_user_id: str = Field(..., description="친구로 등록할 대상 사용자 ID")
    
    # 고양이 프로필 (선택적)
    cat_pattern: Optional[str] = Field("solid", description="고양이 무늬")
    cat_color: Optional[str] = Field("#FF6B6B", description="고양이 색상")


class QuickRegisterResponse(BaseModel):
    """빠른 등록 응답"""
    success: bool
    message: str
    user_id: str
    nickname: str
    friend_code: str
    friend_added: bool
    target_nickname: str
    meow_audio_url: Optional[str] = None
    train_voice_urls: list[str] = []
