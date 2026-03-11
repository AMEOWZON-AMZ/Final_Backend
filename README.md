# Final_Backend

AMEOWZON 백엔드 저장소입니다. 현재 코드 기준으로 **실제 구현이 집중된 서비스는 `user_service`**이며, `message_service`, `inference_service`는 라우트 골격(placeholder)만 존재합니다.

---

## 1) 저장소 한눈에 보기

### 서비스 구성
- **User Service (`services/user_service`)**
  - FastAPI 기반 핵심 백엔드
  - 사용자 가입/로그인/프로필, 친구 관계, 챌린지, 파일 업로드, QR 기반 빠른 등록, 고양이 이미지 생성, 오디오 검증/BGM 관련 API 포함
  - SQLite(로컬) + PostgreSQL RDS(운영) 전환 지원
  - DynamoDB(Local/AWS), S3, Cognito, Gemini/Nanobanana 등 외부 연동 코드 포함

- **Message Service (`services/message_service`)**
  - 현재 `main.py`, routes 파일이 주석 수준의 placeholder 상태

- **Inference Service (`services/inference_service`)**
  - 현재 routes 파일이 주석 수준의 placeholder 상태

### 인프라 구성
- `k8s/`에 namespace, deployment, service, ingress, configmap, serviceaccount, secret template, cronjob manifest 포함
- `build-and-deploy.sh` / `build-and-deploy.ps1`로 Docker 빌드 및 ECR 푸시 후 EKS 롤아웃 자동화

---

## 2) 디렉토리 구조

```text
Final_Backend/
├── services/
│   ├── user_service/
│   │   ├── app/
│   │   │   ├── api/            # 라우터(v1/users/friends/challenges/upload/...)
│   │   │   ├── core/           # 설정, DB, 인증/보안, 로깅
│   │   │   ├── models/         # SQLAlchemy 모델
│   │   │   ├── repositories/   # DB 접근 레이어
│   │   │   ├── schemas/        # Pydantic 스키마
│   │   │   └── services/       # 비즈니스 로직 + 외부 서비스 연동
│   │   ├── migrations/         # SQL 마이그레이션 스크립트
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── run_local.py
│   ├── message_service/
│   └── inference_service/
├── k8s/                        # 쿠버네티스 매니페스트
├── docs/                       # API/배포/테스트 관련 문서
└── build-and-deploy.sh
```

---

## 3) User Service API 개요

기본 앱 진입점은 `services/user_service/app/main.py`입니다.

- Docs: `GET /docs`
- Health: `GET /health/`, `GET /health/detailed`, `GET /health/ready`, `GET /health/live`
- API Prefix: ` /api/v1`

주요 라우트 그룹:
- `/api/v1/users` : 로그인, 회원가입, 프로필 조회/수정, 상태/토큰 관리 등
- `/api/v1/friends` : 친구 요청/수락/거절/목록/삭제
- `/api/v1/challenges` : 챌린지 생성/조회/제출/히스토리/지도
- `/api/v1/upload` : 프로필 이미지/오디오 업로드
- `/api/v1/quick` : QR 기반 빠른 등록
- `/api/v1/cats`, `/api/v1/cat-character` : 고양이 이미지 생성 관련
- `/api/v1/audio` : 오디오 검증
- `/api/v1/bgm` : BGM 업데이트/조회

상세 API는 아래 문서를 함께 확인하세요.
- `docs/API_DOCUMENTATION.md`
- `services/user_service/CHALLENGE_API_DOCUMENTATION.md`
- `QUICK_REGISTER_API_SAMPLE.md`

---

## 4) 로컬 실행 방법 (User Service)

### 4.1 Python 직접 실행

```bash
cd services/user_service
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run_local.py
```

실행 후:
- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`

### 4.2 Docker 실행

```bash
cd services/user_service
docker build -t user-service:local .
docker run --rm -p 8000:8000 --env-file .env user-service:local
```

---

## 5) 환경 변수 핵심

`services/user_service/app/core/config.py` 기준 주요 환경 변수:

- 앱: `APP_NAME`, `DEBUG`, `ENVIRONMENT`, `PORT`
- DB:
  - 로컬: `DATABASE_URL` (기본 sqlite)
  - 운영: `USE_RDS=true` + `RDS_HOST`, `RDS_PORT`, `RDS_DATABASE`, `RDS_USERNAME`, `RDS_PASSWORD`
- AWS/Cognito/S3: `AWS_REGION`, `S3_BUCKET_NAME`, `COGNITO_*`
- DynamoDB:
  - 로컬: `USE_LOCAL_DYNAMODB=true`, `DYNAMODB_ENDPOINT_URL`
  - 운영: Pod Identity 기반 AWS DynamoDB 사용
- AI 연동: `GEMINI_API_KEY`, `NANOBANANA_API_URL`, `NANOBANANA_API_KEY`, `REPLICATE_TOKEN`

운영 배포 시 예시는 `k8s/configmap.yaml`, `k8s/secret.yaml.template` 참고.

---

## 6) 배포 (EKS)

기본 흐름:
1. 이미지 빌드
2. ECR 푸시
3. `user-service` deployment 롤아웃 재시작

스크립트 사용:

```bash
./build-and-deploy.sh [image-tag]
```

쿠버네티스 리소스:
- `k8s/namespace.yaml`
- `k8s/deployment.yaml`
- `k8s/service.yaml`
- `k8s/ingress.yaml`
- `k8s/configmap.yaml`
- `k8s/secret.yaml.template`

---

## 7) 참고 문서

- `docs/API_DOCUMENTATION.md`
- `docs/ACTUAL_TEST_RESULTS.md`
- `DATABASE_ERD.md`
- `docs/deployment/*`
- `INFRASTRUCTURE_COMPLETE_ANALYSIS.md`

---

## 8) 현재 상태 요약

- 이 저장소는 멀티서비스 구조를 갖추고 있으나, 실제 기능 구현은 `user_service`에 집중되어 있습니다.
- `message_service`, `inference_service`는 추후 구현이 필요한 초기 스캐폴딩 상태입니다.

