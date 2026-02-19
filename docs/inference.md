# Inference Status Service + Outbox Integration (Codex Prompt)

## Goal
Implement a FastAPI service ("inference-status-service") that:
1) Receives daily status callbacks (from SageMaker) and updates DynamoDB.
2) Receives critical events (from Lambda) and updates DynamoDB + writes push events to Outbox.
3) Reuses existing push-worker by only writing Outbox events (no direct FCM send in this service).

## Existing Tables
### user_friends (DynamoDB)
- PK: user_id (S)
- SK: friend_user_id (S)
- Columns include: daily_status, nickname, profile_image_url, ... updated_at
- For mutual friends: (A,B) and (B,A) rows exist.

### Outbox (existing)
- Used by push-worker for push delivery (claim -> send -> update status with retry/backoff)

## New Tables
### user_status (DynamoDB)
- PK: user_id (S)
- Attributes:
  - current_daily_status (S) enum: HAPPY | SOSO | SAD | FAINT | NO_DATA
  - is_critical (BOOL)
  - critical_since (S, UTC ISO-8601)
  - updated_at (S, UTC ISO-8601)
  - last_inference_at (S, UTC ISO-8601, optional)

### critical_contacts (DynamoDB)
- PK: critical_user_id (S)
- SK: event_id (S) or event_time (S)
- Attributes:
  - critical_gps (MAP or STRING)
  - friends (LIST of { friend_user_id, friend_gps })
  - created_at (S, UTC ISO-8601)
  - ttl (N, epoch seconds) optional

## Indexes
### user_friends GSI1 (REQUIRED)
- GSI1PK: friend_user_id
- GSI1SK: user_id
Purpose: find all rows where friend_user_id = target_user_id for fanout updates.

## APIs
### POST /events/daily-status
Input JSON:
{
  "event_id": "string (optional)",
  "user_id": "string",
  "daily_status": "HAPPY|SOSO|SAD|FAINT|NO_DATA",
  "inference_at": "string (optional, ISO-8601 UTC)"
}

Rules:
- Read user_status for user_id.
- If is_critical == true AND daily_status == "NO_DATA": DO NOT UPDATE (keep previous).
- Else if daily_status == current_daily_status: DO NOT UPDATE.
- Else:
  - Update user_status.current_daily_status = daily_status, updated_at=now.
  - Fanout update user_friends rows where friend_user_id == user_id (via GSI1) set daily_status = new value, updated_at=now.

Note:
- If is_critical == false AND daily_status == "NO_DATA": store NO_DATA (and fanout if changed).

### POST /events/critical
Input JSON:
{
  "event_id": "string",
  "critical_user_id": "string",
  "critical_gps": { ... } or "string",
  "friends": [
    { "friend_user_id": "string", "friend_gps": { ... } or "string" }
  ],
  "occurred_at": "string (optional, ISO-8601 UTC)"
}

Rules:
- Mark user_status.is_critical = true (one-time). If already true, skip push/outbox.
- Save snapshot to critical_contacts.
- Write ONE outbox event that will notify ALL friends (once):
  - dedupe_key = "CRITICAL#{critical_user_id}"
  - payload includes critical_user_id and minimal info for push (title/body variables)
- The push-worker will expand to device tokens and send FCM.

## Outbox Event Contract (for push-worker)
Create outbox item like:
{
  "event_id": "...",
  "type": "CRITICAL_ALERT",
  "dedupe_key": "CRITICAL#<critical_user_id>",
  "status": "PENDING",
  "attempt_count": 0,
  "next_retry_at": "<now>",
  "payload": {
    "to_user_ids": ["friend1","friend2",...],
    "title": "위급 상태 감지",
    "body": "<nickname>님의 상태가 위급해요. 확인해주세요.",
    "criti
