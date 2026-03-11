# Final Backend 포트폴리오 README

> 이 문서는 **`services/inference_batch`를 제외한** 현재 저장소의 모든 주요 코드/서비스를 취업용 포트폴리오 관점에서 정리한 문서입니다.

---

## 1) 프로젝트 소개

이 프로젝트는 반려동물(고양이) 중심 소셜 앱을 위한 **이벤트 기반 마이크로서비스 백엔드**입니다. 핵심 목표는 다음 3가지입니다.

1. 사용자 간 상호작용(메시지/하트)을 안정적으로 저장한다.
2. 저장된 이벤트를 비동기 푸시(FCM)로 전달해 사용자 경험을 높인다.
3. AI 추론 결과(일일 상태, 위급 상태)를 서비스 이벤트로 연결해 실시간 대응성을 확보한다.

현재 코드베이스는 크게 아래 3개 서비스 + 공통/배포/문서 계층으로 구성됩니다.

- `message_service`: 쪽지/하트 API + outbox 기반 푸시 이벤트 생성 + push-worker
- `inference_service`: S3 CSV 기반 일일 상태 동기화 + 위급 이벤트 처리
- `vision_service`: 이미지 업로드 후 CLIP 기반 주제 적합도 검증 API
- `libs/common`: 공통 라이브러리 자리(현재 스캐폴드)
- `deploy/k8s`, `services/*/deploy|k8s`: 쿠버네티스 배포 리소스
- `docs`: 아키텍처/운영 문서
- `scripts`: 로컬 실행 편의 스크립트

### 저장소 폴더 요약 (inference_batch 제외)

```text
Final_Backend/
├─ services/
│  ├─ message_service/      # 메시지 API + 푸시 워커
│  ├─ inference_service/    # 일일 상태 동기화 + 위급 이벤트
│  └─ vision_service/       # 이미지-주제 검증
├─ libs/common/             # 공통 모듈 스캐폴드
├─ deploy/k8s/              # 공용 네임스페이스 등 인프라 매니페스트
├─ docs/                    # 아키텍처/계약/운영 문서
├─ scripts/                 # 로컬 실행 스크립트
└─ Makefile                 # 개발 명령 집합
```

---

## 2) 아키텍처

### 전체 아키텍처 개요

- API 계층은 FastAPI 기반으로 서비스별 독립 배포됩니다.
- 저장소는 DynamoDB 중심(메시지, 하트, 토큰, 친구, outbox, 상태 등)이며,
- 비동기 알림은 **Outbox 패턴 + Worker**로 처리됩니다.
- 추론 데이터는 S3 CSV를 ingestion 하여 사용자/친구 상태를 동기화합니다.

### 서비스별 책임

#### A. Message Service

- `POST /messages`, `GET /messages/inbox`
- `POST /hearts`, `GET /hearts/received`
- `POST /device-token`
- 핵심은 “쓰기 먼저, 알림은 나중에” 입니다.
  - 메시지/하트를 DynamoDB에 저장한 뒤,
  - Outbox 이벤트를 기록하고,
  - push-worker가 후속 비동기 처리합니다.

#### B. Push Worker (message_service 내부)

- Outbox에서 `PENDING/RETRY` 이벤트를 읽어 처리합니다.
- 이벤트 클레임(낙관적 잠금) → 토큰 조회 → FCM 전송 → 상태 갱신(`SENT/RETRY/FAILED`) 순으로 동작합니다.
- 지수 백오프(최대 8회)로 전송 안정성을 높였습니다.

#### C. Inference Service

- `POST /jobs/daily-status-sync`:
  - `s3://<bucket>/<prefix>/dt=YYYY-MM-DD/state_out.csv`를 읽어 사용자 상태 갱신
  - 친구 관계를 역조회해 fan-out 업데이트
  - 상태 리프레시용 Outbox 이벤트(`STATE_REFRESH`) 생성
- `POST /events/critical`:
  - 위급 이벤트를 1회성 트랜잭션으로 처리
  - critical snapshot 저장 + 친구 상태 `CRITICAL` fan-out
  - 에이전트 연동용 이벤트 enqueue

#### D. Vision Service

- `POST /vision/validate`:
  - 이미지 업로드 검증(형식/크기)
  - 날짜 기반 주제 조회(DB)
  - OpenCLIP으로 이미지-텍스트 유사도 계산
  - threshold 기반 매칭 결과 반환

### 폴더/운영 계층

- `deploy/k8s` + 각 서비스 k8s 매니페스트:
  - ServiceAccount, ConfigMap, Deployment/Service, CronJob 등을 제공
- `docs`:
  - API 계약, 아키텍처, pod 운영 문서
- `scripts/run_local.sh`, `Makefile`:
  - 로컬 개발/실행 자동화 엔트리

---

## 3) 기술 스택

### 백엔드/런타임

- Python 3.11
- FastAPI, Uvicorn
- Pydantic

### 데이터/인프라

- AWS DynamoDB (주 저장소)
- AWS S3 (추론 결과 원본)
- AWS SQS (일부 이벤트 연동 경로)
- Kubernetes(EKS 가정) + Docker

### 비동기/알림

- Outbox 패턴
- FCM(Firebase Cloud Messaging)
- 폴링 워커 + 재시도 백오프

### AI/비전

- PyTorch
- OpenCLIP
- Pillow
- SQLAlchemy (주제 조회)

### 공통/운영

- python-dotenv
- boto3/botocore
- 프로젝트 문서화(`docs/*.md`)

---

## 4) 핵심 기능

### 4-1. 메시지/하트 도메인

- 메시지 전송/조회, 하트 전송/조회 API 제공
- Device token 등록/업데이트 API 제공
- 하트는 감사 로그(Audit) 이벤트 기록까지 포함

**핵심 설계 포인트**
- 동기 API에서 직접 푸시를 보내지 않고, Outbox에 이벤트를 기록
- 쪽지는 메시지+아웃박스를 트랜잭션성으로 저장해 정합성 강화
- 푸시 본문은 템플릿 기반 랜덤 생성

### 4-2. Outbox 기반 비동기 푸시

- 워커가 이벤트를 선점(claim)하여 중복 처리 방지
- 토큰 미존재/전송 실패 시 RETRY 상태 전환
- 지수 백오프 + 최대 시도 제한으로 운영 안정성 확보
- 이벤트 타입별 대상 유저 추출(`PUSH_SEND`, `CRITICAL_ALERT`, `STATE_REFRESH`) 지원

### 4-3. 일일 상태 동기화 (Inference)

- 일 단위 CSV ingestion으로 추론 결과를 서비스 데이터에 반영
- 상태가 변하지 않아도 refresh 이벤트를 enqueue해 앱 동기화 보장
- 사용자 본인 + 관계 사용자 fan-out 업데이트
- 스케줄러 내장(시간대/시간 환경변수 기반)

### 4-4. 위급 이벤트 처리

- 동일 사용자의 중복 위급 처리 방지(once 처리)
- critical contacts snapshot 저장(TTL)
- 친구 관계 테이블 fan-out으로 `CRITICAL` 상태 전파
- 외부 에이전트 연동 큐 이벤트 전송

### 4-5. 비전 주제 검증

- 파일 MIME/용량/유효 이미지 검증
- 입력 이미지 정규화(JPEG)
- date 기반 topic 조회 후 CLIP score 계산
- 임계치 기반 matched 반환으로 클라이언트 판단 단순화

---

## 5) 문제 해결 (포트폴리오 강조 포인트)

아래는 “이 프로젝트에서 내가 해결한 백엔드 문제”로 인터뷰에서 설명하기 좋은 항목들입니다.

### 문제 1) API 응답 시간과 푸시 전달을 동시에 만족해야 함

- **문제**: 동기 API에서 FCM까지 처리하면 지연/실패 전파 위험이 큼
- **해결**: Outbox 패턴 도입
  - API는 영속화에 집중
  - 푸시는 워커에서 비동기 처리
- **성과**: 사용자 요청 성공률과 체감 응답성을 분리해 안정성 확보

### 문제 2) 푸시 전송 실패가 빈번한 운영 환경

- **문제**: 토큰 무효/일시 장애/네트워크 오류 등으로 알림 누락 발생
- **해결**:
  - `PENDING → PROCESSING → SENT/RETRY/FAILED` 상태 머신
  - 지수 백오프, 최대 재시도 횟수, 오류 로그 축적
- **성과**: 일시적 장애 흡수 + 운영자가 실패 케이스를 추적 가능

### 문제 3) 추론 결과 반영 시 데이터 정합성/파급범위 관리

- **문제**: 사용자 상태 변경이 친구 화면까지 연결되어야 함
- **해결**:
  - 상태 업데이트 + 친구 fan-out 업데이트 루프 구현
  - CSV row 단위 처리 통계(`processed/updated/skipped/errors`) 반환
  - refresh 이벤트를 명시적으로 enqueue
- **성과**: 상태 반영 누락을 줄이고 관측 가능성 개선

### 문제 4) 위급 이벤트 중복 처리 방지

- **문제**: 동일 사용자에 대해 위급 이벤트가 중복 유입될 수 있음
- **해결**: 트랜잭션 기반 once 처리 + 이미 위급 상태이면 skip
- **성과**: 중복 알림/중복 전파 방지, 신뢰성 강화

### 문제 5) 비전 모델 API의 입력 신뢰성

- **문제**: 손상 파일/비이미지/대용량 업로드가 모델 파이프라인을 깨뜨릴 수 있음
- **해결**: 업로드 초기에 형식/크기/디코딩 검증, 명확한 HTTP 에러 반환
- **성과**: 모델 추론 안정성 및 API 사용성 개선

---

## 서비스별 빠른 실행 가이드

> 실제 실행 전 서비스별 `.env`/AWS 자격증명 설정이 필요합니다.

### message_service

```bash
uvicorn services.message_service.apps.msg_service.main:app --reload --port 8080
python -m services.message_service.apps.push_worker.main
```

### inference_service

```bash
pip install -r services/inference_service/requirements.txt
python services/inference_service/scripts/check_ddb_connection.py
uvicorn services.inference_service.app.main:app --reload --port 8003
```

### vision_service

```bash
pip install -r services/vision_service/requirements.txt
uvicorn services.vision_service.app.main:app --reload --port 8004
```
