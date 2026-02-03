"""
공통 기본 설정 모듈
모든 Pod에서 공유하는 기본 설정들
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class BaseConfig(BaseSettings):
    """모든 Pod에서 공유하는 기본 설정"""
    
    # 환경 설정
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # 로깅 설정
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 보안 설정
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS 설정
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000"]
    ALLOWED_METHODS: list = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    ALLOWED_HEADERS: list = ["*"]
    
    # 서비스 간 통신 설정
    USER_POD_URL: str = "http://localhost:8001"
    INFERENCE_POD_URL: str = "http://localhost:8002"
    MESSAGE_POD_URL: str = "http://localhost:8003"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


class DatabaseConfig(BaseSettings):
    """데이터베이스 공통 설정"""
    
    DATABASE_URL: Optional[str] = None
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "password"
    DB_NAME: str = "microservice_db"
    
    # SQLite 설정 (개발용)
    SQLITE_URL: str = "sqlite:///./app.db"
    
    # 연결 풀 설정
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    
    @property
    def database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 전역 설정 인스턴스
base_config = BaseConfig()
db_config = DatabaseConfig()