# Vibe Coding Constraints (Final)


## Goal
- Implement Message/Heart + Push with:
- msg-service (FastAPI)
- DynamoDB storage
- OutboxEvents for durability
- Optional SQS for delivery
- push-worker sends push via FCM


## Non-negotiables
1) Writes first: message/heart must be persisted to DynamoDB before any push is attempted.
2) Push is async: msg-service MUST NOT call FCM directly.
3) Friend-only: sender -> receiver must be an ACCEPTED friend.
4) SQS does NOT display notifications; it only carries a “send push” job.
5) SQS payload is minimal (no message content). DB is source of truth.
6) **Audit is mandatory and minimal**: write to `AuditEvents` with
- `type(MESSAGE|HEART)`, `sender_id`, `receiver_id`, `ref_id`, `created_at`.
7) **TTL policy**: `AuditEvents.expires_at` MUST be set (default 90 days) and auto-expire.
8) **No sent-box**: Do NOT implement sent message/heart APIs or UI.
9) Security: No hard-coded AWS credentials. Use role-based auth (IRSA preferred) + env vars.
10) Time: All timestamps are UTC ISO-8601 with `Z`.
11) Code quality: Copy-paste runnable, list required env vars, minimal setup notes.


## Data Access Patterns
- Inbox: query by `receiver_id`, newest first
- Hearts received: query by `receiver_id`, newest first
- Token lookup: get by `user_id`
- Friend check: get by `(user_id, friend_id)`
- Outbox: query by `status=PENDING`
- Audit: query by `date_bucket` + time range


## API Endpoints (minimum)
- POST /messages
- GET /messages/inbox
- POST /hearts
- POST /device-token
- (optional) GET /hearts/received


## Worker Behavior
- Consume SQS OR poll OutboxEvents(PENDING).
- Lookup receiver token → call FCM → update Outbox status (SENT/FAILED).
- Retry with backoff; if no token, skip push but mark SENT (or NO_TOKEN).


## SQS Job Schema
{
"event_type": "MESSAGE|HEART",
"from_user_id": "string",
"to_user_id": "string",
"ref_id": "string",
"created_at": "YYYY-MM-DDTHH:MM:SSZ"
}


## Output Standards
- Provide file structure suggestions.
- Prefer simple, explicit code.
- Explain *why* (durability, async push, minimal payload).
- Do not introduce new services without explicit need.