# Ameowzon Database ERD

**작성일**: 2026-02-11  
**데이터베이스**: PostgreSQL RDS + AWS DynamoDB

---

## 📊 데이터베이스 구조 개요

### RDS (PostgreSQL)
- 사용자 기본 정보 저장
- 정규화된 구조

### DynamoDB
- 친구 관계 정보 저장 (비정규화)
- 빠른 조회를 위해 친구 프로필 정보 중복 저장

---

## 🗄️ RDS (PostgreSQL)

### users 테이블

```
┌─────────────────────────────────────────────────────────────┐
│                           users                              │
├─────────────────────────────────────────────────────────────┤
│ PK  user_id                VARCHAR(255)                     │
│     email                  VARCHAR(100)  UNIQUE, NOT NULL   │
│     nickname               VARCHAR(50)   NOT NULL           │
│     profile_image_url      VARCHAR(500)  NULL               │
│     friend_code            VARCHAR(6)    UNIQUE, NOT NULL   │
│     created_at_timestamp   BIGINT        NOT NULL           │
│     updated_at_timestamp   BIGINT        NOT NULL           │
│     cat_pattern            VARCHAR(20)   NULL               │
│     cat_color              VARCHAR(7)    NULL               │
│     duress_code            VARCHAR(100)  NULL               │
│     meow_audio_url         VARCHAR(500)  NULL               │
│     duress_audio_url       VARCHAR(500)  NULL               │
│     token                  VARCHAR(500)  NULL               │
│     provider               VARCHAR(50)   NOT NULL           │
│     profile_setup_completed BOOLEAN      DEFAULT FALSE      │
└─────────────────────────────────────────────────────────────┘

인덱스:
- PRIMARY KEY: user_id
- UNIQUE INDEX: email
- UNIQUE INDEX: friend_code
- INDEX: user_id
```

### 컬럼 설명

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| `user_id` | VARCHAR(255) | 사용자 고유 ID (Cognito Sub) |
| `email` | VARCHAR(100) | 이메일 주소 (고유) |
| `nickname` | VARCHAR(50) | 닉네임 |
| `profile_image_url` | VARCHAR(500) | 프로필 이미지 URL (S3) |
| `friend_code` | VARCHAR(6) | 친구 추가용 코드 (6자리 영숫자) |
| `created_at_timestamp` | BIGINT | 생성 시간 (밀리초) |
| `updated_at_timestamp` | BIGINT | 수정 시간 (밀리초) |
| `cat_pattern` | VARCHAR(20) | 고양이 패턴 (solid, dotted, stripe) |
| `cat_color` | VARCHAR(7) | 고양이 색상 (HEX 코드) |
| `duress_code` | VARCHAR(100) | 위험 신호 코드 |
| `meow_audio_url` | VARCHAR(500) | 야옹 소리 URL (S3) |
| `duress_audio_url` | VARCHAR(500) | 위험 신호 소리 URL (S3) |
| `token` | VARCHAR(500) | FCM 토큰 (푸시 알림용) |
| `provider` | VARCHAR(50) | 인증 제공자 (google, cognito) |
| `profile_setup_completed` | BOOLEAN | 프로필 설정 완료 여부 |

---

## 🔥 DynamoDB

### Friends 테이블

```
┌─────────────────────────────────────────────────────────────┐
│                          Friends                            │
├─────────────────────────────────────────────────────────────┤
│ PK  user_id                String                           │
│ SK  friend_user_id         String                           │
│     status                 String  (accepted, blocked)      │
│     created_at             Number  (timestamp)              │
│     updated_at             Number  (timestamp)              │
│                                                             │
│     # 친구 프로필 정보 (비정규화)                              │
│     email                  String                           │
│     nickname               String                           │
│     profile_image_url      String                           │
│     cat_pattern            String                           │
│     cat_color              String                           │
│     meow_audio_url         String                           │
│     duress_code            String                           │
│     duress_audio_url       String                           │
│     daily_status           String                           │
│                                                             │
│     # 차단 관련 (status=blocked일 때만)                       │
│     blocked_at             Number  (timestamp)              │
│     blocked_reason         String  (spam, harassment, etc)  │
└─────────────────────────────────────────────────────────────┘

키 구조:
- Partition Key (PK): user_id
- Sort Key (SK): friend_user_id
```

### 컬럼 설명

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| `user_id` | String | 사용자 ID (PK) |
| `friend_user_id` | String | 친구 사용자 ID (SK) |
| `status` | String | 관계 상태 (accepted, blocked) |
| `created_at` | Number | 생성 시간 (밀리초) |
| `updated_at` | Number | 수정 시간 (밀리초) |
| `email` | String | 친구 이메일 (비정규화) |
| `nickname` | String | 친구 닉네임 (비정규화) |
| `profile_image_url` | String | 친구 프로필 이미지 (비정규화) |
| `cat_pattern` | String | 친구 고양이 패턴 (비정규화) |
| `cat_color` | String | 친구 고양이 색상 (비정규화) |
| `meow_audio_url` | String | 친구 야옹 소리 (비정규화) |
| `duress_code` | String | 친구 위험 신호 코드 (비정규화) |
| `duress_audio_url` | String | 친구 위험 신호 소리 (비정규화) |
| `daily_status` | String | 일일 상태 (AI 추론) |
| `blocked_at` | Number | 차단 시간 (차단 시에만) |
| `blocked_reason` | String | 차단 사유 (차단 시에만) |

---

## 🔗 관계도

```
┌─────────────────┐
│   PostgreSQL    │
│      RDS        │
│                 │
│  ┌───────────┐  │
│  │   users   │  │
│  └─────┬─────┘  │
│        │        │
└────────┼────────┘
         │
         │ user_id로 연결
         │
┌────────┼────────┐
│        │        │
│  ┌─────▼─────┐  │
│  │  Friends  │  │
│  │ (DynamoDB)│  │
│  └───────────┘  │
│                 │
│   DynamoDB      │
└─────────────────┘
```

### 데이터 흐름

1. **회원가입/로그인**
   - RDS `users` 테이블에 사용자 정보 저장
   - FCM 토큰도 함께 저장 (선택)

2. **친구 추가**
   - RDS에서 친구 코드로 사용자 조회
   - DynamoDB `Friends` 테이블에 양방향 관계 생성
   - 친구의 프로필 정보를 비정규화하여 함께 저장

3. **로비 친구 목록 조회**
   - DynamoDB에서 한 번의 쿼리로 모든 친구 정보 조회
   - RDS 조회 불필요 (비정규화 덕분)

4. **친구 차단**
   - DynamoDB에서 `status`를 `blocked`로 변경
   - `blocked_at`, `blocked_reason` 추가

---

## 📝 설계 특징

### RDS (정규화)
- 사용자 기본 정보만 저장
- 중복 데이터 최소화
- 데이터 일관성 보장

### DynamoDB (비정규화)
- 친구 관계 + 친구 프로필 정보 함께 저장
- 빠른 조회 성능 (한 번의 쿼리)
- 로비 화면 최적화

### 트레이드오프
- **장점**: 로비 친구 목록 조회 시 매우 빠름 (1회 쿼리)
- **단점**: 사용자 프로필 변경 시 DynamoDB 친구 레코드도 업데이트 필요
- **해결**: 프로필 변경 빈도가 낮아 비정규화의 이점이 더 큼

---

## 🔍 주요 쿼리 패턴

### 1. 사용자 조회 (이메일)
```sql
-- RDS
SELECT * FROM users WHERE email = 'user@example.com';
```

### 2. 사용자 조회 (친구 코드)
```sql
-- RDS
SELECT * FROM users WHERE friend_code = 'ABC123';
```

### 3. 로비 친구 목록 조회
```python
# DynamoDB
response = table.query(
    KeyConditionExpression=Key('user_id').eq(user_id),
    FilterExpression=Attr('status').eq('accepted')
)
```

### 4. 차단한 사용자 목록
```python
# DynamoDB
response = table.query(
    KeyConditionExpression=Key('user_id').eq(user_id),
    FilterExpression=Attr('status').eq('blocked')
)
```

### 5. FCM 토큰 조회
```sql
-- RDS
SELECT token FROM users WHERE user_id = 'google-oauth2|123456';
```

---

## 📊 ERD 다이어그램 (Mermaid)

```mermaid
erDiagram
    USERS ||--o{ FRIENDS : "has"
    
    USERS {
        string user_id PK
        string email UK
        string nickname
        string profile_image_url
        string friend_code UK
        bigint created_at_timestamp
        bigint updated_at_timestamp
        string cat_pattern
        string cat_color
        string duress_code
        string meow_audio_url
        string duress_audio_url
        string token
        string provider
        boolean profile_setup_completed
    }
    
    FRIENDS {
        string user_id PK
        string friend_user_id SK
        string status
        number created_at
        number updated_at
        string email
        string nickname
        string profile_image_url
        string cat_pattern
        string cat_color
        string meow_audio_url
        string duress_code
        string duress_audio_url
        string daily_status
        number blocked_at
        string blocked_reason
    }
```

---

## 🔐 보안 고려사항

1. **RDS**
   - VPC 내부에서만 접근 가능
   - IAM 인증 사용
   - SSL/TLS 암호화 연결

2. **DynamoDB**
   - IAM 역할 기반 접근 제어
   - 암호화 저장 (at-rest)
   - VPC 엔드포인트 사용

3. **민감 정보**
   - `duress_code`: 위험 신호 코드 (암호화 권장)
   - `token`: FCM 토큰 (만료 관리 필요)

---

**문서 버전**: 1.0  
**최종 업데이트**: 2026-02-11
