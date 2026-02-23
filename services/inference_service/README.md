# inference-service

## Overview
This service updates DynamoDB state from inference outputs.

- `POST /jobs/daily-status-sync`
  - Reads `s3://<bucket>/<prefix>/dt=YYYY-MM-DD/state_out.csv`
  - Required CSV columns: `uuid`, `date`, `cat_state`
  - Maps `uuid -> user_id`, `cat_state -> daily_status`
  - Updates `user_status.current_daily_status`
  - Fanout updates `user_friends.daily_status` via GSI
- Automatic scheduler
  - Runs every day at `DAILY_STATUS_SYNC_HOUR` (default `06:00`) in `DAILY_STATUS_SYNC_TIMEZONE`
  - Loads previous day folder (`dt=YYYY-MM-DD`)
- `POST /events/critical`
  - Marks user as critical (one-time)
  - Writes `critical_contacts` snapshot
  - Writes one outbox event (`CRITICAL#<critical_user_id>`)

## Local setup
1. Create env file:
   - Copy `.env.example` to `.env`
2. Install deps:
   - `pip install -r services/inference_service/requirements.txt`
3. Check DynamoDB connectivity:
   - `python services/inference_service/scripts/check_ddb_connection.py`
4. Run API:
   - `uvicorn services.inference_service.app.main:app --reload --port 8003`

### Sync env vars
- `DAILY_STATUS_SYNC_ENABLED` (default: `true`)
- `DAILY_STATUS_S3_BUCKET` (default: `nyang-ml-apne2-dev`)
- `DAILY_STATUS_S3_PREFIX` (default: `outputs`)
- `DAILY_STATUS_SYNC_TIMEZONE` (default: `Asia/Seoul`)
- `DAILY_STATUS_SYNC_HOUR` (default: `6`)

## EKS manifests
`services/inference_service/deploy/k8s`

- `serviceAccount.yaml`
- `configMap.yaml`
- `deployment.yaml`
- `service.yaml`

Apply:

```bash
kubectl apply -f services/inference_service/deploy/k8s/serviceAccount.yaml
kubectl apply -f services/inference_service/deploy/k8s/configMap.yaml
kubectl apply -f services/inference_service/deploy/k8s/deployment.yaml
kubectl apply -f services/inference_service/deploy/k8s/service.yaml
```
