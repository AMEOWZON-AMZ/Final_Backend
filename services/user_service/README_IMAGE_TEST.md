# Gemini 이미지 생성 테스트 가이드

## 📋 준비사항

### 1. 환경 변수 설정
`.env` 파일에 Gemini API 키가 설정되어 있어야 합니다:
```bash
GEMINI_API_KEY=your_api_key_here
```

### 2. 테스트 이미지 준비
`test_images/` 폴더에 테스트할 이미지를 넣어주세요:
```bash
mkdir -p test_images
# 이미지 파일을 test_images/ 폴더에 복사
```

지원 형식: `.jpg`, `.jpeg`, `.png`, `.webp`

---

## 🧪 테스트 방법

### 방법 1: 간단 테스트 (추천)
여러 이미지를 한 번에 테스트:
```bash
cd services/user_service
python test_gemini_image_simple.py
```

### 방법 2: 개별 이미지 테스트
특정 이미지 하나만 테스트:
```bash
cd services/user_service
python test_gemini_image.py test_images/person1.jpg
```

또는 대화형으로:
```bash
python test_gemini_image.py
# 이미지 경로 입력 프롬프트가 나타남
```

### 방법 3: API 엔드포인트 테스트
실제 API 서버를 통해 테스트:
```bash
# 먼저 서버 실행 (다른 터미널에서)
cd services/user_service
uvicorn app.main:app --reload

# 테스트 실행
python test_gemini_api.py
```

---

## 📂 결과 확인

생성된 이미지는 다음 위치에 저장됩니다:
```
services/user_service/test_output/
├── cat_person1.jpg
├── cat_person2.jpg
└── cat_person3.jpg
```

---

## 🔍 테스트 시나리오

### 1. 기본 테스트
- 사람 얼굴 사진 → 고양이 캐릭터 변환
- 생성 시간 측정
- 결과 이미지 저장

### 2. 다양한 입력 테스트
- 다양한 각도의 얼굴
- 다양한 표정
- 다양한 조명 조건
- 다양한 이미지 크기

### 3. 에러 처리 테스트
- 얼굴이 없는 이미지
- 손상된 이미지 파일
- 지원하지 않는 형식
- 타임아웃 (60초)

---

## ⚙️ 설정

### 타임아웃 조정
`app/services/gemini_image_service.py`:
```python
GEMINI_API_TIMEOUT = 60  # 초 단위
```

### 프롬프트 수정
`app/services/gemini_image_service.py`:
```python
CAT_CHARACTER_TRANSFORM_PROMPT = """
당신의 커스텀 프롬프트...
"""
```

---

## 📊 성능 지표

- **평균 생성 시간**: 10-30초
- **타임아웃**: 60초
- **지원 이미지 크기**: 최대 20MB
- **출력 형식**: JPEG

---

## 🐛 문제 해결

### API 키 오류
```
❌ GEMINI_API_KEY not configured
```
→ `.env` 파일에 API 키 설정 확인

### 타임아웃 오류
```
⏱️ Gemini API timeout after 60.0 seconds
```
→ 이미지 크기를 줄이거나 타임아웃 시간 증가

### 이미지 생성 실패
```
❌ Gemini returned text instead of image
```
→ 입력 이미지에 얼굴이 명확하게 보이는지 확인

---

## 📝 API 엔드포인트

### POST /api/v1/cat-character/generate
고양이 캐릭터 생성

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/cat-character/generate \
  -F "image=@test_images/person1.jpg"
```

**Response:**
```json
{
  "status": "success",
  "message": "Cat character generated successfully",
  "data": {
    "image_url": "https://s3.amazonaws.com/bucket/generated/cat_xxx.jpg"
  }
}
```

---

## 🎯 다음 단계

1. ✅ 로컬 테스트 완료
2. ✅ API 엔드포인트 테스트
3. ⬜ 프론트엔드 통합 테스트
4. ⬜ 성능 최적화
5. ⬜ 프로덕션 배포
