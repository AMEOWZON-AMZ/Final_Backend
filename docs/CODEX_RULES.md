# CODEX_RULES (Must Follow)

## 0) Scope
You are coding the Message/Heart + Push system for:
- msg-service (FastAPI)
- DynamoDB storage
- OutboxEvents for durability
- Optional SQS for delivery
- push-worker sends push via FCM

## 1) Non-negotiables
1) Writes first: message/heart must be persisted to DynamoDB before any push is attempted.
2) Push is async: msg-service must NOT call FCM directly.
3) Friend-only: sender -> receiver must be an ACCEPTED friend (server-side check).
4) SQS does NOT display notifications. SQS only carries a “send push” job.
5) SQS payload must be minimal (no message content). DB is source of truth.
6) No hard-coded AWS credentials. Use role-based auth (IRSA preferred) and env vars.
7) All timestamps must be UTC ISO-8601 with Z.
8) IDs must be stable strings (ULID/UUID). Sort keys use created_at#id.
9) Code must be copy-paste runnable with clear env vars and minimal setup notes.

## 2) Data Access Patterns (must stay efficient)
- Inbox: query by receiver_id, newest first
- Hearts received: query by receiver_id, newest first
- Token lookup: get by user_id
- Friend check: get by (user_id, friend_id)
- Outbox: query by status=PENDING, process, then mark SENT/FAILED

## 3) API endpoints (minimum)
- POST /messages
- GET  /messages/inbox
- POST /hearts
- POST /device-token
Optional:
- GET /hearts/received
- GET /messages/sent (requires GSI)

## 4) Worker behavior
- Consume jobs from SQS OR poll OutboxEvents(PENDING).
- For each job:
  1) lookup receiver token in DeviceTokens
  2) call FCM
  3) update OutboxEvents status: SENT or FAILED
  4) implement retry with backoff and max retries
- If receiver has no token: skip push; still mark job as SENT (or a dedicated NO_TOKEN state).

## 5) SQS Job Schema
{
  "event_type": "MESSAGE|HEART",
  "from_user_id": "string",
  "to_user_id": "string",
  "ref_id": "string",
  "created_at": "YYYY-MM-DDTHH:MM:SSZ"
}

## 6) Output standards
- Provide file structure suggestions when generating code.
- Prefer simple, explicit code over clever abstractions.
- Include comments explaining why (durability, async push, minimal payload).
- Do not introduce new services/requirements without explicit need.
