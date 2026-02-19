# 한 줄 정리
msg-service는 쪽지/하트를 DynamoDB에 저장(사실 기록)하고, Outbox로 푸시 이벤트를 유실 없이 남긴 뒤, SQS로 worker에게 ‘푸시 보내라’ 작업을 전달하며, worker가 FCM을 호출해 수신자 기기에 알림을 띄운다. 보낸함 UI는 제공하지 않되, 관리 대비 최소 AuditEvents 기록을 TTL로 보관한다.
---

## 1. 목표
- 기능: 쪽지/하트 전송, 받은 쪽지 조회, (선택) 받은 하트 기록 조회
- 알림: 쪽지/하트 전송 시 수신자에게 푸시 알림

---

## 2. 큰 흐름(End-to-End)
1) 앱에서 쪽지/하트 버튼 → msg-service API 호출
2) msg-service:
   - (필수) DynamoDB에 쪽지/하트 저장
   - (필수) OutboxEvents에 “푸시 필요” 이벤트 기록(PENDING)
   - (권장) SQS에 “푸시 보내라” 이벤트 발행(최소 정보)
3) push-worker:
   - SQS(또는 Outbox)에서 이벤트 수신
   - DeviceTokens에서 수신자 FCM 토큰 조회
   - FCM 호출 → 수신자 휴대폰에 알림 표시
   - OutboxEvents 상태를 SENT/FAILED로 업데이트(재시도 포함)
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

## 4. SQS 메시지에는 무엇이 들어가나?
- SQS는 전달용. DB가 원본.
- 본문(쪽지 content)은 SQS에 넣지 않는다(기본 원칙).
- 최소 필드만:
  - event_type: MESSAGE | HEART
  - from_user_id
  - to_user_id
  - ref_id: message_id 또는 event_id
  - created_at (UTC ISO-8601 Z)

예시:
{
  "event_type": "MESSAGE",
  "from_user_id": "user_123",
  "to_user_id": "user_456",
  "ref_id": "msg_789",
  "created_at": "2026-02-03T10:15:30Z"
}

---

## 5. 테이블(초기 분리형 권장)
- Messages
  - PK: receiver_id
  - SK: created_at#message_id
  - sender_id, content, created_at, message_id, read_at(optional)
  - (optional) GSI for sent: sender_id + created_at#message_id

- HeartEvents
  - PK: receiver_id
  - SK: created_at#event_id
  - sender_id, created_at, event_id
  - (optional) idempotency_key

- DeviceTokens
  - PK: user_id
  - fcm_token, platform, updated_at

- Friends
  - PK: user_id
  - SK: friend_id
  - status: ACCEPTED 등

- OutboxEvents
  - PK: status (PENDING/SENT/FAILED)
  - SK: created_at#event_id
  - type(MESSAGE/HEART), to_user_id, payload, retry_count, created_at

---

## 6. 실패/중복 기본 정책
- 저장 성공 후에만 푸시 시도
- 수신자 토큰 없으면 푸시 스킵(저장은 유지)
- worker 재시도 및 실패 누적 시 FAILED 전환
- 하트는 idempotency(연타 중복 처리 방지) 고려
