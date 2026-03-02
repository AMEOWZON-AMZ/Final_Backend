# vision_service Pod 문서

## 1. Pod 개요

- Pod 이름: `vision-validate`
- 담당 도메인: 이미지-주제 적합성 검증
- 배포 환경: AWS EKS
- 주요 역할:
  - 업로드 이미지 정규화(JPEG)
  - OpenCLIP/SigLIP 기반 이미지-텍스트 유사도 계산
  - DB에서 일자별 챌린지 주제를 조회해 매칭 여부 판정

## 2. 담당 기능

### 2.1 처리 기능
- `POST /vision/validate`:
  - 이미지 파일 입력 검증
  - 날짜별 topic 조회
  - score 계산 및 threshold 비교 결과 반환
- `GET /health`
- startup 시 모델/DB 리소스 초기화

### 2.2 제외 기능
- 메시지/하트/푸시 처리
- Outbox 생성/소비
- 배치 추론 파이프라인 실행
- 사용자 상태 동기화

## 3. API Endpoints

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/vision/validate` | 이미지가 해당 날짜 주제와 맞는지 검증 |
| GET | `/health` | 헬스체크 |

## 4. 데이터 흐름

1. User App 또는 Backend가 이미지와 날짜를 `vision_service`로 전송
2. Pod가 이미지 타입/크기 검증 후 JPEG 정규화
3. DB(`challenge_days`)에서 해당 날짜 topic 조회
4. OpenCLIP으로 cosine similarity 계산
5. threshold 이상이면 `matched=true`로 응답

## 5. 사용 인프라

- EKS Deployment: `services/vision_service/k8s/deployment.yaml`
- EKS Service(LoadBalancer): `services/vision_service/k8s/service.yaml`
- ServiceAccount: `vision-validate-sa`
- Secret: `vision-validate-secret` (`DATABASE_URL`)
- 리소스 설정:
  - requests: `cpu 500m`, `memory 1Gi`
  - limits: `cpu 2000m`, `memory 4Gi`
- readiness/liveness probe: `/health`
- CloudWatch Logs

## 6. 이벤트 처리 방식

- 본 서비스는 이벤트 큐/Outbox를 사용하지 않는 동기 API 구조
- 요청 단위 처리로 결과를 즉시 반환
- 비동기 알림/재시도는 다른 서비스 계층(`msg_service`, `push_worker`)에서 담당

## 7. 장애 대응 전략

- 입력 검증 강화: 파일 타입/빈 파일/용량 초과/날짜 포맷 검사
- DB 조회 실패 시 `502`, 모델 처리 실패 시 `500`으로 오류 분리
- readiness/liveness probe로 비정상 Pod 자동 교체
- 모델/DB 리소스 startup 초기화 실패를 조기 감지

## 8. 확장 전략

- CPU/GPU 노드 정책에 맞춘 수평 확장(HPA) 적용 가능
- 모델 버전 교체 시 이미지 태그 기반 Blue/Green 배포 적합
- 주제 조회 DB 병목 시 캐시 계층 도입 여지
- 추후 멀티모델/AB 테스트 구조로 확장 가능
