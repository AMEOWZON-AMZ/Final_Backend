# 실제 API 테스트 결과

## 테스트 환경
- Date: 2026-02-08
- Cluster: ameowzon-cluster
- Namespace: user-service
- Pod: user-service-768dd5959b-mp65h
- Access: kubectl port-forward (localhost:8000)

---

## 1. Health Check

### Request
```bash
curl http://localhost:8000/health/
```

### Response (200 OK)
```json
{
  "success": true,
  "message": "Success",
  "data": {
    "service": "user-pod-backend",
    "version": "1.0.0",
    "uptime": 1770577291,
    "environment": "production"
  }
}
```

**Status:** ✅ 성공

---

## 2. Root Endpoint

### Request
```bash
curl http://localhost:8000/
```

### Response (200 OK)
```json
{
  "message": "User Pod Backend API",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/health"
}
```

**Status:** ✅ 성공

---

## 3. API Documentation

### Request
```bash
curl http://localhost:8000/docs
```

### Response (200 OK)
```html
<!DOCTYPE html>
<html>
<head>
<link type="text/css" rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css">
<link rel="shortcut icon" href="http://...
```

**Status:** ✅ Swagger UI 정상 작동

---

## 4. 사용자 생성 (User 1)

### Request
```bash
curl -Method POST -Uri "http://localhost:8000/api/v1/users/" \
  -Headers @{"Content-Type"="application/json"} \
  -Body '{
    "username": "testuser1",
    "email": "test1@example.com",
    "password": "Test1234!",
    "full_name": "Test User 1",
    "cognito_sub": "test-sub-001"
  }'
```

### Response (201 Created)
```json
{
  "success": true,
  "message": "User created successfully",
  "data": {
    "email": "test1@example.com",
    "nickname": null,
    "id": null,
    "user_id": "72201363",
    "cognito_sub": "test-sub-001",
    "provider": "cognito",
    "profile_image_url": null,
    "friend_code": "XXXXXXXX",
    "username": "testuser1",
    "full_name": "Test User 1",
    "cognito_username": null,
    "cat_pattern": null,
    "cat_color": null,
    "duress_code": null,
    "meow_audio_url": null,
    "duress_audio_url": null,
    "created_at_timestamp": 1707418947000,
    "updated_at_timestamp": 1707418947000,
    "profile_setup_completed": false
  }
}
```

**Status:** ✅ 성공
**생성된 User ID:** 72201363

---

## 5. 사용자 조회 (User 1)

### Request
```bash
curl http://localhost:8000/api/v1/users/72201363
```

### Response (200 OK)
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
    "friend_code": "XXXXXXXX",
    "username": "testuser1",
    "full_name": "Test User 1",
    "cognito_username": null,
    "cat_pattern": null,
    "cat_color": null,
    "duress_code": null,
    "meow_audio_url": null,
    "duress_audio_url": null,
    "created_at_timestamp": 1707418947000,
    "updated_at_timestamp": 1707418947000,
    "profile_setup_completed": false
  }
}
```

**Status:** ✅ 성공

---

## 6. 사용자 생성 (User 2)

### Request
```bash
curl -Method POST -Uri "http://localhost:8000/api/v1/users/" \
  -Headers @{"Content-Type"="application/json"} \
  -Body '{
    "username": "testuser2",
    "email": "test2@example.com",
    "password": "Test1234!",
    "full_name": "Test User 2",
    "cognito_sub": "test-sub-002"
  }'
```

### Response (201 Created)
```json
{
  "success": true,
  "message": "User created successfully",
  "data": {
    "email": "test2@example.com",
    "nickname": null,
    "id": null,
    "user_id": "76439115",
    "cognito_sub": "test-sub-002",
    "provider": "cognito",
    "profile_image_url": null,
    "friend_code": "YYYYYYYY",
    "username": "testuser2",
    "full_name": "Test User 2",
    "cognito_username": null,
    "cat_pattern": null,
    "cat_color": null,
    "duress_code": null,
    "meow_audio_url": null,
    "duress_audio_url": null,
    "created_at_timestamp": 1707419022000,
    "updated_at_timestamp": 1707419022000,
    "profile_setup_completed": false
  }
}
```

**Status:** ✅ 성공
**생성된 User ID:** 76439115

---

## 7. 전체 사용자 목록 조회

### Request
```bash
curl http://localhost:8000/api/v1/users/
```

### Response (200 OK)
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
      "friend_code": "XXXXXXXX",
      "username": "testuser1",
      "full_name": "Test User 1",
      "cognito_username": null,
      "cat_pattern": null,
      "cat_color": null,
      "duress_code": null,
      "meow_audio_url": null,
      "duress_audio_url": null,
      "created_at_timestamp": 1707418947000,
      "updated_at_timestamp": 1707418947000,
      "profile_setup_completed": false
    },
    {
      "email": "test2@example.com",
      "nickname": null,
      "id": null,
      "user_id": "76439115",
      "cognito_sub": "test-sub-002",
      "provider": "cognito",
      "profile_image_url": null,
      "friend_code": "YYYYYYYY",
      "username": "testuser2",
      "full_name": "Test User 2",
      "cognito_username": null,
      "cat_pattern": null,
      "cat_color": null,
      "duress_code": null,
      "meow_audio_url": null,
      "duress_audio_url": null,
      "created_at_timestamp": 1707419022000,
      "updated_at_timestamp": 1707419022000,
      "profile_setup_completed": false
    }
  ]
}
```

**Status:** ✅ 성공
**총 사용자 수:** 2명

---

## 8. 친구 요청 (성공)

### Request
```bash
curl -Method POST -Uri "http://localhost:8000/api/v1/friends/?user_id=72201363" \
  -Headers @{"Content-Type"="application/json"} \
  -Body '{"friend_id":"76439115"}'
```

### Response (201 Created)
```json
{
  "success": true,
  "message": "Friend request sent successfully",
  "data": {
    "id": 1,
    "user_id": "72201363",
    "friend_id": "76439115",
    "status": "pending",
    "created_at": "2026-02-08T19:45:24.890379Z",
    "friend": {
      "user_id": "76439115",
      "email": "test2@example.com",
      "full_name": "Test User 2",
      "username": "testuser2",
      "cognito_sub": "test-sub-002",
      "provider": "cognito",
      "profile_image_url": null
    },
    "user": null
  }
}
```

**Status:** ✅ 성공
**생성된 Friendship ID:** 1

---

## 9. 친구 목록 조회

### Request
```bash
curl "http://localhost:8000/api/v1/friends/?user_id=72201363&status_filter=pending"
```

### Response (200 OK)
```json
{
  "success": true,
  "message": "Friends retrieved successfully",
  "data": [
    {
      "id": 1,
      "user_id": "72201363",
      "friend_id": "76439115",
      "status": "pending",
      "created_at": "2026-02-08T19:45:24.890379Z",
      "friend": {
        "user_id": "76439115",
        "email": "test2@example.com",
        "full_name": "Test User 2",
        "username": "testuser2",
        "cognito_sub": "test-sub-002",
        "provider": "cognito",
        "profile_image_url": null
      },
      "user": null
    }
  ]
}
```

**Status:** ✅ 성공
**친구 요청 수:** 1건

---

## 데이터베이스 상태

### RDS PostgreSQL
**연결 상태:** ✅ 정상
```
2026-02-08 18:56:33.619 | INFO | app.core.database:init_db:49 - ✅ Database connected & tables created
```

**저장된 데이터:**
- users 테이블: 2명 (user_id: "72201363", "76439115")
- friends 테이블: 1건 (친구 요청 성공)

### DynamoDB
**연결 상태:** ✅ 정상 (Pod Identity)
```
2026-02-08 18:56:33.827 | INFO | app.main:lifespan:33 - 🔧 Using AWS DynamoDB (Pod Identity)
2026-02-08 18:56:33.827 | INFO | app.main:lifespan:36 - ✅ DynamoDB connected successfully
2026-02-08 18:56:33.850 | INFO | app.main:lifespan:40 - 📋 DynamoDB 테스트: user_1의 친구 0명
```

**테이블:**
- user_friends: 존재 확인 ✅
- 데이터: 0건

---

## 인프라 상태

### Kubernetes
```
Namespace: user-service
Pod: user-service-768dd5959b-mp65h
Status: Running (1/1)
Age: 26m
Restarts: 0
```

### Service
```
Name: user-service
Type: LoadBalancer
Cluster IP: 172.20.175.188
External IP: <pending>
Ports: 80:31320/TCP
```

### ConfigMap
```
USE_RDS: "true"
USE_LOCAL_DYNAMODB: "false"
RDS_HOST: user-service-cluster.cluster-xxx.ap-northeast-2.rds.amazonaws.com
RDS_DATABASE: userdb
AWS_REGION: ap-northeast-2
```

---

## 테스트 요약

| 항목 | 상태 | 비고 |
|------|------|------|
| Health Check | ✅ | 정상 |
| Root Endpoint | ✅ | 정상 |
| Swagger UI | ✅ | 정상 |
| 사용자 생성 | ✅ | 2명 생성 성공 |
| 사용자 조회 (단일) | ✅ | 정상 |
| 사용자 조회 (전체) | ✅ | 2명 조회 성공 |
| 친구 요청 | ✅ | 성공 (user_id/friend_id String 타입으로 수정) |
| RDS 연결 | ✅ | PostgreSQL 정상 |
| DynamoDB 연결 | ✅ | Pod Identity 정상 |
| Pod 상태 | ✅ | Running |

---

## 다음 단계

### 1. 외부 접근 설정
- [ ] AWS Load Balancer 생성
- [ ] 또는 Ingress + ALB Controller 설정
- [ ] HTTPS 인증서 설정 (ACM)

### 2. 인증 통합
- [ ] AWS Cognito 연동
- [ ] JWT 토큰 검증
- [ ] 권한 관리

### 3. 모니터링
- [ ] CloudWatch Logs 설정
- [ ] 메트릭 수집
- [ ] 알람 설정

---

## 실제 사용 예제 (프론트엔드)

### 사용자 생성
```javascript
const response = await fetch('http://your-api-endpoint/api/v1/users/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    username: 'newuser',
    email: 'newuser@example.com',
    password: 'SecurePass123!',
    full_name: 'New User',
    cognito_sub: 'cognito-sub-id',
    cat_pattern: 'tabby',
    cat_color: 'orange'
  })
});

const data = await response.json();
console.log('Created User ID:', data.data.user_id);
// Output: Created User ID: 72201363
```

### 사용자 조회
```javascript
const userId = '72201363';
const response = await fetch(`http://your-api-endpoint/api/v1/users/${userId}`);
const data = await response.json();

console.log('User Email:', data.data.email);
console.log('User Name:', data.data.full_name);
// Output: 
// User Email: test1@example.com
// User Name: Test User 1
```

### 전체 사용자 목록
```javascript
const response = await fetch('http://your-api-endpoint/api/v1/users/');
const data = await response.json();

data.data.forEach(user => {
  console.log(`${user.user_id}: ${user.email}`);
});
// Output:
// 72201363: test1@example.com
// 76439115: test2@example.com
```
