# User Service

FastAPI 기반의 사용자 관리 및 친구 관계 관리 서비스입니다.

## 기능

- 사용자 CRUD (생성, 조회, 수정, 삭제)
- 친구 관계 관리 (추가, 수락, 거절, 삭제)
- 헬스체크 엔드포인트
- 자동 API 문서화

## 로컬 실행

### 1. 의존성 설치

```bash
cd services/user_service
pip install -e .
```

### 2. 서버 실행

```bash
python run_local.py
```

또는

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. API 문서 확인

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 엔드포인트

### 기본 엔드포인트
- `GET /` - 루트 엔드포인트
- `GET /health/` - 기본 헬스체크
- `GET /health/detailed` - 상세 헬스체크 (DB 연결 포함)
- `GET /health/ready` - Readiness 체크
- `GET /health/live` - Liveness 체크

### 사용자 관리
- `POST /api/v1/users/` - 사용자 생성
- `GET /api/v1/users/` - 사용자 목록 조회
- `GET /api/v1/users/{user_id}` - 특정 사용자 조회
- `PUT /api/v1/users/{user_id}` - 사용자 정보 수정
- `DELETE /api/v1/users/{user_id}` - 사용자 삭제

### 친구 관리
- `POST /api/v1/friends/?user_id={user_id}` - 친구 추가 요청
- `GET /api/v1/friends/?user_id={user_id}` - 친구 목록 조회
- `PUT /api/v1/friends/{friendship_id}` - 친구 관계 상태 업데이트
- `DELETE /api/v1/friends/{friendship_id}` - 친구 관계 삭제

## 테스트

### 테스트 실행

```bash
cd services/user_service
python tests/run_tests.py
```

또는

```bash
python -m pytest tests/ -v
```

### 테스트 커버리지

```bash
python -m pytest tests/ --cov=app --cov-report=html
```

## 예제 요청

### 사용자 생성
```bash
curl -X POST "http://localhost:8000/api/v1/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "full_name": "Test User",
    "password": "testpassword123"
  }'
```

### 친구 추가
```bash
curl -X POST "http://localhost:8000/api/v1/friends/?user_id=1" \
  -H "Content-Type: application/json" \
  -d '{
    "friend_id": 2
  }'
```

## 환경 변수

`.env` 파일에서 다음 환경 변수를 설정할 수 있습니다:

- `DEBUG`: 디버그 모드 (기본값: true)
- `HOST`: 서버 호스트 (기본값: 0.0.0.0)
- `PORT`: 서버 포트 (기본값: 8000)
- `DATABASE_URL`: 데이터베이스 URL (기본값: sqlite:///./test.db)
- `SECRET_KEY`: JWT 시크릿 키
- `LOG_LEVEL`: 로그 레벨 (기본값: INFO)

## 데이터베이스

기본적으로 SQLite를 사용하며, `test.db` 파일에 데이터가 저장됩니다.
PostgreSQL 등 다른 데이터베이스를 사용하려면 `DATABASE_URL`을 수정하세요.

## 프로젝트 구조

```
services/user_service/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── users.py
│   │   │   ├── friends.py
│   │   │   └── health.py
│   │   ├── v1/
│   │   │   └── api.py
│   │   └── health.py
│   ├── core/
│   │   ├── config.py
│   │   └── database.py
│   ├── models/
│   │   ├── user.py
│   │   └── friend.py
│   ├── schemas/
│   │   ├── user.py
│   │   ├── friend.py
│   │   └── response.py
│   ├── services/
│   │   ├── user_service.py
│   │   └── friend_service.py
│   └── main.py
├── tests/
│   ├── test_api.py
│   ├── test_users.py
│   ├── test_friends.py
│   ├── conftest.py
│   └── run_tests.py
├── .env
├── pyproject.toml
├── run_local.py
└── README.md
```