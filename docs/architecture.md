# 아키텍처 문서

## 🏗️ 시스템 개요

이 프로젝트는 **마이크로서비스 아키텍처**로 설계된 고양이 친구 매칭 앱의 백엔드입니다. AWS EKS에 배포되며 여러 서비스가 독립적으로 실행되지만 DynamoDB와 SQS를 통해 통신합니다.

```
┌─────────────────────────────────────────────────────────────┐
│                     모바일 앱 (Android/iOS)                  │
└──────────────┬─────────────────────────────────────────────┘
               │ (FCM, REST API)
    ┌──────────▼──────────────────────────────────┐
    │         AWS ALB / API Gateway                │
    └──────────┬────────────────────────────────────┘
               │
    ┌──────────┴───────────────────────────────────────────┐
    │              EKS Cluster (Kubernetes)                │
    │  ┌──────────────┐  ┌──────────────┐  ┌────────────┐  │
    │  │   msg-      │  │  inference   │  │   user     │  │
    │  │  service    │  │   service    │  │  service   │  │
    │  │ (Port 8001) │  │ (Port 8003)  │  │ (Port 8000)│  │
    │  └──────┬───────┘  └──────┬───────┘  └────┬───────┘  │
    │         │                 │                │          │
    │         └─────────────────┼────────────────┘          │
    │                           │                           │
    │  ┌──────────────────────────▼──────────────────────┐  │
    │  │      push-worker (CronJob)                       │  │
    │  │   - Outbox 폴링                                  │  │
    │  │   - FCM 푸시 전송                                │  │
    │  └──────────────────────────┬──────────────────────┘  │
    │                           │                           │
    │  ┌──────────────────────────▼──────────────────────┐  │
    │  │      daily-status-sync (CronJob)                │  │
    │  │   - S3 CSV 읽기                                 │  │
    │  │   - 상태 동기화                                 │  │
    │  └─────────────────────────────────────────────────┘  │
    │                                                        │
    └────────────────────────────────────────────────────────┘
               │
    ┌──────────▼──────────────────────────────────┐
    │       AWS 서비스 (Region: ap-northeast-2)    │
    │                                             │
    │  ┌──────────────┐  ┌──────────────┐        │
    │  │  DynamoDB    │  │   S3 Bucket  │        │
    │  │              │  │              │        │
    │  │ • Messages   │  │ • ML outputs │        │
    │  │ • Hearts     │  │ • state_out  │        │
    │  │ • DeviceTokens                 │        │
    │  │ • OutboxEvents                 │        │
    │  │ • Friends    │  │              │        │
    │  │ • AuditEvents                  │        │
    │  └──────────────┘  └──────────────┘        │
    │                                             │
    │  ┌──────────────┐  ┌──────────────┐        │
    │  │  SQS Queue   │  │  ECR Registry│        │
    │  │              │  │              │        │
    │  │ (예약됨,      │  │ 컨테이너 이미지│      │
    │  │  현재 미사용)  │  │              │        │
    │  └──────────────┘  └──────────────┘        │
    └──────────────────────────────────────────────┘
               │
    ┌──────────▼──────────────────────────────────┐
    │       외부 서비스 (Third-party)              │
    │                                             │
    │  ┌──────────────┐  ┌──────────────┐        │
    │  │   FCM API    │  │ Google Auth  │        │
    │  │  (Firebase)  │  │   (optional) │        │
    │  └──────────────┘  └──────────────┘        │
    └──────────────────────────────────────────────┘
```

---

## 🎯 마이크로서비스 상세

### 1. Message Service (메시지 서비스)
**목적**: 쪽지와 하트 기능 관리, 푸시 알림 조율

**포트**: 8001

**핵심 기능**:
- 사용자 간 쪽지 전송 및 조회
- 하트(좋아요) 전송 및 기록
- FCM 토큰 관리
- Outbox 패턴으로 푸시 이벤트 생성

**API 엔드포인트**:
- `POST /messages` - 쪽지 전송
- `GET /messages/inbox` - 받은 쪽지 조회
- `POST /hearts` - 하트 전송
- `GET /hearts/received` - 받은 하트 조회
- `POST /device-token` - 기기 토큰 등록

**데이터 흐름**:
```
쪽지 전송 API 호출
    ↓
Message + Outbox 트랜잭션 저장
    ↓
push-worker가 Outbox 폴링
    ↓
FCM 토큰 조회 및 푸시 전송
    ↓
Outbox 상태 업데이트 (SENT/RETRY/FAILED)
```

---

### 2. Inference Service (추론 서비스)
**목적**: 머신러닝 추론 결과 처리 및 위급 이벤트 관리

**포트**: 8003

**핵심 기능**:
- S3에서 일일 상태 CSV 읽기 및 동기화
- 상태 변경 시 친구에게 알림 (STATE_REFRESH)
- 위급 상황(SOS) 보고 및 친구 알림
- CronJob으로 자동 스케줄링

**API 엔드포인트**:
- `POST /jobs/daily-status-sync` - 일일 상태 동기화 (수동)
- `POST /events/critical` - 위급 이벤트 보고

**데이터 흐름**:
```
Daily Status Sync (매일 06:00 KST)
    ↓
S3 state_out.csv 읽기
    ↓
사용자별 상태 업데이트
    ↓
영향받은 사용자 + 친구들에게 STATE_REFRESH 생성
    ↓
push-worker가 처리하여 FCM 전송
```

---

### 3. User Service (사용자 서비스)
**목적**: 사용자 프로필 및 친구 관계 관리

**포트**: 8000

**핵심 기능**:
- 사용자 프로필 조회 및 수정
- 친구 추가/삭제/목록 조회
- 소셜 로그인 통합
- 사용자 검색

**상태**: 향후 구현 예정 (기본 구조만 설정됨)

---

### 4. Vision Service (비전 서비스)
**목적**: 이미지 처리 및 비전 분석

**포트**: 8004 (예정)

**상태**: 향후 구현 예정

---

### 5. Push Worker (푸시 워커)
**목적**: Outbox 테이블에서 이벤트를 폴링하여 FCM 푸시 전송

**실행**: 지속적 프로세스 또는 정기적 스케줄

**처리 로직**:
```python
while True:
    # PENDING/RETRY 이벤트 조회
    events = outbox_repo.query_ready(limit=10)
    
    for event in events:
        # 이벤트를 PROCESSING으로 마킹 (낙관적 잠금)
        if not repo.try_mark_processing(event_id):
            continue
        
        # FCM 토큰 조회
        token = device_token_repo.get_token(to_user_id)
        
        # FCM 푸시 전송
        success = send_fcm(token, event.payload)
        
        # 결과에 따라 상태 업데이트
        if success:
            repo.mark_sent(event_id)
        else:
            # 지수 백오프: 5s → 10s → 20s → ... → 300s (MAX)
            repo.mark_retry(event_id, next_retry_at)
            
            # 8회 재시도 후에도 실패하면 FAILED로 전환
            if attempt_count >= 8:
                repo.mark_failed(event_id)
```

**재시도 정책**:
- 최대 시도: 8회
- 초기 백오프: 5초
- 최대 백오프: 300초
- 지수 증가: min(5 × 2^(attempt-1), 300)

---

## 💾 데이터 모델

### DynamoDB 테이블 구조

#### 1. Messages (쪽지)
```
PK: RECEIVER#{to_user_id}
SK: {created_at}#{message_id}

속성:
- message_id (String)
- from_user_id (String)
- to_user_id (String)
- body (String, 최대 4000자)
- nickname (String)
- created_at (ISO-8601)
```

#### 2. Hearts (하트)
```
PK: RECEIVER#{to_user_id}
SK: {created_at}#{heart_id}

속성:
- heart_id (String)
- from_user_id (String)
- to_user_id (String)
- created_at (ISO-8601)
```

#### 3. DeviceTokens (FCM 토큰)
```
PK: USER#{user_id}
SK: TOKEN

속성:
- user_id (String)
- token (String, FCM 토큰)
- platform (String, "android" or "ios")
- updated_at (ISO-8601)
```

#### 4. Friends (친구 관계)
```
PK: user_id
SK: friend_user_id

또는 (레거시):
PK: USER#{user_id}
SK: FRIEND#{friend_id}

속성:
- user_id (String)
- friend_user_id (String)
- status (String, "ACCEPTED")
- nickname (String)
```

#### 5. OutboxEvents (푸시 이벤트 큐)
```
PK: EVENT#{event_id}
SK: EVENT

GSI (status-index):
PK: status (PENDING, PROCESSING, RETRY, SENT, FAILED)
SK: created_at#{event_id}

속성:
- event_id (String)
- event_type (String, PUSH_SEND / CRITICAL_ALERT / STATE_REFRESH)
- status (String)
- attempt_count (Number)
- next_retry_at (ISO-8601)
- created_at (ISO-8601)
- payload (Map)
- last_error (String, optional)
```

#### 6. AuditEvents (감사 기록)
```
TTL: 설정됨 (삭제 자동화)

속성:
- event_type (String)
- ref_id (String)
- from_user_id (String)
- to_user_id (String)
- created_at (ISO-8601)
```

---

## 🔄 데이터 흐름 시나리오

### 시나리오 1: 쪽지 전송 및 푸시 알림

```
1. 사용자 A가 사용자 B에게 쪽지 전송
   POST /messages
   ├─ from_user_id: user_A
   ├─ to_user_id: user_B
   └─ body: "안녕하세요!"

2. msg-service가 처리
   ├─ Message 아이템 생성
   ├─ OutboxEvent 아이템 생성 (PUSH_SEND)
   └─ DynamoDB 트랜잭션으로 원자성 보장

3. push-worker가 Outbox 폴링
   ├─ status="PENDING" 이벤트 조회
   └─ 이벤트를 PROCESSING으로 마킹

4. FCM 토큰 조회
   ├─ user_B의 DeviceTokens 조회
   └─ FCM 토큰 획득

5. FCM 푸시 전송
   ├─ FCM v1 API 호출
   ├─ 알림 제목: "🐱 새 쪽지가 도착했어요"
   ├─ 알림 본문: "고양이가 전해준 말: 안녕하세요!"
   └─ 사용자 B의 휴대폰에 알림 표시

6. 결과 처리
   ├─ 성공: OutboxEvent.status = "SENT"
   ├─ 실패: retry 로직 실행
   │  ├─ attempt_count 증가
   │  ├─ 지수 백오프로 next_retry_at 계산
   │  └─ OutboxEvent.status = "RETRY"
   └─ 최대 재시도 초과: status = "FAILED"
```

### 시나리오 2: 일일 상태 동기화

```
1. CronJob 트리거 (매일 06:00 KST)
   └─ python -m services.inference_service.app.jobs.daily_status_sync_job

2. S3에서 state_out.csv 다운로드
   ├─ 경로: s3://nyang-ml-apne2-dev/ml/outputs/dt=YYYY-MM-DD/state_out.csv
   ├─ 필수 컬럼: uuid, date, cat_state
   └─ 행 처리 (배치 방식)

3. 각 행마다 상태 업데이트
   ├─ uuid를 user_id로 맵핑
   ├─ cat_state를 daily_status로 저장
   ├─ 상태 변경 여부 확인
   └─ 변경된 사용자 수집

4. 친구들에게 팬아웃 업데이트
   ├─ 상태 변경된 user_X의 친구들 조회
   ├─ 각 친구의 Friends 테이블 업데이트
   └─ 영향받은 모든 사용자 ID 수집

5. STATE_REFRESH 이벤트 생성
   ├─ 상태 변경된 사용자
   ├─ 상태 변경된 사용자의 친구들
   └─ 각각에 대해 OutboxEvent 생성 (event_type=STATE_REFRESH)

6. push-worker가 STATE_REFRESH 처리
   ├─ FCM data-only 메시지 전송 (시각적 알림 없음)
   ├─ 앱에서 상태 새로고침 트리거
   └─ OutboxEvent.status = "SENT"
```

### 시나리오 3: 위급 상황 (SOS) 보고

```
1. 사용자가 위급 버튼 클릭
   POST /events/critical
   ├─ critical_user_id: user_X
   ├─ critical_gps: {latitude, longitude}
   └─ friends: [친구 정보 배열]

2. inference-service가 처리
   ├─ 이미 위급 상태 확인
   ├─ CRITICAL_ALERT 이벤트 생성
   ├─ 친구의 위치 정보 저장
   └─ SQS에 critical agent 작업 발행

3. push-worker가 CRITICAL_ALERT 처리
   ├─ FCM data-only 메시지 전송
   └─ 앱에서 위급 알림 처리
      ├─ 통화 화면 표시
      ├─ GPS 위치 표시
      └─ 친구 정보 표시

4. 친구들의 시스템
   ├─ Friends GSI로 user_X의 친구 조회
   ├─ user_X의 상태를 "CRITICAL"로 마킹
   └─ 친구들의 앱에 알림 전송
```

---

## 🚀 배포 아키텍처

### Kubernetes 리소스

#### Namespace
```yaml
metadata:
  name: default  # 필요시 별도 namespace 생성
```

#### Service Account (IRSA)
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: inference-service-sa
  namespace: default
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::ACCOUNT:role/inference-service-role
```

#### Deployment (msg-service)
```yaml
kind: Deployment
metadata:
  name: msg-service
spec:
  replicas: 2
  selector:
    matchLabels:
      app: msg-service
  template:
    spec:
      serviceAccountName: msg-service-sa
      containers:
      - name: msg-service
        image: ECR_ACCOUNT.dkr.ecr.ap-northeast-2.amazonaws.com/msg-service:latest
        ports:
        - containerPort: 8001
        env:
        - name: DDB_MESSAGES_TABLE
          value: "Messages"
        - name: DDB_HEARTS_TABLE
          value: "Hearts"
        # ... 기타 환경 변수
```

#### CronJob (Daily Status Sync)
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: daily-status-sync
spec:
  schedule: "0 6 * * *"  # 매일 06:00 KST
  timeZone: "Asia/Seoul"
  concurrencyPolicy: Forbid
  jobTemplate:
    spec:
      template:
        spec:
          serviceAccountName: inference-service-sa
          containers:
          - name: daily-sync
            image: ECR_ACCOUNT.dkr.ecr.ap-northeast-2.amazonaws.com/inference-service:latest
            command:
            - python
            - -m
            - services.inference_service.app.jobs.daily_status_sync_job
          restartPolicy: OnFailure
```

---

## 🔐 보안 고려사항

### 1. IAM 권한 (최소 권한 원칙)
```
msg-service:
- s3:GetObject (DeviceTokens 읽기용 - 미사용)
- dynamodb:GetItem (DeviceTokens)
- dynamodb:PutItem (Messages, Hearts, OutboxEvents)
- dynamodb:UpdateItem (OutboxEvents status 업데이트)
- dynamodb:Query (받은 메시지/하트 조회)

inference-service:
- s3:ListBucket (ml/outputs 폴더)
- s3:GetObject (state_out.csv)
- dynamodb:UpdateItem (UserStatus)
- dynamodb:PutItem (OutboxEvents)
- dynamodb:Query (Friends 조회)

push-worker:
- dynamodb:Query (Outbox 폴링)
- dynamodb:GetItem (Outbox 상세)
- dynamodb:UpdateItem (Outbox 상태 업데이트)
- dynamodb:GetItem (DeviceTokens)
```

### 2. 데이터 암호화
- DynamoDB: 저장 시 암호화 (기본 활성화)
- S3: 저장 시 암호화 (기본 활성화)
- 통신: TLS/SSL (ALB를 통한 HTTPS)

### 3. 환경 변수 관리
- Kubernetes Secrets 사용
- 민감한 정보 (API 키, DB 접근) 저장
- AWS Systems Manager Parameter Store 통합 가능

---

## 📊 성능 특성

### 처리량
- Message Service: ~1,000 TPS (DynamoDB 프로비저닝에 따라)
- Outbox 폴링: 10개씩 배치 처리, ~초 단위 처리
- 일일 상태 동기화: CSV 크기에 따라 수분 소요

### 레이턴시
- 쪽지 전송: <100ms
- 푸시 알림 도달: <5초 (FCM 포함)
- 상태 동기화: 수초

### 확장성
- 수평 확장: Deployment replicas 증가
- 수직 확장: 인스턴스 타입 변경
- DynamoDB: On-demand 스케일링 또는 프로비저닝 모드

---

## 🔍 모니터링 및 로깅

### CloudWatch
- 애플리케이션 로그: Deployment 업로드
- CronJob 로그: 실행 결과 저장
- 메트릭: CPU, 메모리, 디스크

### 알림 설정 (권장)
- CronJob 실패 시 이메일 알림
- DynamoDB 용량 초과 시 경고
- 푸시 실패율 모니터링

### 로그 분석
- ELK Stack 통합 가능
- CloudWatch Insights 활용
- 분석: 장애 추적, 성능 분석

---

## 🔄 향후 개선사항

1. **API Gateway 도입**
   - 서비스 통합 및 버전 관리
   - Rate limiting 추가
   - 문서 자동 생성

2. **Service Mesh (Istio)**
   - 트래픽 관리 개선
   - 서킷 브레이커 추가
   - 트레이싱 통합

3. **Event Streaming (Kafka)**
   - SQS 대체 고려
   - 실시간 이벤트 처리
   - 다중 구독자 지원

4. **GraphQL API**
   - 점진적 마이그레이션
   - 유연한 쿼리 지원

5. **캐싱 계층 (Redis)**
   - DynamoDB 쿼리 최소화
   - 성능 개선
   - 사용자 세션 관리