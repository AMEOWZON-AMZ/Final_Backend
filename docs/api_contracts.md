# API 계약서

## 🎯 개요

백엔드는 3개의 마이크로서비스로 구성되어 있으며, 각각 고유한 API 엔드포인트를 제공합니다. 모든 API는 JSON 기반 요청/응답을 사용합니다.

---

## 📋 Message Service (메시지 서비스)

메시지와 하트 기능을 담당하는 서비스입니다.

### 1. 메시지 API

#### 1.1 쪽지 생성
**요청:**
```http
POST /messages
Content-Type: application/json

{
  "from_user_id": "user_123",
  "to_user_id": "user_456",
  "body": "안녕하세요! 반갑습니다.",
  "nickname": "철수"
}
```

**응답 (성공):**
```json
{
  "ok": true,
  "message_id": "msg_789",
  "created_at": "2026-02-24T10:15:30Z"
}
```

**응답 (실패):**
```json
{
  "ok": false,
  "detail": "Error message"
}
```

#### 1.2 받은 쪽지 조회
**요청:**
```http
GET /messages/inbox?to_user_id=user_456&limit=20
```

**응답:**
```json
{
  "ok": true,
  "items": [
    {
      "pk": "RECEIVER#user_456",
      "sk": "2026-02-24T10:15:30Z#msg_789",
      "message_id": "msg_789",
      "from_user_id": "user_123",
      "to_user_id": "user_456",
      "body": "안녕하세요! 반갑습니다.",
      "nickname": "철수",
      "created_at": "2026-02-24T10:15:30Z"
    }
  ]
}
```

### 2. 하트 API

#### 2.1 하트 전송
**요청:**
```http
POST /hearts
Content-Type: application/json

{
  "from_user_id": "user_789",
  "to_user_id": "user_456",
  "nickname": "막내"
}
```

**응답 (성공):**
```json
{
  "ok": true,
  "heart_id": "heart_456",
  "created_at": "2026-02-24T10:15:30Z"
}
```

#### 2.2 받은 하트 조회
**요청:**
```http
GET /hearts/received?to_user_id=user_456&limit=20
```

**응답:**
```json
{
  "ok": true,
  "items": [
    {
      "pk": "RECEIVER#user_456",
      "sk": "2026-02-24T10:15:30Z#heart_456",
      "heart_id": "heart_456",
      "from_user_id": "user_789",
      "to_user_id": "user_456",
      "created_at": "2026-02-24T10:15:30Z"
    }
  ]
}
```

### 3. 기기 토큰 API

#### 3.1 FCM 토큰 등록/업데이트
**요청:**
```http
POST /device-token
Content-Type: application/json

{
  "user_id": "user_456",
  "token": "fcm_token_here",
  "platform": "android"
}
```

**응답:**
```json
{
  "ok": true,
  "message": "Device token registered"
}
```

### 4. Health Check API

#### 4.1 헬스 체크
**요청:**
```http
GET /health
```

**응답:**
```json
{
  "status": "healthy"
}
```

---

## 📋 Inference Service (추론 서비스)

사용자 상태 동기화 및 위급 이벤트 처리를 담당하는 서비스입니다.

### 1. 일일 상태 동기화 API

#### 1.1 일일 상태 동기화 (수동 트리거)
**요청:**
```http
POST /jobs/daily-status-sync?target_date=2026-02-23
```

**응답 (성공):**
```json
{
  "ok": true,
  "result": {
    "target_date": "2026-02-23",
    "s3_bucket": "nyang-ml-apne2-dev",
    "s3_key": "ml/outputs/dt=2026-02-23/state_out.csv",
    "processed": 100,
    "updated": 45,
    "skipped": 55,
    "errors": 0,
    "refresh_enqueued": 50
  }
}
```

**응답 (파일 없음):**
```json
{
  "ok": true,
  "result": {
    "action": "SKIPPED",
    "reason": "daily_status_file_not_found",
    "target_date": "2026-02-23",
    "s3_bucket": "nyang-ml-apne2-dev",
    "s3_key": "ml/outputs/dt=2026-02-23/state_out.csv",
    "processed": 0,
    "updated": 0,
    "skipped": 0,
    "errors": 0
  }
}
```

### 2. 위급 이벤트 API

#### 2.1 위급 상황 보고
**요청:**
```http
POST /events/critical
Content-Type: application/json

{
  "event_id": "critical_event_001",
  "critical_user_id": "user_123",
  "occurred_at": "2026-02-24T10:15:30Z",
  "critical_gps": {
    "latitude": 37.5,
    "longitude": 127.0
  },
  "friends": [
    {
      "user_id": "user_456",
      "phone_number": "010-1234-5678"
    },
    {
      "user_id": "user_789",
      "phone_number": "010-9876-5432"
    }
  ]
}
```

**응답 (성공):**
```json
{
  "ok": true,
  "result": {
    "action": "UPDATED",
    "critical_user_id": "user_123",
    "critical_agent_enqueued": true,
    "fanout_updated": 2,
    "occurred_at": "2026-02-24T10:15:30Z",
    "updated_at": "2026-02-24T10:15:31Z"
  }
}
```

**응답 (이미 위급 상태):**
```json
{
  "ok": true,
  "result": {
    "action": "SKIPPED",
    "reason": "already_critical"
  }
}
```

### 3. Health Check API

#### 3.1 기본 헬스 체크
**요청:**
```http
GET /health
```

**응답:**
```json
{
  "status": "healthy"
}
```

#### 3.2 상세 헬스 체크
**요청:**
```http
GET /health/detailed
```

**응답:**
```json
{
  "status": "healthy",
  "dynamodb": "connected",
  "timestamp": "2026-02-24T10:15:30Z"
}
```

---

## 🔄 공통 응답 형식

### 성공 응답
모든 성공 응답은 다음 형식을 따릅니다:
```json
{
  "ok": true,
  "message": "Success message",
  "data": {}
}
```

### 에러 응답
모든 실패 응답은 다음 형식을 따릅니다:
```json
{
  "ok": false,
  "detail": "Error description",
  "error_code": "ERROR_CODE"
}
```

---

## 🚀 Outbox 이벤트 (푸시 알림 처리)

메시지/하트 전송 시 자동으로 생성되는 이벤트입니다. 별도의 API 호출이 필요하지 않습니다.

### Outbox 이벤트 구조

**생성된 이벤트 (DynamoDB OutboxEvents 테이블에 저장):**
```json
{
  "pk": "EVENT#msg_789",
  "sk": "EVENT",
  "event_id": "msg_789",
  "event_type": "PUSH_SEND",
  "status": "PENDING",
  "attempt_count": 0,
  "next_retry_at": "2026-02-24T10:15:30Z",
  "created_at": "2026-02-24T10:15:30Z",
  "payload": {
    "title": "🐱 새 쪽지가 도착했어요",
    "body": "고양이가 전해준 말: 안녕하세요!",
    "message_id": "msg_789",
    "from_user_id": "user_123",
    "to_user_id": "user_456"
  }
}
```

**이벤트 상태:**
- `PENDING`: 처리 대기 중
- `PROCESSING`: 현재 처리 중
- `RETRY`: 재시도 대기 중
- `SENT`: 성공적으로 전송됨
- `FAILED`: 최대 재시도 횟수 초과로 실패

---

## 🔧 테스트 방법

### Message Service 테스트
```bash
# 쪽지 전송
curl -X POST "http://localhost:8001/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "from_user_id": "user_123",
    "to_user_id": "user_456",
    "body": "안녕하세요!",
    "nickname": "철수"
  }'

# 받은 쪽지 조회
curl "http://localhost:8001/messages/inbox?to_user_id=user_456"

# 하트 전송
curl -X POST "http://localhost:8001/hearts" \
  -H "Content-Type: application/json" \
  -d '{
    "from_user_id": "user_789",
    "to_user_id": "user_456",
    "nickname": "막내"
  }'

# 받은 하트 조회
curl "http://localhost:8001/hearts/received?to_user_id=user_456"
```

### Inference Service 테스트
```bash
# 일일 상태 동기화 (수동)
curl -X POST "http://localhost:8003/jobs/daily-status-sync?target_date=2026-02-23"

# 위급 이벤트 보고
curl -X POST "http://localhost:8003/events/critical" \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "critical_001",
    "critical_user_id": "user_123",
    "occurred_at": "2026-02-24T10:15:30Z",
    "critical_gps": {
      "latitude": 37.5,
      "longitude": 127.0
    },
    "friends": [
      {
        "user_id": "user_456",
        "phone_number": "010-1234-5678"
      }
    ]
  }'
```

---

## 📝 주요 특징

### Message Service
- ✅ 쪽지 및 하트 전송
- ✅ 트랜잭션 기반 데이터 일관성 보장
- ✅ 자동 푸시 알림 생성
- ✅ DynamoDB Outbox 패턴으로 이벤트 유실 방지
- ✅ 지수 백오프 재시도 (최대 8회)

### Inference Service  
- ✅ S3 CSV 기반 일일 상태 동기화
- ✅ 위급 이벤트 처리
- ✅ 친구에게 상태 변경 알림 (STATE_REFRESH)
- ✅ Kubernetes CronJob으로 자동 스케줄링
- ✅ 수동 트리거 엔드포인트 제공