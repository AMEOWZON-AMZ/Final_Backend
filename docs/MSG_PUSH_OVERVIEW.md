# 한 줄 정리
msg-service는 쪽지/하트를 DynamoDB에 저장하고, Outbox에 푸시 이벤트를 기록한 뒤, push-worker가 Outbox를 주기적으로 폴링하여 FCM을 호출해 수신자 기기에 알림을 띄운다. SQS는 사용하지 않으며, 모든 이벤트는 Outbox 테이블을 통해 처리된다. 하트는 별도로 AuditEvents에도 기록된다.

---

## 1. 목표
- 기능: 쪽지/하트 전송, 받은 쪽지 조회, 받은 하트 기록 조회
- 알림: 쪽지/하트 전송 시 수신자에게 푸시 알림

---

## 2. 큰 흐름(End-to-End)
1) 앱에서 쪽지/하트 버튼 → msg-service API 호출
2) msg-service:
   - (필수) DynamoDB에 쪽지/하트 저장
   - (필수) OutboxEvents에 "푸시 필요" 이벤트 기록(PENDING)
   - 쪽지: Message + Outbox를 단일 트랜잭션으로 저장
   - 하트: Heart → Outbox → AuditEvents 순차 저장
   - 푸시 메시지 템플릿을 랜덤 선택하여 생성
3) push-worker:
   - Outbox 테이블을 주기적으로 폴링하여 PENDING/RETRY 이벤트 조회
   - 이벤트를 PROCESSING으로 마킹(낙관적 잠금)
   - DeviceTokens에서 수신자 FCM 토큰 조회
   - FCM 호출 → 수신자 휴대폰에 알림 표시
   - OutboxEvents 상태를 SENT/RETRY/FAILED로 업데이트(지수 백오프 재시도)
4) 수신자 앱:
   - 알림 클릭/앱 진입
   - msg-service 조회 API로 DynamoDB에서 메시지/하트 기록 조회

---

## 3. 역할 분리
- msg-service (FastAPI):
  - API 제공
  - 친구 여부 검증(친구만 전송)
  - DynamoDB 저장
  - OutboxEvents 기록
  - (선택) SQS 발행

- push-worker:
  - 이벤트 소비
  - FCM 발송
  - 재시도/실패 처리
  - OutboxEvents 상태 업데이트

- DynamoDB:
  - Messages / HeartEvents / DeviceTokens / Friends / OutboxEvents

- SQS:
  - “푸시 보내라” 작업 전달 (알림을 띄우는 주체가 아님)

- FCM:
  - 실제로 사용자 기기에 푸시 알림을 표시하는 서비스

---

## 4. Outbox 이벤트 구조
- Outbox는 이벤트 큐 역할을 하며, 모든 필드를 payload에 포함
- 이벤트 타입:
  - **PUSH_SEND**: 일반 푸시 알림 (쪽지/하트)
  - **CRITICAL_ALERT**: 위급 상황 알림 (data-only 전송, 전화 걸기 등)
  - **STATE_REFRESH**: 상태 갱신 알림 (data-only 전송, 앱 상태 새로고침용)

PUSH_SEND 예시 (쪽지):
```json
{
  "event_id": "msg_789",
  "event_type": "PUSH_SEND",
  "status": "PENDING",
  "attempt_count": 0,
  "next_retry_at": "2026-02-24T10:15:30Z",
  "created_at": "2026-02-24T10:15:30Z",
  "payload": {
    "title": "🐱 새 쪽지가 도착했어요",
    "body": "고양이가 전해준 말: 안녕하세요",
    "message_id": "msg_789",
    "from_user_id": "user_123",
    "to_user_id": "user_456"
  }
}
```

PUSH_SEND 예시 (하트):
```json
{
  "event_id": "heart_456",
  "event_type": "PUSH_SEND",
  "status": "PENDING",
  "attempt_count": 0,
  "next_retry_at": "2026-02-24T10:15:30Z",
  "created_at": "2026-02-24T10:15:30Z",
  "payload": {
    "title": "❤️ 하트가 도착했어요",
    "body": "철수님이 하트를 보냈어요",
    "heart_id": "heart_456",
    "from_user_id": "user_789",
    "to_user_id": "user_456"
  }
}
```

---

## 5. 테이블 구조 (실제 구현)
- **Messages** - 받은 쪽지 저장
  - PK: `RECEIVER#{to_user_id}`
  - SK: `{created_at}#{message_id}`
  - 속성: message_id, from_user_id, to_user_id, body, created_at, nickname

- **Hearts** - 받은 하트 기록
  - PK: `RECEIVER#{to_user_id}`
  - SK: `{created_at}#{heart_id}`
  - 속성: heart_id, from_user_id, to_user_id, created_at

- **DeviceTokens** - FCM 토큰 저장
  - PK: `USER#{user_id}`
  - SK: `TOKEN`
  - 속성: user_id, token, platform, updated_at

- **Friends** - 친구 관계 (2가지 스키마 지원)
  - 새 스키마: PK=user_id, SK=friend_user_id
  - 기존 스키마: PK=`USER#{user_id}`, SK=`FRIEND#{friend_id}`
  - 속성: user_id, friend_user_id, status, nickname
  - GSI1: friend_user_id 기반 역조회 (설정된 경우)

- **OutboxEvents** - 푸시 작업 큐
  - PK: `EVENT#{event_id}`
  - SK: `EVENT`
  - 속성: event_id, event_type, status, attempt_count, next_retry_at, created_at, payload, last_error
  - GSI: status-index (status를 PK로 사용하여 PENDING/RETRY 이벤트 조회)

- **AuditEvents** - 하트 감사 기록 (TTL 적용)
  - 하트 전송 시에만 기록됨
  - 구조는 audit_repo.py 참고

---

## 6. 실패/재시도 정책
- 저장 성공 후에만 푸시 시도
- 수신자 토큰 없으면 푸시 스킵하고 RETRY로 전환
- 지수 백오프 재시도:
  - MAX_ATTEMPTS: 8회
  - BASE_BACKOFF_SECONDS: 5초
  - MAX_BACKOFF_SECONDS: 300초
  - 계산식: min(5 × 2^(attempt-1), 300)
- 8회 재시도 후에도 실패하면 FAILED 상태로 전환
- 쪽지는 Message + Outbox 트랜잭션으로 동시성 보장
- 하트는 순차 저장 (Heart → Outbox → AuditEvents)

---

## 7. 푸시 템플릿
- 쪽지: 10가지 랜덤 템플릿 (예: "🐱 새 쪽지가 도착했어요", "💌 쪽지 도착")
- 하트: 10가지 랜덤 템플릿 (예: "❤️ 하트가 도착했어요", "{nickname}님이 하트를 보냈어요")
- 템플릿은 `shared/push_templates.py`에 정의됨
- 쪽지 본문은 80자까지 미리보기로 표시 (초과 시 ...)

---

## 8. 추가 이벤트 타입
- **CRITICAL_ALERT**: 위급 상황 알림
  - data-only 푸시 (알림 미표시)
  - 앱에서 전화 걸기 등 커스텀 동작 처리
  - 친구 닉네임 조회 포함

- **STATE_REFRESH**: 상태 갱신 알림
  - data-only 푸시 (알림 미표시)
  - 앱 상태 새로고침용
  - daily_status_sync에서 자동 생성됨
