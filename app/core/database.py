from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool, QueuePool
from loguru import logger

from app.core.config import settings

# 환경변수 기준으로 DATABASE_URL 사용 (하드코딩 제거)
DATABASE_URL = settings.DATABASE_URL

# DB 타입에 따른 엔진 설정 분리
if "sqlite" in DATABASE_URL:
    # SQLite 설정
    engine = create_engine(
        DATABASE_URL,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=settings.DEBUG
    )
else:
    # PostgreSQL 설정
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=5,
        max_overflow=10,
        echo=settings.DEBUG
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Database dependency
def get_db():
    """데이터베이스 세션 의존성 - 에러 로깅 추가"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"DB session error: {e}")
        raise
    finally:
        db.close()


async def init_db():
    """데이터베이스 초기화"""
    try:
        # 테이블 생성
        Base.metadata.create_all(bind=engine)
        logger.info(f"Database initialized - URL: {DATABASE_URL}")
            
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise