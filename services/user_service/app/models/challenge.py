"""
챌린지 모델
매일 고양이 사진 챌린지 시스템
"""
from sqlalchemy import Column, String, DateTime, Date, Text, ForeignKey, UniqueConstraint, BigInteger, Index, Numeric, Boolean
from sqlalchemy.sql import func
from app.core.database import Base


class ChallengeDay(Base):
    """일일 챌린지 정의"""
    __tablename__ = "challenge_days"

    # Primary Key
    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # 챌린지 정보
    challenge_date = Column(Date, unique=True, nullable=False, index=True)  # 챌린지 날짜 (UNIQUE)
    title = Column(String(255), nullable=False)  # 챌린지 제목 (한글)
    title_en = Column(String(255), nullable=True)  # 챌린지 제목 (영문)
    description = Column(Text, nullable=True)  # 챌린지 설명

    # 타임스탬프
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)



class ChallengeSubmission(Base):
    """사용자 챌린지 제출"""
    __tablename__ = "challenge_submissions"
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # Foreign Keys
    user_id = Column(String(255), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    challenge_day_id = Column(BigInteger, ForeignKey("challenge_days.id", ondelete="CASCADE"), nullable=False)
    
    # 제출 정보
    image_url = Column(Text, nullable=False)  # S3 이미지 URL
    
    # GPS 좌표
    latitude = Column(Numeric(10, 8), nullable=True)  # 위도 (-90 ~ 90)
    longitude = Column(Numeric(11, 8), nullable=True)  # 경도 (-180 ~ 180)
    altitude = Column(Numeric(8, 2), nullable=True)  # 고도 (미터)
    has_gps = Column(Boolean, default=False, nullable=False)  # GPS 정보 유무
    
    # 타임스탬프
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # 제약조건 및 인덱스
    __table_args__ = (
        UniqueConstraint('user_id', 'challenge_day_id', name='ux_user_challenge'),
        Index('idx_submission_day_user', 'challenge_day_id', 'user_id'),
        Index('idx_submission_user', 'user_id'),
        Index('idx_submissions_gps', 'latitude', 'longitude'),
        Index('idx_submissions_date_gps', 'challenge_day_id', 'has_gps'),
    )
