# Inference Service Runbook

## 1. Purpose
This service updates DynamoDB state from S3 daily inference outputs and handles critical events.

Primary goals:
- Daily status sync from S3 `state_out.csv`
- Critical event handling via API
- Deployment on EKS using ECR images

---

## 2. Current Architecture

### 2.1 Daily Status (Batch)
- Executor: Kubernetes CronJob `daily-status-sync`
- Schedule: Every day at 06:00 (`Asia/Seoul`)
- Command:
  - `python -m services.inference_service.app.jobs.daily_status_sync_job`
- S3 input path:
  - `s3://nyang-ml-apne2-dev/ml/outputs/dt=YYYY-MM-DD/state_out.csv`
- Date rule:
  - Reads the previous day folder by default

### 2.2 Critical Event (API)
- Endpoint: `POST /events/critical`
- Behavior: updates user status / critical snapshot and enqueues critical agent event

### 2.3 Legacy Daily Endpoint
- `POST /events/daily-status` is disabled (commented)
- Daily status updates are done by CronJob flow

---

## 3. Code Changes Summary

### 3.1 Service Logic
File: `services/inference_service/app/services/inference_event_service.py`

Implemented:
- Added `sync_daily_status_from_s3(target_date: str | None)`
- CSV field mapping:
  - `uuid -> user_id`
  - `cat_state -> daily_status`
  - `date -> inference_at`
- Required CSV columns:
  - `uuid`, `date`, `cat_state`
- Row processing:
  - Reuses existing `handle_daily_status()` per row
- Missing file handling:
  - For `NoSuchKey/404/NotFound`, return `SKIPPED` and keep existing DB state

### 3.2 Routes
File: `services/inference_service/app/routes/inference.py`

Implemented:
- Disabled legacy `/events/daily-status`
- Added manual trigger endpoint:
  - `POST /jobs/daily-status-sync?target_date=YYYY-MM-DD`

### 3.3 Batch Entrypoint
File: `services/inference_service/app/jobs/daily_status_sync_job.py`

Implemented:
- Added `main()` for CronJob execution
- Exit code `0` on success, `1` on failure

### 3.4 Config
File: `services/inference_service/app/core/config.py`

Added env variables:
- `DAILY_STATUS_SYNC_ENABLED`
- `DAILY_STATUS_S3_BUCKET`
- `DAILY_STATUS_S3_PREFIX`
- `DAILY_STATUS_SYNC_TIMEZONE`
- `DAILY_STATUS_SYNC_HOUR`

Default prefix:
- `ml/outputs`

---

## 4. Kubernetes Resources

### 4.1 ConfigMap
File: `services/inference_service/deploy/k8s/configMap.yaml`

Key values:
- `DAILY_STATUS_SYNC_ENABLED: "false"`
  - Prevents duplicate scheduling inside API pods
- `DAILY_STATUS_S3_BUCKET: "nyang-ml-apne2-dev"`
- `DAILY_STATUS_S3_PREFIX: "ml/outputs"`
- `DAILY_STATUS_SYNC_TIMEZONE: "Asia/Seoul"`
- `DAILY_STATUS_SYNC_HOUR: "6"`

### 4.2 Deployment
File: `services/inference_service/deploy/k8s/deployment.yaml`

Current image:
- `715428147916.dkr.ecr.ap-northeast-2.amazonaws.com/inference-service:0.7`

### 4.3 CronJob
File: `services/inference_service/deploy/k8s/cronjob-daily-status-sync.yaml`

Key settings:
- `schedule: "0 6 * * *"`
- `timeZone: "Asia/Seoul"`
- `concurrencyPolicy: Forbid`
- `restartPolicy: OnFailure`

Current image:
- `715428147916.dkr.ecr.ap-northeast-2.amazonaws.com/inference-service:0.7`

---

## 5. Deployment Procedure

### 5.1 When Code Changes
1. Increase image tag (example: `0.8`)
2. Build and push image
3. Update Deployment/CronJob image tags
4. Apply manifests
5. Check rollout

Example:
```bash
docker build -f services/inference_service/Dockerfile -t 715428147916.dkr.ecr.ap-northeast-2.amazonaws.com/inference-service:0.8 .
docker push 715428147916.dkr.ecr.ap-northeast-2.amazonaws.com/inference-service:0.8

kubectl apply -f services/inference_service/deploy/k8s/deployment.yaml
kubectl apply -f services/inference_service/deploy/k8s/cronjob-daily-status-sync.yaml
kubectl rollout status deployment/inference-service -n default --timeout=240s
```

### 5.2 When Only YAML Changes
No image rebuild is required.

Example:
```bash
kubectl apply -f services/inference_service/deploy/k8s/configMap.yaml
```

If Deployment pods must pick new env values:
```bash
kubectl rollout restart deployment/inference-service -n default
kubectl rollout status deployment/inference-service -n default --timeout=240s
```

---

## 6. Test Procedure

### 6.1 Manual CronJob Run
```bash
kubectl create job --from=cronjob/daily-status-sync daily-status-sync-manual-001 -n default
kubectl get job -n default daily-status-sync-manual-001 -o wide
kubectl logs -n default job/daily-status-sync-manual-001 --tail=200
```

### 6.2 Manual API Run
Use Swagger or curl:
- `POST /jobs/daily-status-sync`
- Query param: `target_date=YYYY-MM-DD`

Example:
```bash
curl -X POST "http://127.0.0.1:8003/jobs/daily-status-sync?target_date=2026-02-20"
```

---

## 7. Troubleshooting

### 7.1 AccessDenied (`s3:ListBucket`)
Symptom:
- `GetObject` fails with `s3:ListBucket` permission error

Checks:
```bash
kubectl get sa inference-service-sa -n default -o yaml
```

Required permissions example:
- `s3:ListBucket` on `arn:aws:s3:::nyang-ml-apne2-dev`
- `s3:GetObject` on `arn:aws:s3:::nyang-ml-apne2-dev/ml/outputs/*`

### 7.2 NoSuchKey
Symptom:
- `state_out.csv` key does not exist

Meaning:
- Permission is OK, but the target date file is missing

Current behavior:
- Returns `SKIPPED(daily_status_file_not_found)`
- Keeps previous status in DB

### 7.3 Prefix Mismatch
Problem:
- Prefix differs across code/config/IAM policy

Expected prefix:
- `ml/outputs`

Check live value:
```bash
kubectl get configmap inference-config -n default -o jsonpath="{.data.DAILY_STATUS_S3_PREFIX}"
```

---

## 8. Local Run

Env file:
- `services/inference_service/.env`

Run server:
```bash
uvicorn services.inference_service.app.main:app --reload --port 8003
```

Swagger:
- `http://127.0.0.1:8003/docs`

Note:
- Local run uses local AWS credentials, not EKS IRSA role

---

## 9. Current Runtime Status

- Daily status source: S3 CSV via CronJob
- Prefix: `ml/outputs`
- Missing file handling: skip, no DB overwrite
- Current image: `inference-service:0.7`
- Deployment and CronJob both use `0.7`

---

## 10. Recommended Next Steps

1. Run one manual CronJob test after each deployment
2. Add alerting for CronJob failures (CloudWatch/Prometheus)
3. Optionally add explicit reprocessing flow with `target_date` argument automation
