# Message Service

This service implements message/heart persistence with durable outbox and async push delivery.

Rules (from CODEX_RULES.md):
- Writes first (DynamoDB) before any push attempt
- Push is async (worker only)
- Friend-only (ACCEPTED) check
- SQS payload is minimal (no message content)
- Timestamps are UTC ISO-8601 with Z
- IDs are stable strings (UUID)

## Structure
- `apps/msg_service`: FastAPI API
- `apps/push_worker`: worker that sends push via FCM
- `shared`: common config/util/ddb/sqs/models
- `deploy/k8s`: manifests
- `docs`: specs

## Env vars (minimum)
- `AWS_REGION`
- `DDB_MESSAGES_TABLE`
- `DDB_HEARTS_TABLE`
- `DDB_OUTBOX_TABLE`
- `DDB_DEVICE_TOKENS_TABLE`
- `DDB_FRIENDS_TABLE`
- `DDB_AUDIT_TABLE`
- `SQS_QUEUE_URL` (optional)
- `FCM_SERVER_KEY` (worker)
- `AUDIT_TTL_DAYS` (default 7)

## DynamoDB table keys
- Messages: `pk=RECEIVER#<to_user_id>`, `sk=<created_at>#<message_id>`
- Hearts: `pk=RECEIVER#<to_user_id>`, `sk=<created_at>#<heart_id>`
- DeviceTokens: `pk=USER#<user_id>`, `sk=TOKEN`
- Friends: `pk=USER#<user_id>`, `sk=FRIEND#<friend_id>`, `status=ACCEPTED`
- OutboxEvents: `pk=OUTBOX#<to_user_id>`, `sk=<created_at>#<ref_id>`, `status=PENDING|SENT|FAILED`
  - GSI `status-index` with partition key `status`
- AuditEvents: `pk=AUDIT#<to_user_id>`, `sk=<created_at>#<ref_id>`, `expires_at` (TTL)

## Dependencies
- `boto3` for DynamoDB/SQS
- `requests` for FCM (worker)

## Run (dev)
```bash
uvicorn services.message_service.apps.msg_service.main:app --reload --port 8080
```

## Worker (dev)
```bash
python -m services.message_service.apps.push_worker.main
```
