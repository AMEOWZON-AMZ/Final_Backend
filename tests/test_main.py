import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import get_db, Base
from app.models.user import User  # User 모델 import 추가

# 테스트용 인메모리 SQLite 데이터베이스
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    # 테스트 시작 전에 테이블 생성
    Base.metadata.create_all(bind=engine)
    yield
    # 테스트 완료 후 테이블 삭제
    Base.metadata.drop_all(bind=engine)


def test_root():
    """루트 엔드포인트 테스트"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "User Pod Backend API"
    assert "version" in data


def test_health_check():
    """헬스체크 엔드포인트 테스트"""
    response = client.get("/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["message"] == "Service is healthy"
    assert "data" in data
    assert data["data"]["service"] == "user-pod-backend"


def test_health_ready():
    """Readiness probe 테스트"""
    response = client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["message"] == "Service is ready to accept requests"
    assert data["data"]["status"] == "ready"


def test_health_live():
    """Liveness probe 테스트"""
    response = client.get("/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["message"] == "Service is alive"
    assert data["data"]["status"] == "alive"


def test_create_dev_token():
    """개발용 토큰 생성 테스트"""
    token_data = {
        "user_id": "test-user-123",
        "email": "test@example.com",
        "provider": "kakao"  # 소문자로 다시 변경
    }
    response = client.post("/api/v1/auth/dev-token", json=token_data)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["message"] == "Development token created successfully"
    assert "data" in data
    assert "access_token" in data["data"]
    assert data["data"]["token_type"] == "bearer"
    assert "user" in data["data"]


def test_unauthorized_access():
    """인증 없이 보호된 엔드포인트 접근 테스트"""
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401


def test_docs_endpoint():
    """API 문서 엔드포인트 테스트"""
    response = client.get("/docs")
    assert response.status_code == 200


def test_redoc_endpoint():
    """ReDoc 엔드포인트 테스트"""
    response = client.get("/redoc")
    assert response.status_code == 200