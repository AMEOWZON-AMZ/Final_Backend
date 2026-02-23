from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from typing import Generator
from loguru import logger

from app.core.config import settings

# 환경에 따른 DB URL 선택
DATABASE_URL = settings.ACTIVE_DATABASE_URL

# SQLAlchemy 엔진 생성
if "sqlite" in DATABASE_URL:
    # SQLite는 connect_timeout을 지원하지 않음
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True,
    )
else:
    # PostgreSQL 등 다른 DB는 connect_timeout 지원
    engine = create_engine(
        DATABASE_URL,
        connect_args={"connect_timeout": 5},
        pool_pre_ping=True,
        pool_recycle=3600,
    )

# 세션 팩토리 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 클래스 생성
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """데이터베이스 세션 의존성"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def init_db():
    """데이터베이스 초기화 - 타임아웃 적용"""
    try:
        # 연결 테스트
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        # 테이블 생성
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database connected & tables created")
        
    except Exception as e:
        logger.warning(f"⚠️ Database init failed (continuing): {e}")