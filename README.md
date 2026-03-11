
# Final_Backend

AMEOWZON 서비스의 백엔드 저장소입니다.

이 저장소는 **FastAPI 기반 이벤트 중심 마이크로서비스 구조**로 구성되어 있으며 사용자 관리, 메시지 상호작용, AI 추론 결과 반영, 이미지 검증 등 서비스 핵심 기능을 담당합니다.

백엔드는 다음과 같은 서비스로 구성됩니다.

* **user_service** : 사용자 계정, 친구, 챌린지 등 사용자 도메인 API
* **message_service** : 메시지/하트 이벤트 처리 및 푸시 알림 이벤트 생성
* **inference_service** : AI 추론 결과 기반 사용자 상태 동기화 및 위급 이벤트 처리
* **vision_service** : 이미지 업로드 후 CLIP 기반 콘텐츠 검증

---

# 1. 프로젝트 소개

이 프로젝트는 반려동물(고양이) 중심 소셜 앱을 위한 **이벤트 기반 마이크로서비스 백엔드**입니다.

핵심 목표는 다음과 같습니다.

1. 사용자 간 상호작용(메시지, 하트)을 안정적으로 저장
2. 이벤트 기반 구조를 통해 비동기 푸시 알림 처리
3. AI 추론 결과를 서비스 이벤트와 연결하여 사용자 상태 반영

서비스는 **FastAPI 기반 서비스 분리 구조**로 설계되어 각 기능이 독립적으로 확장될 수 있도록 구성되어 있습니다.

---

# 2. 저장소 한눈에 보기

## 서비스 구성

### User Service (`services/user_service`)

사용자 관련 기능을 담당하는 핵심 서비스입니다.

주요 기능

* 회원가입 / 로그인
* 사용자 프로필 관리
* 친구 관계 관리
* 챌린지 생성 및 참여
* 프로필 이미지 및 오디오 업로드
* QR 기반 빠른 등록
* 고양이 이미지 생성
* BGM 관리

특징

* FastAPI 기반 API 서버
* SQLite (로컬 개발) → PostgreSQL RDS (운영) 전환 구조
* DynamoDB(Local/AWS), S3, Cognito 연동
* Gemini / Nanobanana 등 외부 AI 서비스 연동

---

### Message Service (`services/message_service`)

사용자 간 메시지 및 상호작용 이벤트를 처리하는 서비스입니다.

주요 기능

* 메시지 전송 및 조회
* 하트 전송 및 조회
* 디바이스 토큰 등록
* Outbox 기반 푸시 이벤트 생성

메시지와 하트 이벤트는 데이터 저장 후 **비동기 푸시 알림 시스템과 연결됩니다.**

---

### Push Worker (`message_service` 내부)

Outbox 이벤트를 처리하는 비동기 워커입니다.

동작 흐름

1. Outbox 이벤트 조회 (`PENDING`, `RETRY`)
2. 이벤트 클레임
3. 디바이스 토큰 조회
4. FCM 전송
5. 이벤트 상태 업데이트 (`SENT`, `RETRY`, `FAILED`)

특징

* 지수 백오프 기반 재시도
* 중복 이벤트 처리 방지

---

### Inference Service (`services/inference_service`)

AI 추론 결과를 서비스 데이터에 반영하는 서비스입니다.

주요 기능

* 일일 상태 데이터 동기화
* 사용자 상태 업데이트
* 친구 관계 기반 상태 fan-out
* 위급 이벤트 처리

AI 추론 결과는 S3 CSV 데이터를 기반으로 서비스 상태 데이터에 반영됩니다.

---

### Vision Service (`services/vision_service`)

이미지 업로드 시 콘텐츠 검증을 수행하는 서비스입니다.

주요 기능

* 이미지 파일 형식 및 크기 검증
* 날짜 기반 주제 조회
* OpenCLIP 기반 이미지-텍스트 유사도 계산
* 임계치 기반 이미지 검증 결과 반환

---

# 3. 디렉토리 구조

```text
Final_Backend/
├── services/
│   ├── user_service/
│   │   ├── app/
│   │   │   ├── api/            # 사용자 / 친구 / 챌린지 / 업로드 API
│   │   │   ├── core/           # 설정, DB, 인증, 로깅
│   │   │   ├── models/         # SQLAlchemy 모델
│   │   │   ├── repositories/   # DB 접근 레이어
│   │   │   ├── schemas/        # Pydantic 스키마
│   │   │   └── services/       # 비즈니스 로직
│   │   ├── migrations/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── run_local.py
│   │
│   ├── message_service/        # 메시지 API + 푸시 워커
│   │   ├── apps/msg_service
│   │   └── apps/push_worker
│   │
│   ├── inference_service/      # AI 상태 동기화 서비스
│   │
│   └── vision_service/         # 이미지 검증 서비스
│
├── libs/common/                # 공통 모듈
├── deploy/k8s/                 # 쿠버네티스 매니페스트
├── docs/                       # API 및 아키텍처 문서
├── scripts/                    # 로컬 실행 스크립트
└── Makefile
```

---

# 4. 아키텍처

## 전체 구조

```
Client
  ↓
API Services (FastAPI)
  ├─ user_service
  ├─ message_service
  ├─ inference_service
  └─ vision_service
  ↓
Data / Event Layer
  ├─ DynamoDB
  ├─ S3
  └─ Outbox Events
  ↓
Push Worker
  ↓
FCM Push Notification
```

---

# 5. 핵심 기능

## 메시지 / 하트 도메인

* 메시지 전송 및 조회
* 하트 전송 및 감사 로그 기록
* 디바이스 토큰 등록

핵심 설계

* API는 데이터 저장만 수행
* 알림은 Outbox 이벤트로 생성
* 워커가 비동기 처리

---

## Outbox 기반 비동기 푸시

푸시 알림은 다음 흐름으로 처리됩니다.

```
API 요청
↓
메시지 저장
↓
Outbox 이벤트 생성
↓
Push Worker 처리
↓
FCM 알림 전송
```

이 구조는

* API 응답 지연 최소화
* 푸시 실패 격리
* 재시도 안정성 확보

를 위해 설계되었습니다.

---

## AI 상태 동기화

Inference 서비스는 S3 CSV 데이터를 기반으로 사용자 상태를 업데이트합니다.

주요 처리

* 사용자 상태 갱신
* 친구 관계 fan-out
* 상태 refresh 이벤트 생성

---

## 위급 이벤트 처리

위급 이벤트 발생 시

* critical snapshot 저장
* 친구 상태 `CRITICAL` 업데이트
* 외부 에이전트 이벤트 생성

---

## 이미지 주제 검증

Vision 서비스는 업로드된 이미지가 챌린지 주제에 적합한지 검증합니다.

검증 과정

1. 이미지 형식 및 크기 검증
2. 주제 조회
3. CLIP 기반 이미지-텍스트 유사도 계산
4. threshold 기반 결과 반환

---

# 6. 기술 스택

## Backend

* Python 3.11
* FastAPI
* Uvicorn
* Pydantic

## Database

* DynamoDB
* PostgreSQL (RDS)
* SQLite (로컬 개발)

## Storage

* AWS S3

## Infrastructure

* Docker
* Kubernetes (EKS)
* AWS ECR

## Messaging / Async

* Outbox Pattern
* FCM (Firebase Cloud Messaging)

## AI / Vision

* PyTorch
* OpenCLIP
* Pillow

---

# 7. 로컬 실행

### User Service

```bash
cd services/user_service

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
python run_local.py
```

접속

```
http://localhost:8000/docs
```

---

### Message Service

```bash
uvicorn services.message_service.apps.msg_service.main:app --reload --port 8080
```

Push Worker 실행

```bash
python -m services.message_service.apps.push_worker.main
```

---

### Inference Service

```bash
uvicorn services.inference_service.app.main:app --reload --port 8003
```

---

### Vision Service

```bash
uvicorn services.vision_service.app.main:app --reload --port 8004
```

---

# 8. 배포

서비스는 **Docker 컨테이너 기반 Kubernetes(EKS)** 환경에서 배포됩니다.

배포 흐름

```
Build Docker Image
  ↓
Push to AWS ECR
  ↓
Kubernetes Deployment Rollout
```

자동 배포 스크립트

```
build-and-deploy.sh
build-and-deploy.ps1
```

---
