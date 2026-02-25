# Gemini 고양이 캐릭터 생성 테스트 가이드

## 준비 단계

### 1. 패키지 설치

```bash
cd services/user_service
pip install -r requirements.txt
```

### 2. 환경 변수 확인

`.env` 파일에 다음이 설정되어 있는지 확인:

```bash
GEMINI_API_KEY=AIzaSyAfcTIQWy09akGQ8Y8oNpJpVD6RZfXIEms
```

## 테스트 방법

### 옵션 1: 배치 테스트 (추천) - 여러 이미지 자동 테스트

**터미널 1 - 서버 실행:**
```bash
cd services/user_service
python run_server.py
```

서버가 실행되면 다음과 같이 표시됩니다:
```
🚀 Starting User Service Server
📍 Server will run on: http://localhost:8000
📚 API Docs: http://localhost:8000/docs
```

**터미널 2 - 배치 테스트 실행:**
```bash
cd services/user_service
python test_gemini_batch.py
```

이 스크립트는:
- `C:\Users\JM\Desktop\사람얼굴테스트` 폴더의 모든 이미지 파일을 찾습니다
- 각 이미지로 고양이 캐릭터를 생성합니다
- 결과를 `generated_cats/` 폴더에 저장합니다
- 테스트 리포트를 생성합니다

### 옵션 2: 단일 이미지 테스트

**1. 테스트 이미지 복사:**
```bash
# 테스트할 이미지를 user_service 폴더로 복사
copy "C:\Users\JM\Desktop\사람얼굴테스트\사진1.jpg" services\user_service\test_photo.jpg
```

**2. 단일 테스트 실행:**
```bash
cd services/user_service
python test_gemini_cat_character.py
```

### 옵션 3: API 직접 호출 (cURL)

```bash
curl -X POST "http://localhost:8000/api/v1/cat-character/generate/b4589ddc-a001-7001-77aa-c2c3f3fd6a98" \
  -F "image=@C:\Users\JM\Desktop\사람얼굴테스트\사진1.jpg"
```

### 옵션 4: Swagger UI 사용

1. 브라우저에서 열기: http://localhost:8000/docs
2. `POST /api/v1/cat-character/generate/{user_id}` 엔드포인트 찾기
3. "Try it out" 클릭
4. user_id 입력: `b4589ddc-a001-7001-77aa-c2c3f3fd6a98`
5. 이미지 파일 선택
6. "Execute" 클릭

## 예상 결과

### 성공 시:

```json
{
  "success": true,
  "data": {
    "user_id": "b4589ddc-a001-7001-77aa-c2c3f3fd6a98",
    "original_url": "https://s3.../profiles/images/...",
    "generated_url": "https://s3.../cat-characters/...",
    "generated_image_base64": "iVBORw0KGgoAAAANSUhEUgAA..."
  },
  "message": "Cat character generated successfully"
}
```

생성된 이미지는:
- S3에 업로드됨 (`generated_url`)
- 로컬에 저장됨 (`generated_cats/` 폴더)

### 실패 시 - API 키 문제:

```
❌ Gemini API key not configured
```
→ `.env` 파일의 `GEMINI_API_KEY` 확인

### 실패 시 - 모델 지원 안 함:

```
❌ Model not found: gemini-2.0-flash-exp
```
→ 새 API 키 발급 필요 (https://aistudio.google.com/app/apikey)

### 실패 시 - 이미지 생성 실패:

```
❌ No image data in Gemini response
```
→ 프롬프트 문제 또는 API 제한, 다시 시도

## 생성 시간

- 일반적으로 30-60초 소요
- 이미지 크기와 복잡도에 따라 다름

## 결과 확인

### 배치 테스트 결과:

```
services/user_service/
├── generated_cats/
│   ├── 사진1_cat.png
│   ├── 사진2_cat.png
│   ├── 사진3_cat.png
│   └── test_report_20260224_153045.txt
```

### 테스트 리포트 예시:

```
Gemini Cat Character Test Report
================================================================================

Test Date: 2026-02-24 15:30:45
Total Tests: 3
Success: 3
Failed: 0

Detailed Results:
--------------------------------------------------------------------------------

File: 사진1.jpg
Status: ✅ Success
Time: 45.23s
Original URL: https://s3.../profiles/images/...
Generated URL: https://s3.../cat-characters/...
Output: generated_cats/사진1_cat.png
```

## 문제 해결

### 1. 서버가 시작되지 않음

```bash
# 포트가 이미 사용 중인지 확인
netstat -ano | findstr :8000

# 프로세스 종료
taskkill /PID <PID> /F
```

### 2. 패키지 설치 오류

```bash
# 가상환경 사용 (권장)
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. S3 업로드 실패

로컬 테스트에서는 S3 업로드가 실패할 수 있습니다.
하지만 base64 이미지는 여전히 반환되므로 로컬에 저장됩니다.

### 4. Gemini API 할당량 초과

```
❌ Quota exceeded
```
→ API 키의 일일 할당량 확인
→ 새 API 키 발급 또는 다음 날 재시도

## 다음 단계

테스트가 성공하면:

1. **EKS 배포 준비**
   - Secret에 GEMINI_API_KEY 추가
   - Docker 이미지 빌드 및 푸시
   - Deployment 업데이트

2. **프론트엔드 통합**
   - API 엔드포인트 연결
   - 이미지 업로드 UI 구현
   - 생성된 캐릭터 표시

3. **최적화**
   - 이미지 크기 최적화
   - 캐싱 구현
   - 에러 처리 개선

## 참고

- API 문서: http://localhost:8000/docs
- Gemini API 키: https://aistudio.google.com/app/apikey
- 가이드: GEMINI_CAT_CHARACTER_GUIDE.md
