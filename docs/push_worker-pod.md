# push_worker Pod 문서

## 1. Pod 개요

- Pod 이름: `push-worker`
- 담당 도메인: 알림 비동기 발송 워커
- 배포 환경: AWS EKS
- 주요 역할:
  - Outbox(`PENDING/RETRY`) 이벤트 소비
  - FCM 발송 및 결과 상태 업데이트
  - 재시도/백오프/최종 실패 처리

## 2. 담당 기능

### 2.1 처리 기능
- Outbox polling (`query_ready`) + 이벤트 선점(`try_mark_processing`)
- 필요 시 SQS 소비(`SQS_QUEUE_URL` 설정 시)
- 이벤트 타입별 FCM 전송(`PUSH_SEND`, `CRITICAL_ALERT`, `STATE_REFRESH`, 친구 이벤트)
- 발송 성공: `SENT`
- 발송 실패: `RETRY` 또는 `FAILED`

### 2.2 제외 기능
- 메시지/하트 원본 데이터 생성
- 사용자 상태 계산/추론
- 이미지 유효성 검증
- 클라이언트 동기 API 제공

## 3. API Endpoints

| Method | Endpoint | 설명 |
|--------|----------|------|
| N/A | N/A | 내부 워커 루프(`run_loop`)로 동작 |

## 4. 데이터 흐름

1. `msg_service`/`inference_service`가 Outbox에 이벤트 생성
2. `push_worker`가 `status-index`로 `PENDING/RETRY` 조회
3. 조건부 업데이트로 `PROCESSING` 선점(동시 처리 충돌 방지)
4. `DeviceTokens` 조회 후 FCM v1 API 호출
5. 성공 시 `SENT`, 실패 시 `RETRY(next_retry_at)`
6. 최대 시도 초과 시 `FAILED`

## 5. 사용 인프라

- EKS Deployment: `deployment-worker.yaml`
- ServiceAccount + IRSA: `msg-service-sa`
- ConfigMap/Secret: `msg-config`, `msg-secret`
- DynamoDB: `OutboxEvents`, `DeviceTokens`, `user_friends`
- 선택 리소스: SQS (configured 시 우선 소비)
- 외부 연동: Firebase FCM v1 API
- CloudWatch Logs

## 6. 이벤트 처리 방식

- Outbox Pattern 핵심 소비자
- 재시도 정책:
  - 최대 시도: 8회
  - Backoff: `min(5 * 2^(attempt-1), 300)` 초
- 중복 방지 전략:
  - `try_mark_processing` 조건식으로 단일 소비 보장
  - `mark_sent`는 `PROCESSING` 상태에서만 성공
- 실패 누적 시 `FAILED`로 종료(사일런트 루프 방지)

## 7. 장애 대응 전략

- 멱등성: 상태 전이 조건식(PENDING/RETRY -> PROCESSING -> SENT/RETRY/FAILED)
- 토큰 누락/FCM 오류 시 즉시 실패하지 않고 재시도 큐 전환
- 부분 실패(여러 수신자 중 일부 실패)도 오류 요약 저장 후 재시도
- 중복 알람 방지 요구사항을 Outbox 상태머신으로 충족

## 8. 확장 전략

- 워커 복제 확장 가능(선점 로직 기반 경쟁 소비)
- Outbox 적체 시 워커 replicas 확장으로 처리량 증가
- Blue/Green 배포 시 신규 워커 버전을 점진 전환
- 장기적으로 DLQ/SQS 전용 모드 강화 시 운영 안정성 향상
