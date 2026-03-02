# msg_service Pod 문서

## 1. Pod 개요

- Pod 이름: `msg-service`
- 담당 도메인: 메시지/하트/디바이스 토큰 API
- 배포 환경: AWS EKS
- 주요 역할:
  - 메시지/하트 생성 및 조회 API 제공
  - Device Token 등록 API 제공
  - Outbox 이벤트 생성(푸시 비동기 처리용)

## 2. 담당 기능

### 2.1 처리 기능
- `POST /messages`, `GET /messages/inbox`
- `POST /hearts`, `GET /hearts/received`
- `POST /device-token`
- 메시지 생성 시 Message + Outbox 동시 저장
- 하트 생성 시 Heart 저장 + Outbox 적재 + Audit 기록

### 2.2 제외 기능
- FCM 직접 발송
- Outbox 재시도/백오프 처리
- 위기 이벤트 상태 동기화
- 배치 추론 실행

## 3. API Endpoints

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/messages` | 메시지 생성 + Outbox 이벤트 생성 |
| GET | `/messages/inbox` | 받은 메시지 조회 |
| POST | `/hearts` | 하트 생성 + Outbox/Audit 적재 |
| GET | `/hearts/received` | 받은 하트 조회 |
| POST | `/device-token` | FCM 디바이스 토큰 등록/갱신 |
| GET | `/health` | 헬스체크 |

## 4. 데이터 흐름

1. User App가 `msg_service` API 호출
2. DynamoDB에 메시지/하트 원본 데이터 저장
3. 동일 요청 흐름에서 `OutboxEvents`에 `PENDING` 이벤트 적재
4. `push_worker`가 Outbox를 비동기 소비하여 FCM 발송
5. 발송 결과에 따라 `SENT/RETRY/FAILED`로 상태 전이

## 5. 사용 인프라

- EKS Deployment: `deployment-msg.yaml`
- EKS Service(LoadBalancer): `service.yaml`
- ServiceAccount + IRSA: `msg-service-sa`
- ConfigMap: `msg-config`
- Secret: `msg-secret`
- DynamoDB: `Messages`, `Hearts`, `DeviceTokens`, `OutboxEvents`, `AuditEvents`, `user_friends`
- 선택적 SQS URL 설정(`SQS_QUEUE_URL`)
- CloudWatch Logs

## 6. 이벤트 처리 방식

- Outbox Pattern 적용:
  - 메시지: 본문 저장과 Outbox 적재를 함께 처리
  - 하트: Heart/Audit/Outbox를 서비스 레이어에서 일관 처리
- 이벤트 타입: `PUSH_SEND` 중심
- 중복 방지:
  - 발송은 Worker 단일 흐름에서 수행
  - API Pod는 이벤트 생성까지만 담당
- Backoff/Retry는 `push_worker`로 위임

## 7. 장애 대응 전략

- 원본 데이터 저장과 발송 분리로 사용자 요청 지연 최소화
- 토큰 미존재/FCM 실패는 Worker 재시도로 완충
- 알림 중복 발송 방지는 Outbox 상태 전이 조건식으로 보장
- AuditEvents 기록으로 사후 추적성 확보

## 8. 확장 전략

- API Pod 수평 확장(HPA) 용이
- 메시지 트래픽 증가 시 Worker 별도 확장 가능
- Blue/Green 배포 시 `msg-service`와 `push-worker`를 독립 전환
- DynamoDB 온디맨드/프로비저닝 조정으로 쓰기 부하 대응
