# inference_batch Pod 문서

## 1. Pod 개요

- Pod 이름: `inference-batch`
- 담당 도메인: 배치 추론 파이프라인
- 배포 환경: AWS EKS (CronJob)
- 주요 역할:
  - Silver 이벤트 Parquet를 읽어 일 단위 feature 생성
  - 최근 윈도우 feature를 기반으로 상태 추론 실행
  - `state_out.csv`/`baseline.parquet`를 S3에 저장
  - downstream(`inference_service`)가 읽을 수 있는 결과 산출

## 2. 담당 기능

### 2.1 처리 기능
- S3 silver 데이터(`S3_SILVER_URI`) 로드
- 일별 feature 생성 및 `S3_DAILY_FEATURE_URI` 적재
- 최근 lookback feature를 사용해 모델 추론 수행
- 추론 결과를 `S3_OUTPUT_URI/dt=YYYY-MM-DD/state_out.csv`에 저장
- baseline 결과를 `S3_BASELINE_URI`에 저장

### 2.2 제외 기능
- 사용자 대상 실시간 API 제공
- FCM 푸시 발송
- DynamoDB 직접 업데이트
- Outbox 이벤트 처리

## 3. API Endpoints

| Method | Endpoint | 설명 |
|--------|----------|------|
| N/A | N/A | CronJob 기반 배치 실행(`python src/runtime/batch_runner.py`) |

## 4. 데이터 흐름

1. EKS CronJob가 매일 스케줄에 맞춰 `inference-batch` 실행
2. Pod가 S3 silver 이벤트를 조회하여 당일 feature 생성
3. 최근 lookback 기간 feature를 로드해 모델 추론 수행
4. 결과를 S3 `ml/outputs/dt=YYYY-MM-DD/state_out.csv`에 저장
5. 이후 `inference_service`가 해당 파일을 읽어 DynamoDB 상태를 동기화

## 5. 사용 인프라

- EKS `CronJob`: `services/inference_batch/deploy/k8s/cronjob.yaml`
- ServiceAccount(IRSA): `inference-batch-sa`
- ConfigMap: `inference-batch-config` (S3 URI, 모델 경로)
- S3:
  - 입력: silver events
  - 출력: daily-feature, baseline, state_out
- CloudWatch Logs: CronJob 실행 로그

## 6. 이벤트 처리 방식

- 본 Pod는 Outbox를 소비/생성하지 않음
- 이벤트 기반 fanout은 `inference_service` + `push_worker`가 담당
- 배치 실패 시 K8s `restartPolicy: OnFailure`로 재시도

## 7. 장애 대응 전략

- 단일 책임 유지: 배치 산출물 생성만 수행
- 입력 누락/파싱 실패 row는 건너뛰고 로그 기록(전체 파이프라인 중단 최소화)
- Job 실패 시 재기동과 이력 제한(`failedJobsHistoryLimit`)으로 운영 관리
- 중복 알림 이슈는 이 Pod가 아닌 downstream Outbox/Worker 계층에서 제어

## 8. 확장 전략

- 데이터량 증가 시 CronJob 리소스 상향(CPU/Memory) 및 병렬 배치 분할
- 모델 교체 시 이미지 태그 단위 Blue/Green 배포 가능
- S3 파티션 구조(`dt=...`) 기반으로 재처리/백필 범위 확장 용이
