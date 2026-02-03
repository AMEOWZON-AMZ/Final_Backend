# 마이크로서비스 Pod 아키텍처

FastAPI 기반의 마이크로서비스 아키텍처로 구성된 소셜 미디어 백엔드입니다.
사용자 관리, AI 추론, 실시간 메시징 기능을 각각 독립적인 Pod로 분리하여 구현했습니다.

## 아키텍처 개요

### Pod 구조
- **User Pod** (포트 8001): 사용자 인증, 프로필 관리, 친구 시스템
- **Inference Pod** (포트 8002): AI/ML 모델 추론 서비스
- **Message Pod** (포트 8003): 실시간 메시징 및 채팅
- **Common Module**: 모든 Pod에서 공유하는 공통 기능

### 기술 스택
- **FastAPI**: 고성능 웹 프레임워크
- **SQLAlchemy**: ORM 및 데이터베이스 관리
- **PostgreSQL**: 메인 데이터베이스
- **Redis**: 캐싱 및 세션 관리
- **Docker**: 컨테이너화 및 배포
- **Nginx**: API 게이트웨이

## 프로젝트 구조

```
project/
├── common/                     # 공통 모듈
│   ├── config/                 # 설정 관리
│   ├── models/                 # 공통 모델
│   ├── schemas/                # 공통 스키마
│   ├── utils/                  # 유틸리티
│   └── middleware/             # 미들웨어
├── app/                        # User Pod (기존)
├── inference_pod/              # 추론 서비스
├── message_pod/                # 메시징 서비스
├── docker/                     # Docker 설정
├── scripts/                    # 배포 스크립트
└── docs/                       # 문서
```

## 설치 및 실행

### 1. 개발 환경 설정

```bash
# 저장소 클론
git clone <repository-url>
cd microservice-pods

# 가상환경 생성
python -m venv venv
venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
copy .env.example .env
# .env 파일을 편집하여 설정 값 입력
```

### 2. 개별 Pod 실행

```bash
# User Pod 실행 (포트 8001)
uvicorn app.main:app --port 8001 --reload

# Inference Pod 실행 (포트 8002)
uvicorn inference_pod.main:app --port 8002 --reload

# Message Pod 실행 (포트 8003)
uvicorn message_pod.main:app --port 8003 --reload
```

### 3. Docker Compose로 전체 실행

```bash
cd docker
docker-compose up --build
```

## API 문서

각 Pod의 API 문서는 다음 주소에서 확인할 수 있습니다:

- **User Pod**: http://localhost:8001/docs
- **Inference Pod**: http://localhost:8002/docs
- **Message Pod**: http://localhost:8003/docs

## 주요 기능

### User Pod
- 사용자 등록/로그인
- JWT 토큰 기반 인증
- 소셜 로그인 (Google, Facebook, 카카오, 네이버, 애플)
- 친구 시스템 (친구 요청, 수락, 삭제)
- 프로필 관리

### Inference Pod
- AI/ML 모델 추론
- 모델 버전 관리
- 추론 결과 캐싱
- 배치 추론 지원

### Message Pod
- 실시간 채팅
- 채팅방 관리
- 메시지 히스토리
- 푸시 알림

## 개발 가이드

### 새로운 기능 추가
1. 해당 Pod의 `models/`에 데이터 모델 추가
2. `schemas/`에 Pydantic 스키마 정의
3. `services/`에 비즈니스 로직 구현
4. `api/v1/endpoints/`에 API 엔드포인트 추가

### 공통 기능 추가
- `common/` 모듈에 모든 Pod에서 사용할 공통 기능 구현
- 설정, 유틸리티, 미들웨어 등

### 테스트 실행
```bash
pytest tests/
```

## 배포

### Docker를 이용한 배포
```bash
# 전체 서비스 빌드 및 실행
docker-compose -f docker/docker-compose.yml up -d

# 개별 서비스 스케일링
docker-compose -f docker/docker-compose.yml up -d --scale user-pod=3
```

### 환경별 설정
- `development`: 개발 환경
- `staging`: 스테이징 환경  
- `production`: 운영 환경

## 모니터링

각 Pod는 다음 헬스체크 엔드포인트를 제공합니다:
- `/health` - 기본 헬스체크
- `/health/ready` - 준비 상태 확인
- `/health/live` - 생존 상태 확인

## 소셜 로그인 설정

### 카카오 로그인
1. [Kakao Developers](https://developers.kakao.com/)에서 앱 생성
2. REST API 키와 보안 키를 `.env`에 설정
3. 리다이렉트 URI 설정: `http://localhost:8001/api/v1/auth/kakao/callback`

### 구글 로그인
1. [Google Cloud Console](https://console.cloud.google.com/)에서 OAuth 2.0 클라이언트 생성
2. 클라이언트 ID와 시크릿을 `.env`에 설정
3. 리다이렉트 URI 설정: `http://localhost:8001/api/v1/auth/google/callback`

### 네이버 로그인
1. [NAVER Developers](https://developers.naver.com/)에서 애플리케이션 등록
2. 클라이언트 ID와 시크릿을 `.env`에 설정
3. 콜백 URL 설정: `http://localhost:8001/api/v1/auth/naver/callback`

## 기여하기

1. 저장소 포크
2. 기능 브랜치 생성
3. 변경사항 구현
4. 테스트 추가
5. Pull Request 제출

## 라이선스

MIT License