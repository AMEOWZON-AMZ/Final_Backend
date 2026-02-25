from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import List, Optional
import os


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", case_sensitive=True, extra='allow')
    
    # App settings
    APP_NAME: str = "User Pod Backend API"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    
    # Database settings
    DATABASE_URL: str = "sqlite:///./test.db"  # 로컬 개발용
    
    # AWS RDS settings (실제 운영용)
    RDS_HOST: str = os.getenv("RDS_HOST", "localhost")
    RDS_PORT: int = int(os.getenv("RDS_PORT", "5432"))
    RDS_DATABASE: str = os.getenv("RDS_DATABASE", "user_service_db")
    RDS_USERNAME: str = os.getenv("RDS_USERNAME", "postgres")
    RDS_PASSWORD: str = os.getenv("RDS_PASSWORD", "password")
    
    # RDS 연결 URL 생성 (SSL 설정 포함)
    @property
    def RDS_DATABASE_URL(self) -> str:
        return f"postgresql://{self.RDS_USERNAME}:{self.RDS_PASSWORD}@{self.RDS_HOST}:{self.RDS_PORT}/{self.RDS_DATABASE}?sslmode=require"
    
    # 환경에 따른 DB URL 선택
    @property
    def ACTIVE_DATABASE_URL(self) -> str:
        use_rds = os.getenv("USE_RDS", "false").lower() == "true"
        return self.RDS_DATABASE_URL if use_rds else self.DATABASE_URL
    
    # Security settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # AWS Cognito settings
    COGNITO_REGION: str = "ap-northeast-2"
    COGNITO_USER_POOL_ID: str = "ap-northeast-2_2tlc2TiI2"
    COGNITO_CLIENT_ID: str = "1ki1nh4k93ctoqhm1hmu7ekhj5"
    COGNITO_ISSUER: str = "https://cognito-idp.ap-northeast-2.amazonaws.com/ap-northeast-2_2tlc2TiI2"
    
    # AWS S3 settings
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_REGION: str = os.getenv("AWS_REGION", "ap-northeast-2")
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", "")
    S3_BASE_URL: str = os.getenv("S3_BASE_URL", "")
    
    # DynamoDB settings
    DYNAMODB_ENDPOINT_URL: str = "http://localhost:8008"  # DynamoDB Local
    DYNAMODB_REGION: str = "ap-northeast-2"
    DYNAMODB_ACCESS_KEY_ID: str = "dummy"  # DynamoDB Local용 더미 키
    DYNAMODB_SECRET_ACCESS_KEY: str = "dummy"  # DynamoDB Local용 더미 키
    
    # File upload settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/webp"]
    ALLOWED_AUDIO_TYPES: List[str] = ["audio/mpeg", "audio/wav", "audio/mp4", "audio/x-m4a", "audio/m4a"]
    
    # Gemini API (챌린지 자동 생성용)
    GEMINI_API_KEY: Optional[str] = None
    
    # Hugging Face API (이미지 생성용)
    HUGGINGFACE_TOKEN: Optional[str] = None
    
    # Replicate API (이미지 생성용 - 확실하게 작동!)
    REPLICATE_TOKEN: Optional[str] = None
    
    # Nanobanana API (AI 이미지 생성용)
    NANOBANANA_API_URL: Optional[str] = None
    NANOBANANA_API_KEY: Optional[str] = None
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = ["*"]


settings = Settings()