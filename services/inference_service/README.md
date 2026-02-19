# inference-service

## Overview
This service receives inference events and updates DynamoDB state.

- `POST /events/daily-status`
  - Updates `user_status.current_daily_status`
  - Fanout updates `user_friends.daily_status` via GSI
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
