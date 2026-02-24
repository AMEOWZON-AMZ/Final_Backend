# 추론 서비스 실행 가이드

## 1. 목적
이 서비스는 S3의 일일 추론 결과로부터 DynamoDB 상태를 업데이트하고 위급 이벤트를 처리합니다.

주요 목표:
- S3 `state_out.csv`에서 일일 상태 동기화
- API를 통한 위급 이벤트 처리
- ECR 이미지를 사용하여 EKS에 배포

---

## 2. 현재 아키텍처

### 2.1 일일 상태 (배치)
- 실행기: Kubernetes CronJob `daily-status-sync`
- 스케줄: 매일 06:00 (`Asia/Seoul`)
- 명령어:
  - `python -m services.inference_service.app.jobs.daily_status_sync_job`
- S3 입력 경로:
  - `s3://nyang-ml-apne2-dev/ml/outputs/dt=YYYY-MM-DD/state_out.csv`
- 날짜 규칙:
  - 기본적으로 전날 폴더를 읽음

### 2.2 위급 이벤트 (API)
- 엔드포인트: `POST /events/critical`
- 동작: 사용자 상태/위급 스냅샷 업데이트 및 위급 에이전트 이벤트 등록

### 2.3 레거시 일일 엔드포인트
- `POST /events/daily-status` 비활성화됨 (주석 처리)
- 일일 상태 업데이트는 CronJob 플로우로 수행됨

### 2.4 STATE_REFRESH 이벤트
- 일일 상태 동기화 완료 후 자동 생성
- 목적: 모바일 앱에 사용자 상태를 실시간으로 새로고침하도록 알림
- 대상 사용자:
  - CSV에서 상태가 변경된 사용자
  - 상태가 변경된 사용자의 친구
- 이벤트 타입: `STATE_REFRESH`
- 전달 방식: FCM을 통한 데이터 전용 푸시 (시각적 알림 없음)
- 저장소: OutboxEvents 테이블, push-worker에 의해 처리됨
- 페이로드 구조:
  ```json
  {
    "to_user_id": "user_id",
    "data": {
      "event_type": "STATE_REFRESH",
      "refresh": "1",
      "source": "DAILY_STATUS_SYNC",
      "target_date": "YYYY-MM-DD",
      "updated_at": "timestamp"
    }
  }
  ```

---

## 3. 코드 변경 사항 요약

### 3.1 서비스 로직
파일: `services/inference_service/app/services/inference_event_service.py`

구현 내용:
- `sync_daily_status_from_s3(target_date: str | None)` 추가
- CSV 필드 매핑:
  - `uuid -> user_id`
  - `cat_state -> daily_status`
  - `date -> inference_at`
- 필수 CSV 컬럼:
  - `uuid`, `date`, `cat_state`
- 행 처리:
  - 각 행마다 기존 `handle_daily_status()` 재사용
- 누락된 파일 처리:
  - `NoSuchKey/404/NotFound`의 경우 `SKIPPED` 반환하고 기존 DB 상태 유지
- STATE_REFRESH 이벤트 생성:
  - 메서드: `_enqueue_state_refresh_events(target_user_ids, target_date)`
  - 상태 변경의 영향을 받는 모든 사용자 수집 (본인 + 친구)
  - OutboxEvents에서 사용자당 1개의 STATE_REFRESH 이벤트 생성
  - 등록된 이벤트 수 반환
  - 이벤트 ID 형식: `STATE_REFRESH#{date}#{user_id}#{random}`
  - 이벤트는 데이터 전용 (시각적 푸시 알림 없음)

### 3.2 라우트
파일: `services/inference_service/app/routes/inference.py`

구현 내용:
- 레거시 `/events/daily-status` 비활성화
- 수동 트리거 엔드포인트 추가:
  - `POST /jobs/daily-status-sync?target_date=YYYY-MM-DD`

### 3.3 배치 진입점
파일: `services/inference_service/app/jobs/daily_status_sync_job.py`

구현 내용:
- CronJob 실행용 `main()` 추가
- 성공 시 종료 코드 `0`, 실패 시 `1`

### 3.4 설정
파일: `services/inference_service/app/core/config.py`

추가된 환경 변수:
- `DAILY_STATUS_SYNC_ENABLED`
- `DAILY_STATUS_S3_BUCKET`
- `DAILY_STATUS_S3_PREFIX`
- `DAILY_STATUS_SYNC_TIMEZONE`
- `DAILY_STATUS_SYNC_HOUR`

기본 접두사:
- `ml/outputs`

---

## 4. Kubernetes 리소스

### 4.1 ConfigMap
파일: `services/inference_service/deploy/k8s/configMap.yaml`

주요 값:
- `DAILY_STATUS_SYNC_ENABLED: "false"`
  - API 포드 내에서 중복 스케줄링 방지
- `DAILY_STATUS_S3_BUCKET: "nyang-ml-apne2-dev"`
- `DAILY_STATUS_S3_PREFIX: "ml/outputs"`
- `DAILY_STATUS_SYNC_TIMEZONE: "Asia/Seoul"`
- `DAILY_STATUS_SYNC_HOUR: "6"`

### 4.2 Deployment
파일: `services/inference_service/deploy/k8s/deployment.yaml`

현재 이미지:
- `715428147916.dkr.ecr.ap-northeast-2.amazonaws.com/inference-service:0.7`

### 4.3 CronJob
파일: `services/inference_service/deploy/k8s/cronjob-daily-status-sync.yaml`

주요 설정:
- `schedule: "0 6 * * *"`
- `timeZone: "Asia/Seoul"`
- `concurrencyPolicy: Forbid`
- `restartPolicy: OnFailure`

현재 이미지:
- `715428147916.dkr.ecr.ap-northeast-2.amazonaws.com/inference-service:0.7`

---

## 5. 배포 절차

### 5.1 코드 변경 시
1. 이미지 태그 증가 (예: `0.8`)
2. 이미지 빌드 및 푸시
3. Deployment/CronJob 이미지 태그 업데이트
4. 매니페스트 적용
5. 롤아웃 확인

예시:
```bash
docker build -f services/inference_service/Dockerfile -t 715428147916.dkr.ecr.ap-northeast-2.amazonaws.com/inference-service:0.8 .
docker push 715428147916.dkr.ecr.ap-northeast-2.amazonaws.com/inference-service:0.8

kubectl apply -f services/inference_service/deploy/k8s/deployment.yaml
kubectl apply -f services/inference_service/deploy/k8s/cronjob-daily-status-sync.yaml
kubectl rollout status deployment/inference-service -n default --timeout=240s
```

### 5.2 YAML만 변경될 때
이미지 재빌드는 필요 없습니다.

예시:
```bash
kubectl apply -f services/inference_service/deploy/k8s/configMap.yaml
```

Deployment 포드가 새 환경 변수를 선택해야 할 경우:
```bash
kubectl rollout restart deployment/inference-service -n default
kubectl rollout status deployment/inference-service -n default --timeout=240s
```

---

## 6. 테스트 절차

### 6.1 수동 CronJob 실행
```bash
kubectl create job --from=cronjob/daily-status-sync daily-status-sync-manual-001 -n default
kubectl get job -n default daily-status-sync-manual-001 -o wide
kubectl logs -n default job/daily-status-sync-manual-001 --tail=200
```

### 6.2 수동 API 실행
Swagger 또는 curl 사용:
- `POST /jobs/daily-status-sync`
- 쿼리 파라미터: `target_date=YYYY-MM-DD`

예시:
```bash
curl -X POST "http://127.0.0.1:8003/jobs/daily-status-sync?target_date=2026-02-20"
```

---

## 7. 문제 해결

### 7.1 AccessDenied (`s3:ListBucket`)
증상:
- `GetObject`가 `s3:ListBucket` 권한 오류로 실패

확인 방법:
```bash
kubectl get sa inference-service-sa -n default -o yaml
```

필요한 권한 예시:
- `s3:ListBucket` on `arn:aws:s3:::nyang-ml-apne2-dev`
- `s3:GetObject` on `arn:aws:s3:::nyang-ml-apne2-dev/ml/outputs/*`

### 7.2 NoSuchKey
증상:
- `state_out.csv` 키가 존재하지 않음

의미:
- 권한은 있지만 대상 날짜 파일이 누락됨

현재 동작:
- `SKIPPED(daily_status_file_not_found)` 반환
- DB의 이전 상태 유지

### 7.3 접두사 불일치
문제:
- 코드/설정/IAM 정책 간에 접두사가 다름

예상 접두사:
- `ml/outputs`

실시간 값 확인:
```bash
kubectl get configmap inference-config -n default -o jsonpath="{.data.DAILY_STATUS_S3_PREFIX}"
```

---

## 8. 로컬 실행

환경 파일:
- `services/inference_service/.env`

서버 실행:
```bash
uvicorn services.inference_service.app.main:app --reload --port 8003
```

Swagger:
- `http://127.0.0.1:8003/docs`

주의:
- 로컬 실행은 EKS IRSA 역할이 아닌 로컬 AWS 자격증명을 사용합니다

---

## 9. 현재 런타임 상태

- 일일 상태 소스: CronJob을 통한 S3 CSV
- 접두사: `ml/outputs`
- 누락된 파일 처리: 스킵, DB 덮어쓰기 없음
- 현재 이미지: `inference-service:0.7`
- Deployment과 CronJob 모두 `0.7` 사용

---

## 10. 권장 다음 단계

1. 각 배포 후 1회 수동 CronJob 테스트 실행
2. CronJob 실패에 대한 알림 추가 (CloudWatch/Prometheus)
3. 선택적으로 `target_date` 인수 자동화를 통한 명시적 재처리 플로우 추가
