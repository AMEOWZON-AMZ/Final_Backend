# inference_service Pod 문서

## 1. Pod 개요

- Pod 이름: `inference-service`
- 담당 도메인: 상태 동기화/위기 이벤트 처리
- 배포 환경: AWS EKS
- 주요 역할:
  - S3의 일별 추론 결과(`state_out.csv`)를 DynamoDB 상태로 동기화
  - 사용자/친구 관계의 상태 fanout 업데이트
  - `STATE_REFRESH` Outbox 이벤트 생성
  - 위기 이벤트(`critical`)를 1회성 트랜잭션으로 반영

## 2. 담당 기능

### 2.1 처리 기능
- `POST /jobs/daily-status-sync`: 대상 날짜 S3 결과를 읽어 상태 반영
- `POST /events/critical`: 사용자 CRITICAL 상태 전환 및 연락처 snapshot 저장
- 친구 테이블 fanout 업데이트
- Outbox `STATE_REFRESH` 이벤트 적재

### 2.2 제외 기능
- FCM 직접 발송
- Outbox 소비/재시도 실행
- 메시지/하트 CRUD
- 이미지 검증 추론

## 3. API Endpoints

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/jobs/daily-status-sync` | S3 CSV 기반 일별 상태 동기화 |
| POST | `/events/critical` | 위기 상태 반영(1회성 처리) |
| GET | `/health` | 헬스체크 |

## 4. 데이터 흐름

1. `inference_batch`가 S3에 `state_out.csv` 저장
2. `inference_service`가 파일을 읽어 `user_status` 업데이트
3. 친구 관계(`user_friends`)를 조회해 반영 대상 fanout 업데이트
4. 반영 대상 사용자별 `OutboxEvents(event_type=STATE_REFRESH)` 생성
5. `push_worker`가 Outbox를 읽어 FCM data 메시지 발송
6. `POST /events/critical` 호출 시 `critical_contacts` snapshot 저장 + SQS 이벤트 발행(critical agent)

## 5. 사용 인프라

- EKS Deployment: `services/inference_service/deploy/k8s/deployment.yaml`
- EKS Service(LoadBalancer): `services/inference_service/deploy/k8s/service.yaml`
- EKS CronJob: `daily-status-sync` (`06:00 Asia/Seoul`)
- ServiceAccount + IRSA: `inference-service-sa`
- ConfigMap: `inference-config`
- DynamoDB: `user_status`, `user_friends`, `critical_contacts`, `OutboxEvents`
- S3: `nyang-ml-apne2-dev/ml/outputs/.../state_out.csv`
- SQS: critical agent 이벤트 연계
- CloudWatch Logs

## 6. 이벤트 처리 방식

- Outbox Pattern 적용: 상태 갱신 알림은 `OutboxEvents`에 `PENDING` 저장
- 중복 방지:
  - 위기 상태는 DynamoDB 트랜잭션 조건식으로 이미 CRITICAL이면 `SKIPPED`
  - 파일 미존재 시 안전하게 skip 처리
- 재시도/Backoff:
  - Outbox 재시도는 `push_worker`에서 담당
  - 동기화 CronJob은 `backoffLimit` + `OnFailure`로 재시도

## 7. 장애 대응 전략

- 트랜잭션 조건부 업데이트로 위기 이벤트 멱등성 보장
- CSV 컬럼 검증/row 단위 오류 카운팅으로 부분 실패 격리
- 파일 없음(`NoSuchKey`)은 장애가 아닌 skip 결과로 반환
- 알림 중복 발송은 Outbox 소비 계층(`push_worker`)의 상태 전이 제약으로 제어

## 8. 확장 전략

- HPA 적용 가능한 Stateless API 구조
- CronJob과 API Pod를 분리해 독립 스케일링 가능
- Blue/Green 배포 시 이미지 태그 전환으로 안정 롤아웃
- Outbox 생성량 증가 시 Worker 확장으로 비동기 처리량 확보
