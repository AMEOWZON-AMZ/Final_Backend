# 02_event_schema

Outbox 이벤트 스키마 (DynamoDB에 저장되는 형태):

```json
{
  "pk": "EVENT#{event_id}",
  "sk": "EVENT",
  "event_id": "string (message_id 또는 heart_id)",
  "event_type": "PUSH_SEND | CRITICAL_ALERT | STATE_REFRESH",
  "status": "PENDING | PROCESSING | RETRY | SENT | FAILED",
  "attempt_count": 0,
  "next_retry_at": "YYYY-MM-DDTHH:MM:SS.mmmmmm",
  "created_at": "YYYY-MM-DDTHH:MM:SS.mmmmmm",
  "payload": {
    "title": "string (PUSH_SEND만)",
    "body": "string (PUSH_SEND만)",
    "message_id": "string (쪽지인 경우)",
    "heart_id": "string (하트인 경우)",
    "from_user_id": "string",
    "to_user_id": "string or [array] (단일 또는 다수)",
    "data": {} // CRITICAL_ALERT, STATE_REFRESH용 추가 데이터
  },
  "last_error": "string | null"
}
```

**참고:**
- SQS는 사용하지 않음
- 모든 이벤트는 Outbox 테이블에 기록되고 push-worker가 폴링하여 처리
- status-index GSI를 통해 PENDING/RETRY 이벤트를 효율적으로 조회
