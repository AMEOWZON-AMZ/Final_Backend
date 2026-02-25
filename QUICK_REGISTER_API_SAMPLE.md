# Quick Register API 데이터 포맷 샘플

## 엔드포인트
```
POST /api/v1/quick/register
Content-Type: multipart/form-data
```

## 요청 데이터 (Request)

### 1. 최소 요청 (닉네임만)
```javascript
const formData = new FormData();
formData.append('nickname', '새친구');

// target_user_id 생략 시 자동으로 시연용 고정값 사용
// 고정값: 44082dbc-b071-70c4-4794-81b840c61c4e
```

### 2. 기본 정보 포함
```javascript
const formData = new FormData();
formData.append('nickname', '냥냥이');
formData.append('phone_number', '010-1234-5678');
formData.append('cat_pattern', 'stripe');
formData.append('cat_color', '#FFD700');
```

### 3. 음성 파일 포함 (완전한 요청)
```javascript
const formData = new FormData();
formData.append('nickname', '귀여운냥이');
formData.append('phone_number', '010-9876-5432');
formData.append('cat_pattern', 'solid');
formData.append('cat_color', '#FF6B6B');
formData.append('meow_audio', meowAudioFile);  // File object (audio/webm, audio/mp3 등)
formData.append('duress_audio', duressAudioFile);  // File object
```

### 4. 특정 사용자와 친구 등록 (target_user_id 지정)
```javascript
const formData = new FormData();
formData.append('nickname', '친구냥');
formData.append('target_user_id', 'abc123-def456-...');  // 특정 사용자 ID
formData.append('phone_number', '010-1111-2222');
```

## 요청 파라미터 상세

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| nickname | string | ✅ | - | 사용자 닉네임 |
| target_user_id | string | ❌ | 44082dbc-b071-70c4-4794-81b840c61c4e | 친구로 등록할 대상 사용자 ID (시연용 고정값) |
| phone_number | string | ❌ | null | 전화번호 (010-1234-5678 형식) |
| cat_pattern | string | ❌ | "solid" | 고양이 무늬 (solid, stripe, spot 등) |
| cat_color | string | ❌ | "#FF6B6B" | 고양이 색상 (HEX 코드) |
| meow_audio | File | ❌ | null | 야옹 소리 음성 파일 |
| duress_audio | File | ❌ | null | 위험 신호 음성 파일 |

## 응답 데이터 (Response)

### 성공 응답 (200 OK)
```json
{
  "success": true,
  "message": "환영합니다! 냥집사님과 친구가 되었습니다.",
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "nickname": "새친구",
  "friend_code": "ABC123",
  "friend_added": true,
  "target_nickname": "냥집사",
  "meow_audio_url": "https://ameowzon-test-files.s3.ap-northeast-2.amazonaws.com/audio/meow/a1b2c3d4-e5f6-7890-abcd-ef1234567890.webm",
  "duress_audio_url": "https://ameowzon-test-files.s3.ap-northeast-2.amazonaws.com/audio/duress/a1b2c3d4-e5f6-7890-abcd-ef1234567890.webm"
}
```

### 성공 응답 (음성 파일 없음)
```json
{
  "success": true,
  "message": "환영합니다! 냥집사님과 친구가 되었습니다.",
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "nickname": "새친구",
  "friend_code": "ABC123",
  "friend_added": true,
  "target_nickname": "냥집사",
  "meow_audio_url": null,
  "duress_audio_url": null
}
```

### 친구 등록 실패 (사용자는 생성됨)
```json
{
  "success": true,
  "message": "계정이 생성되었습니다. (친구 등록 실패: 나중에 다시 시도해주세요)",
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "nickname": "새친구",
  "friend_code": "ABC123",
  "friend_added": false,
  "target_nickname": null,
  "meow_audio_url": null,
  "duress_audio_url": null
}
```

### 에러 응답 (400 Bad Request)
```json
{
  "detail": "Nickname is required"
}
```

### 에러 응답 (500 Internal Server Error)
```json
{
  "detail": "Failed to register user"
}
```

## 실제 사용 예제

### JavaScript (Fetch API)
```javascript
async function quickRegister(nickname, meowAudio, duressAudio) {
  const formData = new FormData();
  formData.append('nickname', nickname);
  
  // 선택 사항
  if (meowAudio) {
    formData.append('meow_audio', meowAudio);
  }
  if (duressAudio) {
    formData.append('duress_audio', duressAudio);
  }
  
  try {
    const response = await fetch(
      'http://k8s-userserv-userserv-faeaf14223-576848475.ap-northeast-2.elb.amazonaws.com/api/v1/quick/register',
      {
        method: 'POST',
        body: formData
      }
    );
    
    const data = await response.json();
    
    if (data.success) {
      console.log('등록 성공!');
      console.log('User ID:', data.user_id);
      console.log('Friend Code:', data.friend_code);
      console.log('친구 추가:', data.friend_added ? '성공' : '실패');
    }
    
    return data;
  } catch (error) {
    console.error('등록 실패:', error);
    throw error;
  }
}

// 사용 예
const meowFile = document.getElementById('meowInput').files[0];
const duressFile = document.getElementById('duressInput').files[0];
quickRegister('냥냥이', meowFile, duressFile);
```

### cURL 예제
```bash
# 최소 요청 (닉네임만)
curl -X POST \
  http://k8s-userserv-userserv-faeaf14223-576848475.ap-northeast-2.elb.amazonaws.com/api/v1/quick/register \
  -F "nickname=새친구"

# 기본 정보 포함
curl -X POST \
  http://k8s-userserv-userserv-faeaf14223-576848475.ap-northeast-2.elb.amazonaws.com/api/v1/quick/register \
  -F "nickname=냥냥이" \
  -F "phone_number=010-1234-5678" \
  -F "cat_pattern=stripe" \
  -F "cat_color=#FFD700"

# 음성 파일 포함
curl -X POST \
  http://k8s-userserv-userserv-faeaf14223-576848475.ap-northeast-2.elb.amazonaws.com/api/v1/quick/register \
  -F "nickname=귀여운냥이" \
  -F "phone_number=010-9876-5432" \
  -F "meow_audio=@meow.webm" \
  -F "duress_audio=@duress.webm"
```

### Python (requests)
```python
import requests

url = "http://k8s-userserv-userserv-faeaf14223-576848475.ap-northeast-2.elb.amazonaws.com/api/v1/quick/register"

# 최소 요청
data = {
    'nickname': '새친구'
}
response = requests.post(url, data=data)
print(response.json())

# 음성 파일 포함
files = {
    'meow_audio': open('meow.webm', 'rb'),
    'duress_audio': open('duress.webm', 'rb')
}
data = {
    'nickname': '냥냥이',
    'phone_number': '010-1234-5678',
    'cat_pattern': 'stripe',
    'cat_color': '#FFD700'
}
response = requests.post(url, data=data, files=files)
print(response.json())
```

## 응답 필드 설명

| 필드 | 타입 | 설명 |
|------|------|------|
| success | boolean | 요청 성공 여부 |
| message | string | 사용자에게 표시할 메시지 |
| user_id | string | 생성된 사용자 ID (UUID) |
| nickname | string | 사용자 닉네임 |
| friend_code | string | 친구 코드 (6자리) |
| friend_added | boolean | 친구 등록 성공 여부 |
| target_nickname | string \| null | 대상 사용자 닉네임 (친구 등록 성공 시) |
| meow_audio_url | string \| null | 야옹 소리 S3 URL |
| duress_audio_url | string \| null | 위험 신호 S3 URL |

## 주의사항

1. **시연용 고정값**: target_user_id를 전달하지 않으면 자동으로 `44082dbc-b071-70c4-4794-81b840c61c4e`와 친구 등록됩니다.

2. **음성 파일 형식**: 
   - 지원 형식: audio/webm, audio/mp3, audio/wav, audio/ogg
   - 최대 크기: 10MB (설정에 따라 다를 수 있음)

3. **전화번호 형식**: 
   - 권장 형식: 010-1234-5678
   - 하이픈 포함/미포함 모두 가능

4. **고양이 색상**: 
   - HEX 코드 형식 (#RRGGBB)
   - 예: #FF6B6B, #FFD700, #4ECDC4

5. **친구 등록 실패**: 
   - 사용자는 생성되지만 친구 등록만 실패할 수 있음
   - friend_added 필드로 확인 가능
