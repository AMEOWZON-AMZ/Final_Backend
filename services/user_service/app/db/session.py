from sqlalchemy.orm import Session
from app.core.database import SessionLocal


def get_db_session() -> Session:
    """데이터베이스 세션 생성"""
    return SessionLocal()