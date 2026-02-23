# User Service API 문서

## Base URL
```
http://localhost:8000  (개발 - port-forward)
http://<LOAD-BALANCER-DNS>  (프로덕션)
```

## 공통 응답 형식

### 성공 응답
```json
{
  "success": true,
  "message": "Success",
  "data": { ... }
}
```

### 에러 응답
```json
{
  "success": false,
  "message": "Error message",
  "error_code": "ERROR_CODE",
  "details": { ... }
}
```

---

## 1. Health Check

### GET /health/
서버 상태 확인

**Request:**
```bash
curl http://localhost:8000/health/
```

**Response:**
```json
{
  "success": true,
  "message": "Success",
  "data": {
    "service": "user-pod-backend",
    "version": "1.0.0",
    "uptime": 1770578618,
    "environment": "production"
  }
}
```

---

## 2. 사용자 관리

### POST /api/v1/users/
사용자 생성

**Request:**
```json
{
  "email": "test@example.com",
  "username": "testuser",
  "password": "Test1234!",
  "full_name": "Test User",
  "cognito_sub": "test-sub-001",
  "provider": "cognito",
  "profile_image_url": "https://example.com/image.jpg",
  "cat_pattern": "tabby",
  "cat_color": "orange",
  "duress_code": "HELP123",
  "meow_audio_url": "https://example.com/meow.mp3"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "User created successfully",
  "data": {
    "email": "test@example.com",
    "nickname": null,
    "id": null,
    "user_id": "72201363",
    "cognito_sub": "test-sub-001",
    "provider": "cognito",
    "profile_image_url": "https://example.com/image.jpg",
    "friend_code": "ABC12345",
    "username": "testuser",
    "full_name": "Test User",
    "cat_pattern": "tabby",
    "cat_color": "orange",
    "duress_code": "HELP123",
    "meow_audio_url": "https://example.com/meow.mp3",
    "created_at_timestamp": 1707418947000,
    "updated_at_timestamp": 1707418947000,
    "profile_setup_completed": false
  }
}
```

### GET /api/v1/users/
모든 사용자 조회

**Request:**
```bash
curl http://localhost:8000/api/v1/users/
```

**Response:**
```json
{
  "success": true,
  "message": "Users retrieved successfully",
  "data": [
    {
      "email": "test1@example.com",
      "nickname": null,
      "id": null,
      "user_id": "72201363",
      "cognito_sub": "test-sub-001",
      "provider": "cognito",
      "profile_image_url": null,
      "friend_code": "ABC12345",
      "username": "testuser1",
      "full_name": "Test User 1",
      "cat_pattern": null,
      "cat_color": null,
      "duress_code": null,
      "meow_audio_url": null,
      "created_at_timestamp": 1707418947000,
      "updated_at_timestamp": 1707418947000,
      "profile_setup_completed": false
    }
  ]
}
```

### GET /api/v1/users/{user_id}
특정 사용자 조회

**Request:**
```bash
curl http://localhost:8000/api/v1/users/72201363
```

**Response:**
```json
{
  "success": true,
  "message": "User retrieved successfully",
  "data": {
    "email": "test1@example.com",
    "nickname": null,
    "id": null,
    "user_id": "72201363",
    "cognito_sub": "test-sub-001",
    "provider": "cognito",
    "profile_image_url": null,
    "friend_code": "ABC12345",
    "username": "testuser1",
    "full_name": "Test User 1",
    "cat_pattern": null,
    "cat_color": null,
    "duress_code": null,
    "meow_audio_url": null,
    "created_at_timestamp": 1707418947000,
    "updated_at_timestamp": 1707418947000,
    "profile_setup_completed": false
  }
}
```

### PUT /api/v1/users/{user_id}
사용자 정보 수정

**Request:**
```json
{
  "nickname": "새로운닉네임",
  "profile_image_url": "https://example.com/new-image.jpg",
  "cat_pattern": "striped",
  "cat_color": "gray",
  "duress_code": "HELP999",
  "meow_audio_url": "https://example.com/new-meow.mp3"
}
```

**Response:**
```json
{
  "success": true,
  "message": "User updated successfully",
  "data": {
    "email": "test1@example.com",
    "nickname": "새로운닉네임",
    "user_id": "72201363",
    "profile_image_url": "https://example.com/new-image.jpg",
    "cat_pattern": "striped",
    "cat_color": "gray",
    "duress_code": "HELP999",
    "meow_audio_url": "https://example.com/new-meow.mp3",
    "updated_at_timestamp": 1707419000000
  }
}
```

### DELETE /api/v1/users/{user_id}
사용자 삭제

**Request:**
```bash
curl -X DELETE http://localhost:8000/api/v1/users/72201363
```

**Response:**
```json
{
  "success": true,
  "message": "User deleted successfully"
}
```

---

## 3. 인증 (Authentication)

### POST /api/v1/users/signup
회원가입

**Request:**
```json
{
  "email": "newuser@example.com",
  "password": "SecurePass123!",
  "nickname": "고양이집사",
  "full_name": "김철수",
  "cat_pattern": "tabby",
  "cat_color": "orange",
  "meow_audio_url": "https://s3.amazonaws.com/bucket/meow.mp3",
  "duress_code": "HELP123",
  "duress_audio_url": "https://s3.amazonaws.com/bucket/duress.mp3",
  "profile_image_url": "https://s3.amazonaws.com/bucket/profile.jpg"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "user_id": "12345678",
    "email": "newuser@example.com",
    "nickname": "고양이집사",
    "friend_code": "XYZ98765",
    "cat_pattern": "tabby",
    "cat_color": "orange",
    "profile_setup_completed": true
  }
}
```

### POST /api/v1/users/login
로그인 및 로비 정보 조회

**Headers:**
```
Authorization: Bearer <JWT_TOKEN>
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "user_profile": {
      "user_id": "12345678",
      "cognito_sub": "cognito-sub-id",
      "email": "user@example.com",
      "nickname": "고양이집사",
      "provider": "cognito",
      "profile_image_url": "https://example.com/profile.jpg",
      "friend_code": "XYZ98765",
      "cat_pattern": "tabby",
      "cat_color": "orange",
      "duress_code": "HELP123",
      "meow_audio_url": "https://example.com/meow.mp3",
      "created_at_timestamp": 1707418947000,
      "updated_at_timestamp": 1707418947000
    },
    "lobby_friends": [
      {
        "friend_id": 1,
        "user_id": "87654321",
        "nickname": "친구1",
        "cat_profile": {
          "pattern": "striped",
          "color": "gray",
          "image_url": "https://example.com/cat1.jpg"
        }
      }
    ],
    "total_friends": 5
  }
}
```

### POST /api/v1/users/logout
로그아웃

**Headers:**
```
Authorization: Bearer <JWT_TOKEN>
```

**Response:**
```json
{
  "success": true,
  "message": "Logout successful"
}
```

### GET /api/v1/users/me
내 프로필 조회

**Headers:**
```
Authorization: Bearer <JWT_TOKEN>
```

**Response:**
```json
{
  "success": true,
  "message": "Profile retrieved successfully",
  "data": {
    "user_id": "12345678",
    "cognito_sub": "cognito-sub-id",
    "email": "user@example.com",
    "nickname": "고양이집사",
    "provider": "cognito",
    "profile_image_url": "https://example.com/profile.jpg",
    "friend_code": "XYZ98765",
    "cat_pattern": "tabby",
    "cat_color": "orange",
    "duress_code": "HELP123",
    "meow_audio_url": "https://example.com/meow.mp3",
    "created_at_timestamp": 1707418947000,
    "updated_at_timestamp": 1707418947000
  }
}
```

---

## 4. 친구 관리

### POST /api/v1/friends/
친구 추가 요청 (레거시)

**Query Parameters:**
- `user_id`: 요청하는 사용자 ID (String, 8자리 숫자)

**Request:**
```json
{
  "friend_id": "76439115"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Friend request sent successfully",
  "data": {
    "id": 1,
    "user_id": "72201363",
    "friend_id": "76439115",
    "status": "pending",
    "created_at": "2026-02-08T19:00:00Z",
    "friend": {
      "user_id": "76439115",
      "email": "friend@example.com",
      "full_name": "Friend User",
      "username": "frienduser",
      "cognito_sub": "friend-sub-002",
      "provider": "cognito",
      "profile_image_url": null
    }
  }
}
```

### GET /api/v1/friends/
사용자의 친구 목록 조회 (레거시)

**Query Parameters:**
- `user_id`: 사용자 ID (String, 8자리 숫자)
- `status_filter`: 상태 필터 (기본값: "accepted")

**Request:**
```bash
curl "http://localhost:8000/api/v1/friends/?user_id=72201363&status_filter=accepted"
```

**Response:**
```json
{
  "success": true,
  "message": "Friends retrieved successfully",
  "data": [
    {
      "id": 1,
      "user_id": "72201363",
      "friend_id": "76439115",
      "status": "accepted",
      "created_at": "2026-02-08T19:00:00Z",
      "friend": {
        "user_id": "76439115",
        "email": "friend@example.com",
        "full_name": "Friend User",
        "username": "frienduser",
        "cognito_sub": "friend-sub-002",
        "provider": "cognito",
        "profile_image_url": null
      }
    }
  ]
}
```

### POST /api/v1/friends/add-friend
친구 추가 요청 (인증 필요)

**Headers:**
```
Authorization: Bearer <JWT_TOKEN>
```

**Request:**
```json
{
  "friend_id": "76439115"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Friend request sent successfully",
  "data": {
    "id": 1,
    "user_id": "72201363",
    "friend_id": "76439115",
    "status": "pending",
    "created_at": "2026-02-08T19:00:00Z"
  }
}
```

### GET /api/v1/friends/my-friends
내 친구 목록 조회 (인증 필요)

**Headers:**
```
Authorization: Bearer <JWT_TOKEN>
```

**Query Parameters:**
- `status_filter`: 상태 필터 (기본값: "accepted")

**Response:**
```json
{
  "success": true,
  "message": "Friends retrieved successfully",
  "data": [
    {
      "id": 1,
      "user_id": "72201363",
      "friend_id": "76439115",
      "status": "accepted",
      "created_at": "2026-02-08T19:00:00Z",
      "friend": {
        "user_id": "76439115",
        "email": "friend@example.com",
        "full_name": "Friend User"
      }
    }
  ]
}
```

### GET /api/v1/friends/pending-requests
받은 친구 요청 목록 (인증 필요)

**Headers:**
```
Authorization: Bearer <JWT_TOKEN>
```

**Response:**
```json
{
  "success": true,
  "message": "Pending requests retrieved successfully",
  "data": [
    {
      "id": 2,
      "user_id": "87654321",
      "friend_id": "72201363",
      "status": "pending",
      "created_at": "2026-02-08T19:00:00Z",
      "user": {
        "user_id": "87654321",
        "email": "requester@example.com",
        "full_name": "Requester User"
      }
    }
  ]
}
```

### PUT /api/v1/friends/{friendship_id}
친구 관계 상태 업데이트 (수락/거절/차단)

**Headers:**
```
Authorization: Bearer <JWT_TOKEN>
```

**Request:**
```json
{
  "status": "accepted"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Friendship status updated successfully",
  "data": {
    "id": 1,
    "user_id": "72201363",
    "friend_id": "76439115",
    "status": "accepted",
    "created_at": "2026-02-08T19:00:00Z"
  }
}
```

### DELETE /api/v1/friends/{friendship_id}
친구 관계 삭제

**Headers:**
```
Authorization: Bearer <JWT_TOKEN>
```

**Response:**
```json
{
  "success": true,
  "message": "Friendship removed successfully"
}
```

### POST /api/v1/users/friend-request
친구 코드로 친구 요청

**Headers:**
```
Authorization: Bearer <JWT_TOKEN>
```

**Request:**
```json
{
  "friend_code": "ABC12345"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Friend request sent",
  "data": {
    "friendship_id": 1,
    "friend_user_id": "76439115",
    "status": "pending"
  }
}
```

### GET /api/v1/users/friend-code/{friend_code}
친구 코드로 사용자 조회

**Request:**
```bash
curl http://localhost:8000/api/v1/users/friend-code/ABC12345
```

**Response:**
```json
{
  "success": true,
  "message": "User found",
  "data": {
    "user_id": "72201363",
    "nickname": "고양이집사",
    "profile_image_url": "https://example.com/profile.jpg",
    "cat_pattern": "tabby",
    "cat_color": "orange"
  }
}
```

---

## 5. 로비 & 프로필

### GET /api/v1/users/lobby
로비 친구 목록 조회 (인증 필요)

**Headers:**
```
Authorization: Bearer <JWT_TOKEN>
```

**Response:**
```json
{
  "success": true,
  "message": "Lobby friends retrieved",
  "data": {
    "friends": [
      {
        "friend_id": 1,
        "user_id": "87654321",
        "nickname": "친구1",
        "cat_profile": {
          "pattern": "striped",
          "color": "gray",
          "image_url": "https://example.com/cat1.jpg"
        }
      }
    ],
    "total": 5
  }
}
```

### GET /api/v1/users/{user_id}/lobby
특정 사용자의 로비 친구 목록

**Request:**
```bash
curl http://localhost:8000/api/v1/users/72201363/lobby
```

**Response:**
```json
{
  "success": true,
  "message": "Lobby friends retrieved",
  "data": {
    "friends": [
      {
        "friend_id": 1,
        "user_id": "87654321",
        "nickname": "친구1",
        "cat_profile": {
          "pattern": "striped",
          "color": "gray",
          "image_url": null
        }
      }
    ],
    "total": 5
  }
}
```

### POST /api/v1/users/profile/setup
프로필 설정 (인증 필요)

**Headers:**
```
Authorization: Bearer <JWT_TOKEN>
```

**Request:**
```json
{
  "nickname": "고양이집사",
  "cat_pattern": "tabby",
  "cat_color": "orange",
  "duress_code": "HELP123",
  "meow_audio_url": "https://example.com/meow.mp3"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Profile setup completed",
  "data": {
    "user_id": "12345678",
    "nickname": "고양이집사",
    "cat_pattern": "tabby",
    "cat_color": "orange",
    "profile_setup_completed": true
  }
}
```

### POST /api/v1/users/sync
프로필 동기화 (인증 필요)

**Headers:**
```
Authorization: Bearer <JWT_TOKEN>
```

**Response:**
```json
{
  "success": true,
  "message": "Profile synced",
  "data": {
    "user_id": "12345678",
    "email": "user@example.com",
    "nickname": "고양이집사",
    "friend_code": "XYZ98765",
    "cat_pattern": "tabby",
    "cat_color": "orange",
    "updated_at_timestamp": 1707419000000
  }
}
```

---

## 6. 검색

### GET /api/v1/users/search
사용자 검색

**Query Parameters:**
- `q`: 검색어 (이메일 또는 닉네임)

**Request:**
```bash
curl "http://localhost:8000/api/v1/users/search?q=test"
```

**Response:**
```json
{
  "success": true,
  "message": "Users found",
  "data": [
    {
      "user_id": "72201363",
      "email": "test@example.com",
      "nickname": "testuser",
      "profile_image_url": null
    }
  ]
}
```

---

## 에러 코드

| 코드 | 설명 |
|------|------|
| `USER_NOT_FOUND` | 사용자를 찾을 수 없음 |
| `USER_ALREADY_EXISTS` | 이미 존재하는 사용자 |
| `FRIEND_REQUEST_ERROR` | 친구 요청 실패 |
| `FRIENDSHIP_NOT_FOUND` | 친구 관계를 찾을 수 없음 |
| `FORBIDDEN` | 권한 없음 |
| `INVALID_TOKEN` | 유효하지 않은 토큰 |
| `VALIDATION_ERROR` | 입력 데이터 검증 실패 |

---

## 테스트 예제

### 1. 사용자 생성 및 조회
```bash
# 사용자 생성
curl -X POST http://localhost:8000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "Test1234!",
    "full_name": "Test User",
    "cognito_sub": "test-sub-001"
  }'

# 사용자 조회
curl http://localhost:8000/api/v1/users/72201363
```

### 2. 친구 추가 플로우
```bash
# 1. 친구 코드로 사용자 검색
curl http://localhost:8000/api/v1/users/friend-code/ABC12345

# 2. 친구 요청 보내기
curl -X POST http://localhost:8000/api/v1/friends/?user_id=72201363 \
  -H "Content-Type: application/json" \
  -d '{"friend_id": "76439115"}'

# 3. 친구 요청 수락
curl -X PUT http://localhost:8000/api/v1/friends/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "accepted"}'

# 4. 친구 목록 확인
curl "http://localhost:8000/api/v1/friends/?user_id=72201363&status_filter=accepted"
```

---

## 데이터베이스

### RDS PostgreSQL
- 사용자 정보 (users 테이블)
- 친구 관계 (friends 테이블)

### DynamoDB
- 친구 관계 캐시 (user_friends 테이블)
- 실시간 친구 상태

---

## 인증 방식

현재는 **인증 없이** 테스트 가능하지만, 프로덕션에서는:
- AWS Cognito JWT 토큰 필요
- Authorization Header: `Bearer <JWT_TOKEN>`
- 일부 엔드포인트는 인증 필수 (`/api/v1/users/me`, `/api/v1/friends/my-friends` 등)
