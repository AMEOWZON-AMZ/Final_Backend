# 마이크로서비스 백엔드 아키텍처

FastAPI 기반의 마이크로서비스 아키텍처로 구성된 백엔드 서비스입니다.

## 서비스 구조

### 🏗️ 마이크로서비스
- **User Service** (포트 8001): 사용자 관리, 인증, 친구 시스템
- **Message Service** (포트 8002): 실시간 메시징 및 알림
- **Inference Service** (포트 8003): AI/ML 모델 추론

### 📁 프로젝트 구조
```
backend/
├── services/
│   ├── user_service/          # 사용자 관리 서비스
│   ├── message_service/       # 메시징 서비스
│   └── inference_service/     # 추론 서비스
├── libs/common/               # 공통 라이브러리
├── deploy/k8s/               # Kubernetes 배포 설정
├── scripts/                  # 개발/배포 스크립트
└── docs/                     # 문서
```

## 기술 스택
- **Backend**: FastAPI + Python 3.11
- **Database**: PostgreSQL / SQLite
- **Authentication**: JWT + 소셜 로그인
- **Container**: Docker + Kubernetes
- **Monitoring**: Prometheus + Grafana

## 로컬 개발 환경

### 1. 전체 서비스 실행
```bash
# 모든 서비스 시작
make run-all

# 개별 서비스 실행
make run-user-service
make run-message-service
make run-inference-service
```

### 2. Docker Compose 실행
```bash
docker-compose up -d
```

## API 문서
- **User Service**: http://localhost:8001/docs
- **Message Service**: http://localhost:8002/docs
- **Inference Service**: http://localhost:8003/docs

## 소셜 로그인 지원
- 🟡 **카카오 로그인**
- 🔴 **구글 로그인**
- 🟢 **네이버 로그인**
- 🍎 **애플 로그인** (iOS)

## 개발 가이드

### 새로운 서비스 추가
1. `backend/services/` 에 새 서비스 디렉토리 생성
2. 표준 구조 따라 구현 (app/, tests/, Dockerfile 등)
3. K8s 배포 설정 추가

### 공통 기능 추가
- `backend/libs/common/` 에 공통 라이브러리 구현
- 인증, 로깅, 설정 등 공유 기능

## 배포

### Kubernetes 배포
```bash
# 네임스페이스 생성
kubectl apply -f deploy/k8s/namespaces/

# 서비스 배포
kubectl apply -f deploy/k8s/user_service/
kubectl apply -f deploy/k8s/message_service/
kubectl apply -f deploy/k8s/inference_service/
```

### 환경별 설정
- `development`: 로컬 개발
- `staging`: 스테이징 환경
- `production`: 운영 환경

## 모니터링
- **헬스체크**: `/health` 엔드포인트
- **메트릭**: Prometheus 수집
- **로그**: 구조화된 JSON 로그

## 테스트
```bash
# 전체 테스트
make test-all

# 개별 서비스 테스트
make test-user-service
make test-message-service
make test-inference-service
```