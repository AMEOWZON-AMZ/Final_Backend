# 서비스 인벤토리(현행) 및 경계 재조정 제안

이 문서는 현재 코드 기준으로 **있는 그대로의 기능**을 정리하고,
`inference_service`, `message_service(API)`, `message_service(push worker)`, `vision_service`
4개 서비스의 책임 경계를 재정의하기 위한 초안이다.

## 1) 지금 기능(As-Is) 요약

### 1-1. inference_service
- 주요 역할
  - S3의 일일 추론 CSV(`state_out.csv`)를 읽어 사용자 상태를 갱신.
  - 임계 이벤트(critical) 수신 시 사용자 상태를 CRITICAL로 전환하고 스냅샷 저장.
  - 상태 변경 대상에게 `STATE_REFRESH` outbox 이벤트를 적재.
  - 임계 이벤트 발생 시 별도 에이전트 큐(`send_critical_agent_event`)로 메시지 전송.
- 동작 특성
  - 앱 시작 시 내장 스케줄러가 주기적으로 daily-status sync 실행.
  - `handle_daily_status`는 status 변경이 없으면 skip.
  - critical 처리 트랜잭션에서 outbox 적재 코드는 현재 비활성화(주석 처리).

### 1-2. message_service (msg API)
- 주요 역할
  - 메시지 작성/조회 API 제공.
  - 하트 작성/조회 API 제공.
  - 디바이스 토큰 등록 API 제공.
  - 메시지 생성 시 메시지 + outbox를 단일 트랜잭션으로 기록(비동기 푸시 전제).
- 동작 특성
  - 친구 검증 로직(`is_accepted`)은 코드상 존재하나 현재 전송 차단용으로는 비활성/완화 상태.
  - health endpoint 제공.

### 1-3. message_service (push worker)
- 주요 역할
  - SQS 우선 소비(설정 시), 없으면 outbox polling으로 이벤트 처리.
  - outbox 이벤트를 PROCESSING으로 claim 후 FCM 발송.
  - 성공 시 SENT, 실패 시 backoff 기반 RETRY/FAILED로 상태 전이.
- 동작 특성
  - 이벤트 payload에서 대상 사용자(`to_user_id`, `to_user_ids`)를 추출.
  - 이벤트 타입별(예: `CRITICAL_ALERT`) 예외 payload 포맷을 일부 허용.

### 1-4. vision_service
- 주요 역할
  - 이미지 업로드를 받아 CLIP 기반으로 “오늘의 토픽” 일치 여부 계산.
  - 토픽은 RDB(`DATABASE_URL`)에서 날짜 기준 1건 조회.
- 동작 특성
  - `/vision/validate` 단일 핵심 API + health endpoint.
  - 파일 타입/크기 검증, 점수 threshold 판정.

---

## 2) 서비스별 엔드포인트 목록

## 2-1. inference_service
- `GET /health/`
- `POST /jobs/daily-status-sync?target_date=YYYY-MM-DD`
- `POST /events/critical`

> 참고: `POST /events/daily-status`는 현재 주석 처리되어 비활성.

## 2-2. message_service (msg API)
- `GET /health/`
- `POST /messages`
- `GET /messages/inbox?to_user_id=<id>&limit=<n>`
- `POST /hearts`
- `GET /hearts/received?to_user_id=<id>&limit=<n>`
- `POST /device-token`

## 2-3. message_service (push worker)
- 외부 HTTP endpoint 없음(백그라운드 루프 워커)

## 2-4. vision_service
- `GET /health`
- `POST /vision/validate` (multipart: image file, optional `date`)

---

## 3) 서비스별 테이블/스토리지 사용 목록

## 3-1. inference_service
- DynamoDB
  - `DDB_USER_STATUS_TABLE`
  - `DDB_FRIENDS_TABLE` (+ GSI: `friend_user_id` 조회용)
  - `DDB_CRITICAL_CONTACTS_TABLE`
  - `DDB_OUTBOX_TABLE` (STATE_REFRESH 이벤트 적재)
- S3
  - `DAILY_STATUS_S3_BUCKET` / `DAILY_STATUS_S3_PREFIX`의 `state_out.csv`
- SQS/이벤트
  - `send_critical_agent_event`로 critical agent queue 전송

## 3-2. message_service (msg API)
- DynamoDB
  - `DDB_MESSAGES_TABLE`
  - `DDB_HEARTS_TABLE`
  - `DDB_DEVICE_TOKENS_TABLE`
  - `DDB_OUTBOX_TABLE`
  - `DDB_FRIENDS_TABLE`
  - (`DDB_AUDIT_TABLE` 환경변수 언급은 있으나 현재 코드 경로에서 핵심 write/read는 제한적)

## 3-3. message_service (push worker)
- DynamoDB
  - `DDB_OUTBOX_TABLE` (ready 조회/claim/상태전이)
  - `DDB_DEVICE_TOKENS_TABLE` (수신자 토큰 조회)
- SQS
  - `SQS_QUEUE_URL` (설정 시 우선 consume)
- 외부
  - FCM 전송

## 3-4. vision_service
- RDB (SQLAlchemy)
  - `DATABASE_URL`
  - `TOPIC_TABLE`, `TOPIC_TEXT_COLUMN`, `TOPIC_DATE_COLUMN`
- ML 모델
  - OpenCLIP model (설정 기반 로드)

---

## 4) 경계 재조정 제안(겹치는 책임은 한쪽으로 몰기)

현재 중복/모호 지점:
1. `inference_service`와 `message_service`가 모두 `DDB_OUTBOX_TABLE`에 이벤트를 기록함.
2. 푸시 전달의 최종 책임은 `message_service.push_worker`인데, 이벤트 스키마 일부가 서비스별로 느슨함.
3. `critical` 시나리오에서 “상태 갱신”과 “알림 fanout”이 부분적으로 분리되어 정책 소유권이 불명확함.

권장 경계(안):
- **inference_service = 상태 도메인의 단일 오너**
  - user_status / friend daily_status cache / critical snapshot까지 책임.
  - "누가 알림 받아야 하는지" 결정 가능한 이벤트만 발행(도메인 이벤트).
- **message_service API = 커뮤니케이션 도메인 오너**
  - 메시지/하트 생성, 토큰 관리, outbox 이벤트 스키마 관리.
- **message_service push worker = 전달(Delivery) 오너**
  - 발송 재시도/백오프/FCM 에러 정책의 단일 소유.
  - 이벤트 타입별 payload normalization을 여기로 집중.
- **vision_service = 추론 보조/검증 오너**
  - 이미지-토픽 검증만 담당, 메시징/상태 저장 책임 없음.

구체적으로 "하나로 몰기" 권장 항목:
- Outbox 쓰기 책임을 명확화:
  - A안) 모든 푸시 목적 이벤트는 `message_service` API를 통해서만 생성.
  - B안) cross-domain 이벤트는 허용하되, **공통 이벤트 계약(schema + version)** 을 강제.
- Critical 알림 경로 단순화:
  - 현재 `critical_agent_event`와 outbox 경로가 공존/변경 이력 있음.
  - 단기적으로는 한 경로를 "공식 경로"로 고정하고 나머지는 deprecated 처리.

---

## 5) 빠른 확정 체크리스트

- [ ] `DDB_OUTBOX_TABLE` 이벤트 스키마 소유 서비스 확정
- [ ] `CRITICAL` 알림 공식 전달 경로 1개로 확정
- [ ] 친구검증(ACCEPTED) 적용 지점(API vs worker) 확정
- [ ] 상태 변경 이벤트(`STATE_REFRESH`)의 발행자/소비자 계약 문서화
- [ ] 서비스 간 의존 방향 문서화 (inference -> message? direct or event-only)

