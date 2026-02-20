from sqlalchemy import Column, String, DateTime, Boolean, BigInteger, Integer, Enum as SQLEnum
from sqlalchemy.sql import func
from app.core.database import Base
import uuid
import time
import random
import string
import enum


class CatPattern(str, enum.Enum):
    """고양이 패턴 (3가지만 허용)"""
    SOLID = "solid"
    DOTTED = "dotted"
    STRIPE = "stripe"


def get_timestamp():
    """현재 타임스탬프를 밀리초로 반환"""
    return int(time.time() * 1000)


def generate_friend_code():
    """친구 추가용 코드 생성 (6자리 영숫자)"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


class User(Base):
    __tablename__ = "users"
    
    # Primary Key (Cognito Sub 사용)
    user_id = Column(String(255), primary_key=True, index=True, nullable=False)  # Cognito Sub를 user_id로 사용
    
    # 인증 관련
    email = Column(String(100), unique=True, index=True, nullable=False)  # 이메일
    
    # 사용자 정보
    nickname = Column(String(50), nullable=False)  # 닉네임
    phone_number = Column(String(20), nullable=True)  # 전화번호
    profile_image_url = Column(String(500), nullable=True)  # 프로필 이미지
    
    # 친구 추가용 코드
    friend_code = Column(String(6), unique=True, index=True, nullable=False, default=generate_friend_code)
    
    # 타임스탬프
    created_at_timestamp = Column(BigInteger, nullable=False, default=get_timestamp)
    updated_at_timestamp = Column(BigInteger, nullable=False, default=get_timestamp, onupdate=get_timestamp)
    
    # 고양이 프로필
    cat_pattern = Column(String(50), nullable=True)  # 문자열로 변경 (DB에 소문자 데이터 존재)
    cat_color = Column(String(7), nullable=True)
    duress_code = Column(String(100), nullable=True)
    meow_audio_url = Column(String(500), nullable=True)
    duress_audio_url = Column(String(500), nullable=True)
    
    # FCM 푸시 알림
    token = Column(String(500), nullable=True)  # Firebase Cloud Messaging 토큰
    
    # 기타
    provider = Column(String(50), default="cognito", nullable=False)
    profile_setup_completed = Column(Boolean, default=False)
