# 챌린지 API 문서

## 개요

매일 고양이 사진 챌린지 시스템
- 매일 새로운 챌린지 주제 제공
- 사용자는 오늘 날짜 챌린지에만 사진 제출 가능
- 한 챌린지당 1회만 제출 가능 (1인 1장)

---

## 데이터베이스 스키마

### challenges 테이블
```sql
CREATE TABLE challenges (
    challenge_id VARCHAR(36) PRIMARY KEY,
    challenge_date DATE NOT NULL UNIQUE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
);
```

### challenge_submissions 테이블
```sql
CREATE TABLE challenge_submissions (
    submission_id VARCHAR(36) PRIMARY KEY,
    challenge_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    image_url VARCHAR(500) NOT NULL,
    submitted_at TIMESTAMP WITH TIME ZONE,
    
    FOREIGN KEY (challenge_id) REFERENCES challenges(challenge_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    UNIQUE (challenge_id, user_id)
);
```

---

## API 엔드포인트

### 1. 챌린지 생성 (관리자용)

**POST** `/api/v1/challenges/`

**요청 Body (JSON)**:
```json
{
  "challenge_date": "2026-02-15",
  "title": "고양이 발바닥 찍기",
  "description": "귀여운 고양이 발바닥을 찍어보세요!"
}
```

**응답 (201 Created)**:
```json
{
  "challenge_id": "550e8400-e29b-41d4-a716-446655440000",
  "challenge_date": "2026-02-15",
  "title": "고양이 발바닥 찍기",
  "description": "귀여운 고양이 발바닥을 찍어보세요!",
  "created_at": "2026-02-15T10:00:00Z",
  "updated_at": "2026-02-15T10:00:00Z"
}
```

**에러**:
- `400`: 해당 날짜에 이미 챌린지 존재

---

### 2. 날짜별 챌린지 조회

**GET** `/api/v1/challenges/date/{date}`

**경로 파라미터**:
- `date`: 조회할 날짜 (YYYY-MM-DD)

**쿼리 파라미터**:
- `user_id` (선택): 사용자 ID (제공 시 제출 여부 포함)

**응답 (200 OK)**:
```json
{
  "challenge_id": "550e8400-e29b-41d4-a716-446655440000",
  "date": "2026-02-15",
  "title": "고양이 발바닥 찍기",
  "description": "귀여운 고양이 발바닥을 찍어보세요!",
  "is_active": true,
  "user_submission": {
    "submitted": false,
    "image_url": null,
    "submitted_at": null
  }
}
```

**user_id 제공 시 (제출 완료)**:
```json
{
  "challenge_id": "550e8400-e29b-41d4-a716-446655440000",
  "date": "2026-02-15",
  "title": "고양이 발바닥 찍기",
  "description": "귀여운 고양이 발바닥을 찍어보세요!",
  "is_active": true,
  "user_submission": {
    "submitted": true,
    "image_url": "https://ameowzon-user-profiles.s3.ap-northeast-2.amazonaws.com/challenges/...",
    "submitted_at": "2026-02-15T14:30:00Z"
  }
}
```

**필드 설명**:
- `is_active`: `true`면 오늘 날짜 (제출 가능), `false`면 과거/미래 날짜 (조회만 가능)
- `user_submission.submitted`: 사용자가 이미 제출했는지 여부

**에러**:
- `404`: 해당 날짜에 챌린지 없음

---

### 3. 챌린지 제출

**POST** `/api/v1/challenges/{challenge_id}/submit`

**경로 파라미터**:
- `challenge_id`: 챌린지 ID

**요청 (Multipart Form)**:
- `user_id` (Form): 사용자 ID
- `image` (File): 이미지 파일

**응답 (201 Created)**:
```json
{
  "submission_id": "660e8400-e29b-41d4-a716-446655440000",
  "challenge_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "c478cd4c-5071-7060-2991-cc9b3bb59dff",
  "image_url": "https://ameowzon-user-profiles.s3.ap-northeast-2.amazonaws.com/challenges/...",
  "submitted_at": "2026-02-15T14:30:00Z"
}
```

**제약사항**:
- 오늘 날짜 챌린지만 제출 가능
- 한 챌린지당 1회만 제출 가능
- 이미지 파일만 허용 (JPEG, PNG, GIF, WebP)

**에러**:
- `400`: 오늘 날짜가 아님 / 이미 제출함 / 잘못된 파일 형식
- `404`: 챌린지 없음

**curl 예제**:
```bash
curl -X POST "http://43.203.213.35:8000/api/v1/challenges/{challenge_id}/submit" \
  -F "user_id=c478cd4c-5071-7060-2991-cc9b3bb59dff" \
  -F "image=@cat_photo.jpg;type=image/jpeg"
```

---

### 4. 사용자 챌린지 이력 조회

**GET** `/api/v1/challenges/users/{user_id}/history`

**경로 파라미터**:
- `user_id`: 사용자 ID

**쿼리 파라미터**:
- `limit` (선택, 기본 50): 조회 개수
- `offset` (선택, 기본 0): 시작 위치

**응답 (200 OK)**:
```json
{
  "total": 15,
  "submissions": [
    {
      "challenge_id": "550e8400-e29b-41d4-a716-446655440000",
      "date": "2026-02-15",
      "title": "고양이 발바닥 찍기",
      "image_url": "https://ameowzon-user-profiles.s3.ap-northeast-2.amazonaws.com/challenges/...",
      "submitted_at": "2026-02-15T14:30:00Z"
    },
    {
      "challenge_id": "660e8400-e29b-41d4-a716-446655440000",
      "date": "2026-02-14",
      "title": "고양이 하품 순간 포착",
      "image_url": "https://ameowzon-user-profiles.s3.ap-northeast-2.amazonaws.com/challenges/...",
      "submitted_at": "2026-02-14T16:20:00Z"
    }
  ]
}
```

**정렬**: 최신순 (submitted_at DESC)

---

## S3 저장 경로

**챌린지 이미지**:
```
challenges/{challenge_id}/{user_id}_{timestamp}_{uuid}.{ext}
```

**예시**:
```
challenges/550e8400-e29b-41d4-a716-446655440000/c478cd4c-5071-7060-2991-cc9b3bb59dff_20260215_143000_a1b2c3d4.jpg
```

---

## 프론트엔드 플로우

### 캘린더 페이지 진입
1. 사용자가 캘린더 페이지 진입
2. 날짜 버튼들 표시 (매일 챌린지 있음)

### 날짜 클릭
1. 사용자가 특정 날짜 클릭
2. `GET /api/v1/challenges/date/{date}?user_id={user_id}` 호출
3. 응답 확인:
   - `is_active: true` → 오늘 날짜 (제출 가능)
   - `is_active: false` → 과거/미래 날짜 (조회만)
   - `user_submission.submitted: true` → 이미 제출함
   - `user_submission.submitted: false` → 아직 미제출

### 오늘 날짜 + 미제출
1. 챌린지 제목/설명 표시
2. 사진 업로드 버튼 활성화
3. 사용자가 사진 선택 후 제출
4. `POST /api/v1/challenges/{challenge_id}/submit` 호출
5. 성공 시 이미지 URL 표시

### 오늘 날짜 + 이미 제출
1. 챌린지 제목/설명 표시
2. 제출한 사진 표시
3. 업로드 버튼 비활성화

### 과거/미래 날짜
1. 챌린지 제목/설명 표시
2. 제출한 사진 표시 (있으면)
3. 업로드 버튼 비활성화

---

## 테스트

### 테이블 생성
```bash
cd services/user_service
python create_challenge_tables.py
```

### API 테스트
```bash
cd services/user_service
python test_challenge_api.py
```

### 수동 테스트

**1. 챌린지 생성**:
```bash
curl -X POST "http://43.203.213.35:8000/api/v1/challenges/" \
  -H "Content-Type: application/json" \
  -d '{
    "challenge_date": "2026-02-15",
    "title": "고양이 발바닥 찍기",
    "description": "귀여운 고양이 발바닥을 찍어보세요!"
  }'
```

**2. 챌린지 조회**:
```bash
curl "http://43.203.213.35:8000/api/v1/challenges/date/2026-02-15?user_id=c478cd4c-5071-7060-2991-cc9b3bb59dff"
```

**3. 챌린지 제출**:
```bash
curl -X POST "http://43.203.213.35:8000/api/v1/challenges/{challenge_id}/submit" \
  -F "user_id=c478cd4c-5071-7060-2991-cc9b3bb59dff" \
  -F "image=@cat_photo.jpg"
```

**4. 이력 조회**:
```bash
curl "http://43.203.213.35:8000/api/v1/challenges/users/c478cd4c-5071-7060-2991-cc9b3bb59dff/history?limit=10"
```

---

## 배포

### 1. 테이블 생성
```bash
python create_challenge_tables.py
```

### 2. Docker 빌드
```bash
cd services/user_service
docker build -t user-service:latest .
```

### 3. ECR 푸시
```bash
aws ecr get-login-password --region ap-northeast-2 | docker login --username AWS --password-stdin 715428147916.dkr.ecr.ap-northeast-2.amazonaws.com
docker tag user-service:latest 715428147916.dkr.ecr.ap-northeast-2.amazonaws.com/user-service:latest
docker push 715428147916.dkr.ecr.ap-northeast-2.amazonaws.com/user-service:latest
```

### 4. EC2 배포
```bash
ssh -i ~/.ssh/user-pair.pem ec2-user@43.203.213.35

# ECR 로그인
aws ecr get-login-password --region ap-northeast-2 | docker login --username AWS --password-stdin 715428147916.dkr.ecr.ap-northeast-2.amazonaws.com

# 이미지 Pull
docker pull 715428147916.dkr.ecr.ap-northeast-2.amazonaws.com/user-service:latest

# 컨테이너 재시작
docker stop user-service-container
docker rm user-service-container
docker run -d --name user-service-container -p 8000:8000 \
  -e USE_RDS=true \
  -e RDS_HOST=user-service-cluster.cluster-cn4w6k04aq5d.ap-northeast-2.rds.amazonaws.com \
  -e RDS_PORT=5432 \
  -e RDS_DATABASE=postgres \
  -e RDS_USERNAME=user_admin \
  -e RDS_PASSWORD=stilbne092! \
  -e AWS_REGION=ap-northeast-2 \
  -e S3_BUCKET_NAME=ameowzon-user-profiles \
  -e S3_BASE_URL=https://ameowzon-user-profiles.s3.ap-northeast-2.amazonaws.com \
  -e DYNAMODB_REGION=ap-northeast-2 \
  -e DEBUG=true \
  715428147916.dkr.ecr.ap-northeast-2.amazonaws.com/user-service:latest
```

---

## 주요 파일

**모델**:
- `services/user_service/app/models/challenge.py`

**스키마**:
- `services/user_service/app/schemas/challenge.py`

**서비스**:
- `services/user_service/app/services/challenge_service.py`
- `services/user_service/app/services/s3_service.py` (챌린지 이미지 업로드 추가)

**API 라우트**:
- `services/user_service/app/api/routes/challenges.py`
- `services/user_service/app/api/v1/api.py` (라우터 등록)

**마이그레이션**:
- `services/user_service/migrations/001_create_challenges_tables.sql`
- `services/user_service/create_challenge_tables.py`

**테스트**:
- `services/user_service/test_challenge_api.py`

---

**작성일**: 2026-02-15
**작성자**: AI Assistant
