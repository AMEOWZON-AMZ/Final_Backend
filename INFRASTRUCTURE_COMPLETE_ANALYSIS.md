# 🏗️ AMEOWZON 프로젝트 인프라 & 배포 환경 완전 분석

**작성일**: 2026-03-02  
**분석 범위**: 전체 시스템 아키텍처, 배포 환경, 데이터베이스, AWS 인프라

---

## 📊 시스템 개요

**프로젝트명**: AMEOWZON (고양이 캐릭터 기반 소셜 챌린지 앱)  
**아키텍처**: 마이크로서비스 (3개 서비스)  
**배포 환경**: AWS EKS (Kubernetes)  
**주요 언어**: Python (FastAPI)

---

## 🎯 서비스 구조

### 1. User Service (메인)
**위치**: `services/user_service/`  
**역할**: 사용자 관리, 친구 시스템, 챌린지, 파일 업로드  
**포트**: 8000  
**프레임워크**: FastAPI + Gunicorn + Uvicorn Workers

**주요 기능**:
- 사용자 인증 & 회원가입 (Cognito)
- 친구 요청/수락/거절 시스템
- 챌린지 생성 & 제출 (GPS 좌표 포함)
- 고양이 캐릭터 생성 (Gemini 2.5 Flash Image)
- 음성 파일 업로드 & 검증 (Audio Guard)
- QR 코드 기반 빠른 등록
- FCM 푸시 알림

### 2. Inference Service
**위치**: `services/inference_service/`  
**역할**: AI 추론 (상태 분석, 음성 처리)  
**상태**: 구조만 존재 (미구현)

### 3. Message Service
**위치**: `services/message_service/`  
**역할**: 메시지 처리  
**상태**: 구조만 존재 (미구현)

---

## 🗄️ 데이터베이스 아키텍처

### RDS PostgreSQL (정규화)

**엔드포인트**: `user-service-cluster.cluster-cn4w6k04aq5d.ap-northeast-2.rds.amazonaws.com`  
**용도**: 사용자 기본 정보, 챌린지 데이터

#### 테이블 구조

**users** (사용자 정보)
```sql
- user_id (PK, VARCHAR(255)) - Cognito Sub
- email (UNIQUE, VARCHAR(100))
- nickname (VARCHAR(50))
- phone_number (VARCHAR(20))
- friend_code (UNIQUE, VARCHAR(6)) - 친구 추가용
- profile_image_url (VARCHAR(500))
- cat_pattern (VARCHAR(50)) - solid/dotted/stripe
- cat_color (VARCHAR(7)) - HEX 색상
- meow_audio_url (VARCHAR(500))
- train_voice_urls (VARCHAR(2000)) - JSON 배열
- token (VARCHAR(500)) - FCM 토큰
- my_status (TEXT) - 상태 메시지
- provider (VARCHAR(50)) - google/cognito
- profile_setup_completed (BOOLEAN)
- created_at_timestamp (BIGINT)
- updated_at_timestamp (BIGINT)
```

**challenge_days** (챌린지 정의)
```sql
- id (PK, BIGINT)
- challenge_date (DATE, UNIQUE)
- title (VARCHAR(255)) - 한글
- title_en (VARCHAR(255)) - 영문
- description (TEXT)
- created_at (TIMESTAMP)
```

**challenge_submissions** (챌린지 제출)
```sql
- id (PK, BIGINT)
- user_id (FK → users.user_id, CASCADE)
- challenge_day_id (FK → challenge_days.id, CASCADE)
- image_url (TEXT) - S3 URL
- latitude (NUMERIC(10,8)) - GPS 위도
- longitude (NUMERIC(11,8)) - GPS 경도
- altitude (NUMERIC(8,2)) - 고도
- has_gps (BOOLEAN)
- created_at (TIMESTAMP)
```

**friends** (미사용 - 정의만 존재)
```sql
- id (PK, INTEGER)
- user_id (FK → users.user_id, CASCADE)
- friend_id (FK → users.user_id, CASCADE)
- status (VARCHAR(20))
- created_at (TIMESTAMP)
```
**참고**: 실제로는 DynamoDB `user_friends` 사용

---

### DynamoDB (비정규화)

**리전**: ap-northeast-2  
**용도**: 친구 관계, 이벤트 큐 (빠른 조회)

#### 테이블 구조

**user_friends** (친구 관계)
```
Partition Key: user_id (String)
Sort Key: friend_user_id (String)

Attributes:
- status (String) - pending/sending/accepted
- created_at (Number) - timestamp
- updated_at (Number) - timestamp
- daily_status (String) - STABLE/SLEEP/LETHARGY/CHAOS/TRAVEL

# 친구 프로필 정보 (비정규화)
- email (String)
- nickname (String)
- profile_image_url (String)
- cat_pattern (String)
- cat_color (String)
- meow_audio_url (String)
```

**OutboxEvents** (이벤트 큐)
```
Partition Key: event_id (String)
Sort Key: created_at (Number)

Attributes:
- event_type (String) - FRIEND_REQUEST/FRIEND_ACCEPTED/FRIEND_REJECTED
- status (String) - PENDING/SENT/FAILED
- to_user_id (String)
- from_user_id (String)
- from_nickname (String)
- payload (Map) - 이벤트 데이터
- retry_count (Number)
- last_error (String)
```

**GSI (Global Secondary Index)**:
- `FriendUserIdIndex` (권장, 미생성) - friend_user_id로 역방향 조회

---

## ☁️ AWS 인프라

### EKS (Elastic Kubernetes Service)

**클러스터명**: (프로젝트별 설정)  
**리전**: ap-northeast-2  
**네트워크**: Private Subnet (보안)

#### Kubernetes 리소스

**Namespace**: `user-service`

**Deployment**: `user-service`
```yaml
Replicas: 1
Image: 715428147916.dkr.ecr.ap-northeast-2.amazonaws.com/user-service:latest
Resources:
  Requests: 1Gi RAM, 250m CPU
  Limits: 2Gi RAM, 1000m CPU
Command: gunicorn -k uvicorn.workers.UvicornWorker -w 2 -b 0.0.0.0:8000
Probes:
  Liveness: /health (90s delay, 20s period)
  Readiness: /health (40s delay, 10s period)
```

**Service**: `user-service`
```yaml
Type: LoadBalancer
Port: 80 → 8000
```

**Ingress**: `user-service-ingress`
```yaml
Class: alb (AWS Application Load Balancer)
Scheme: internet-facing
Target Type: ip
Health Check: /health/ (30s interval)
```

**ServiceAccount**: `user-service-sa`
```yaml
Annotations:
  eks.amazonaws.com/role-arn: arn:aws:iam::715428147916:role/UserServicePodRole
```

**ConfigMap**: `user-service-config`
```yaml
USE_RDS: "true"
USE_LOCAL_DYNAMODB: "false"
AWS_REGION: "ap-northeast-2"
RDS_HOST: "user-service-cluster.cluster-cn4w6k04aq5d.ap-northeast-2.rds.amazonaws.com"
RDS_PORT: "5432"
RDS_DATABASE: "postgres"
RDS_USER: "user_admin"
COGNITO_USER_POOL_ID: "..."
COGNITO_REGION: "ap-northeast-2"
```

**Secret**: `user-service-secret`
```yaml
SECRET_KEY: <base64>
RDS_PASSWORD: <base64>
GEMINI_API_KEY: <base64>
NANOBANANA_API_KEY: <base64>
FCM_CREDENTIALS_JSON: <base64>
```

---

### S3 (Simple Storage Service)

**버킷 1**: `ameowzon-test-files`
```
용도: 사용자 파일 저장
구조:
  profiles/images/{user_id}_*.jpg        # 프로필 이미지
  profiles/audio/meow/{user_id}_*.wav    # 야옹 소리
  profiles/audio/train/{user_id}_*.wav   # 암구호 음성 (개별 3개)
  cat-characters/{user_id}_*.png         # 고양이 캐릭터
  challenges/{date}/{user_id}_*.jpg      # 챌린지 이미지
```

**버킷 2**: `amz-bgm`
```
용도: BGM 및 병합 음성
구조:
  meow/enroll/{user_id}/enroll.wav       # 병합된 train voice (SageMaker용)
  meow/daily_outputs/{user_id}_*.wav     # BGM 파일
```

---

### IAM (Identity and Access Management)

**Role**: `UserServicePodRole`
```json
Permissions:
- RDS: Connect (IAM 인증)
- DynamoDB: Query, Scan, PutItem, UpdateItem, DeleteItem
- S3: GetObject, PutObject, DeleteObject
- Transcribe: StartTranscriptionJob, GetTranscriptionJob
- Cognito: GetUser, ListUsers
```

**Policy**: `user-service-policy.json`
```
위치: iam/user-service-policy.json
적용: UserServicePodRole
```

**Pod Identity**: EKS Pod Identity (최신 방식)
```
ServiceAccount: user-service-sa
Role ARN: arn:aws:iam::715428147916:role/UserServicePodRole
Token: /var/run/secrets/eks.amazonaws.com/serviceaccount/token
```

---

### ECR (Elastic Container Registry)

**Repository**: `user-service`
```
URI: 715428147916.dkr.ecr.ap-northeast-2.amazonaws.com/user-service
Tag: latest
Image Size: ~1.5GB
Base Image: python:3.11-slim
```

---

### Other AWS Services

**Cognito**
```
User Pool ID: (설정됨)
Region: ap-northeast-2
용도: JWT 토큰 인증
```

**Transcribe**
```
용도: 음성 → 텍스트 변환 (Audio Guard)
API: StartTranscriptionJob (일반 API, Streaming 아님)
```

**CloudWatch**
```
용도: 로그 수집 (EKS Pod 로그)
Log Group: /aws/eks/user-service
```

---

## 🔌 외부 API 통합

### 1. Gemini API (Google)
```
모델: gemini-2.5-flash-image
용도:
  - 고양이 캐릭터 생성 (사람 사진 → 고양이)
  - 챌린지 자동 생성 (매월 30개)
  - 음성 판단 (Audio Guard)
타임아웃: 120초
```

### 2. Firebase FCM
```
용도: 푸시 알림
방식:
  - 직접 전송 (기존)
  - OutboxEvents 큐 (새 방식, Push Worker)
Credentials: FCM_CREDENTIALS_JSON (Secret)
```

### 3. Nanobanana API (대안)
```
용도: 고양이 이미지 생성 (Gemini 대안)
상태: 구현됨, 사용 안 함
```

---

## 🔄 데이터 흐름

### 1. 회원가입 & 로그인
```
Client
  ↓ POST /api/v1/users/signup
User Service
  ↓ 1. Cognito 토큰 검증
  ↓ 2. RDS users 테이블에 저장
  ↓ 3. S3에 파일 업로드 (선택)
  ↓ 4. FCM 토큰 저장 (선택)
  ← Response (user_id, friend_code)
```

### 2. 친구 추가
```
Client
  ↓ POST /api/v1/friends/request (friend_code)
User Service
  ↓ 1. RDS에서 friend_code로 사용자 조회
  ↓ 2. DynamoDB user_friends에 양방향 관계 생성
  ↓    - user_id → friend_user_id (status=sending)
  ↓    - friend_user_id → user_id (status=pending)
  ↓ 3. DynamoDB OutboxEvents에 이벤트 저장
  ↓    - event_type: FRIEND_REQUEST
  ↓    - to_user_id: friend_user_id
  ↓    - from_user_id: user_id
  ← Response (success)

Push Worker (별도 Pod)
  ↓ 1. OutboxEvents 폴링 (0.5초 간격)
  ↓ 2. status=PENDING 이벤트 조회
  ↓ 3. RDS에서 to_user_id의 FCM 토큰 조회
  ↓ 4. Firebase FCM API 호출
  ↓ 5. OutboxEvents 상태 업데이트 (SENT/FAILED)
```

### 3. 챌린지 제출
```
Client
  ↓ POST /api/v1/challenges/{id}/submit (image)
User Service
  ↓ 1. 이미지 EXIF에서 GPS 좌표 추출
  ↓ 2. S3에 이미지 업로드
  ↓    - challenges/{date}/{user_id}_{timestamp}.jpg
  ↓ 3. RDS challenge_submissions에 저장
  ↓    - image_url, latitude, longitude
  ← Response (submission_id)
```

### 4. 고양이 캐릭터 생성
```
Client
  ↓ POST /api/v1/cat-character/generate/{user_id} (image)
User Service
  ↓ 1. 이미지 검증 (크기, 형식)
  ↓ 2. Gemini 2.5 Flash Image API 호출
  ↓    - 프롬프트: CAT_CHARACTER_TRANSFORM_PROMPT
  ↓    - 타임아웃: 120초
  ↓ 3. 생성된 이미지 S3 업로드
  ↓    - cat-characters/{user_id}_{timestamp}.png
  ↓ 4. Base64 인코딩 (즉시 표시용)
  ← Response (generated_url, generated_image_base64)
```

---

## 🚀 배포 프로세스

### 1. 로컬 개발
```bash
cd services/user_service
python run_local.py
# http://localhost:8000
```

### 2. Docker 빌드
```bash
cd services/user_service
docker build -t user-service:latest .
```

### 3. ECR 푸시
```bash
# ECR 로그인
aws ecr get-login-password --region ap-northeast-2 | \
  docker login --username AWS --password-stdin \
  715428147916.dkr.ecr.ap-northeast-2.amazonaws.com

# 태그
docker tag user-service:latest \
  715428147916.dkr.ecr.ap-northeast-2.amazonaws.com/user-service:latest

# 푸시
docker push 715428147916.dkr.ecr.ap-northeast-2.amazonaws.com/user-service:latest
```

### 4. EKS 배포
```bash
# Namespace 생성 (최초 1회)
kubectl apply -f k8s/namespace.yaml

# ConfigMap & Secret 생성
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml

# ServiceAccount & IAM 설정
kubectl apply -f k8s/serviceaccount.yaml

# Deployment & Service
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Ingress (ALB)
kubectl apply -f k8s/ingress.yaml
```

### 5. 배포 확인
```bash
# Pod 상태
kubectl get pods -n user-service

# 로그 확인
kubectl logs -f deployment/user-service -n user-service

# Service 확인
kubectl get svc -n user-service

# Ingress 확인
kubectl get ingress -n user-service
```

### 6. 롤링 업데이트
```bash
# 새 이미지 배포
kubectl rollout restart deployment/user-service -n user-service

# 배포 상태 확인
kubectl rollout status deployment/user-service -n user-service

# 롤백 (필요시)
kubectl rollout undo deployment/user-service -n user-service
```

---

## 🔐 보안 설정

### 1. 네트워크
- EKS Private Subnet (인터넷 직접 접근 불가)
- ALB를 통한 외부 접근 (internet-facing)
- RDS VPC 내부 (외부 접근 불가)
- DynamoDB VPC Endpoint (선택)

### 2. 인증 & 권한
- Cognito JWT 토큰 인증
- EKS Pod Identity (IAM Role)
- RDS IAM 인증 (선택)
- Secret 암호화 (Kubernetes Secret)

### 3. 데이터 암호화
- RDS at-rest 암호화
- DynamoDB at-rest 암호화
- S3 at-rest 암호화
- TLS/SSL 통신 (HTTPS)

---

## 📊 모니터링 & 로깅

### CloudWatch
```
Log Group: /aws/eks/user-service
Metrics:
  - CPU 사용률
  - 메모리 사용률
  - 네트워크 I/O
  - 요청 수 (ALB)
```

### Kubernetes
```bash
# Pod 리소스 사용량
kubectl top pods -n user-service

# Node 리소스 사용량
kubectl top nodes

# 이벤트 확인
kubectl get events -n user-service --sort-by='.lastTimestamp'
```

### Application Logs
```python
# Loguru 사용
logger.info("✅ Success message")
logger.error("❌ Error message")
logger.warning("⚠️ Warning message")
```

---

## 🔧 주요 설정 파일

### Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ ./app/
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", \
     "-w", "2", "-b", "0.0.0.0:8000", "app.main:app"]
```

### requirements.txt
```
fastapi==0.109.0
uvicorn==0.27.0
gunicorn==21.2.0
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
boto3==1.34.34
pydantic==2.5.3
python-jose[cryptography]==3.3.0
google-generativeai==0.3.2
firebase-admin==6.4.0
pydub==0.25.1
pillow==10.2.0
loguru==0.7.2
```

---

## 📈 성능 최적화

### 1. 데이터베이스
- DynamoDB 비정규화 (친구 목록 1회 쿼리)
- RDS 인덱스 (email, friend_code, user_id)
- Connection Pool (SQLAlchemy)

### 2. 캐싱
- S3 Presigned URL (1시간 유효)
- DynamoDB 쿼리 결과 (선택)

### 3. 비동기 처리
- OutboxEvents 큐 (Push Worker)
- Gunicorn + Uvicorn Workers (2개)

### 4. 리소스 제한
- Pod Requests: 1Gi RAM, 250m CPU
- Pod Limits: 2Gi RAM, 1000m CPU
- Gunicorn Timeout: 120초

---

## 🚧 알려진 이슈 & 제한사항

### 1. DynamoDB GSI 미생성
- `FriendUserIdIndex` GSI 없음
- 역방향 조회 시 Scan 사용 (느림)
- 해결: GSI 추가 권장

### 2. RDS Friends 테이블 미사용
- 모델만 정의, 실제 사용 안 함
- DynamoDB `user_friends` 사용
- 해결: 모델 제거 또는 주석 처리

### 3. Push Worker 미배포
- OutboxEvents 폴링 Pod 없음
- 친구 이벤트 알림 미전송
- 해결: Push Worker Pod 배포 필요

### 4. 프론트엔드 FCM 토큰 미전송
- 로그인 시 FCM 토큰 전송 안 함
- Push 알림 불가
- 해결: 프론트엔드 수정 필요

---

## 📝 마이그레이션 이력

### 001_create_challenges_tables.sql
- challenge_days, challenge_submissions 테이블 생성

### 002_add_phone_number_to_users.sql
- users 테이블에 phone_number 컬럼 추가

### 003_add_gps_to_submissions.sql
- challenge_submissions에 GPS 컬럼 추가
- latitude, longitude, altitude, has_gps

### 004_add_cascade_to_friends.sql (삭제됨)
- Friends 테이블 CASCADE 설정
- 실제로는 사용 안 함 (DynamoDB 사용)

---

## 🎯 다음 단계

### 즉시 필요
1. ✅ 사용자 삭제 기능 배포 (완료)
2. ✅ Quick Register OutboxEvents 추가 (완료)
3. ⏳ Docker 빌드 & ECR 푸시 (진행 중)
4. ⏳ EKS 배포

### 단기 (1주일)
1. Push Worker Pod 배포
2. DynamoDB GSI 추가 (FriendUserIdIndex)
3. 프론트엔드 FCM 토큰 전송 구현
4. 챌린지 UNIQUE 제약 제거 마이그레이션

### 중기 (1개월)
1. Inference Service 구현
2. Message Service 구현
3. 모니터링 대시보드 구축
4. 자동 스케일링 설정

---

**작성자**: Kiro AI Assistant  
**분석 완료일**: 2026-03-02  
**문서 버전**: 1.0  
**상태**: ✅ 완전 분석 완료
