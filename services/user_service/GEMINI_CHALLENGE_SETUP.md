# Gemini 챌린지 자동 생성 설정 가이드

## 📋 개요

Gemini API를 사용하여 매달 챌린지를 자동 생성하는 기능입니다.

---

## 🚀 빠른 시작

### 1단계: Gemini API Key 발급

1. https://aistudio.google.com/app/apikey 접속
2. "Create API Key" 클릭
3. API Key 복사

### 2단계: 환경 변수 설정

#### 로컬 개발 (.env)
```bash
GEMINI_API_KEY=your_api_key_here
```

#### EC2 배포 (docker run)
```bash
docker run -d \
  -e GEMINI_API_KEY=your_api_key_here \
  ...
```

#### Kubernetes (secret.yaml)
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: user-service-secret
  namespace: user-service
stringData:
  GEMINI_API_KEY: "your_api_key_here"
```

### 3단계: 패키지 설치

```bash
cd services/user_service
pip install google-generativeai==0.3.2
```

---

## 📡 API 사용법

### 엔드포인트

```
POST /api/v1/challenges/generate-next-month
```

### 요청 예시

```bash
# 다음 달 챌린지 생성
curl -X POST http://43.203.213.35:8000/api/v1/challenges/generate-next-month
```

### 응답 예시

```json
{
  "success": true,
  "message": "Successfully generated 28 challenges for 2026-03",
  "data": {
    "year": 2026,
    "month": 3,
    "inserted": 28,
    "skipped": 0,
    "total": 28
  }
}
```

---

## 🔧 로컬 스크립트 실행

```bash
cd services/user_service

# 환경 변수 설정 (.env 파일 사용)
export $(cat .env | grep -v '^#' | xargs)

# 스크립트 실행
python generate_monthly_challenges.py
```

**출력 예시**:
```
🎯 Generating challenges for 2026-03
📅 Inserting 31 challenges...
✅ 2026-03-01: 소화기
✅ 2026-03-02: 엘리베이터 버튼
✅ 2026-03-03: 현관 발판
...
📊 Summary:
   Inserted: 31
   Skipped: 0
✅ Successfully generated 31 challenges!
```

---

## 📅 사용 시나리오

### 시나리오 1: 매달 1일 수동 실행

```bash
# 매달 1일에 실행
curl -X POST http://43.203.213.35:8000/api/v1/challenges/generate-next-month
```

### 시나리오 2: 미리 생성 (월말)

```bash
# 2월 28일에 3월 챌린지 미리 생성
curl -X POST http://43.203.213.35:8000/api/v1/challenges/generate-next-month
```

### 시나리오 3: 로컬에서 테스트

```bash
cd services/user_service
python generate_monthly_challenges.py
```

---

## 🎨 Gemini 프롬프트 커스터마이징

`generate_monthly_challenges.py` 파일의 `prompt` 변수를 수정하여 챌린지 스타일을 변경할 수 있습니다.

### 예시 1: 계절 테마 강조

```python
prompt = f"""
{year}년 {month}월 ({season}) 테마의 일일 사진 챌린지를 생성해주세요.

계절 특성:
- 봄: 꽃, 새싹, 따뜻한 날씨
- 여름: 시원한 것, 그늘, 물
- 가을: 단풍, 낙엽, 선선한 날씨
- 겨울: 눈, 따뜻한 것, 실내
"""
```

### 예시 2: 난이도 조절

```python
prompt = f"""
난이도별 챌린지 생성:
- 1-10일: 쉬움 (집 근처에서 찾을 수 있는 것)
- 11-20일: 보통 (외출 시 찾을 수 있는 것)
- 21-{days_in_month}일: 어려움 (특정 장소나 상황)
"""
```

---

## 🔍 생성된 챌린지 확인

### API로 확인

```bash
# 특정 날짜 챌린지 조회
curl "http://43.203.213.35:8000/api/v1/challenges/date/2026-03-01?user_id=test"
```

### DB에서 직접 확인

```sql
SELECT challenge_date, title, description 
FROM challenge_days 
WHERE challenge_date >= '2026-03-01' AND challenge_date <= '2026-03-31'
ORDER BY challenge_date;
```

---

## ⚠️ 주의사항

### 1. API Key 보안

- `.env` 파일을 Git에 커밋하지 마세요
- 프로덕션에서는 Secret으로 관리
- API Key 노출 시 즉시 재발급

### 2. 중복 방지

- 같은 날짜에 대해 여러 번 실행해도 안전 (ON CONFLICT DO NOTHING)
- 이미 존재하는 날짜는 자동으로 스킵

### 3. Gemini API 제한

- 무료 티어: 60 requests/minute
- 월 1회 실행이므로 제한 걱정 없음

---

## 💰 비용

- **Gemini API**: 무료 (Gemini 1.5 Flash)
- **월간 사용량**: 1회 (매달 1일)
- **예상 비용**: $0

---

## 🐛 트러블슈팅

### 에러 1: "GEMINI_API_KEY not configured"

**원인**: 환경 변수 미설정

**해결**:
```bash
# .env 파일에 추가
GEMINI_API_KEY=your_api_key_here

# 또는 직접 export
export GEMINI_API_KEY=your_api_key_here
```

### 에러 2: "google-generativeai package not installed"

**원인**: 패키지 미설치

**해결**:
```bash
pip install google-generativeai==0.3.2
```

### 에러 3: "No challenges generated"

**원인**: Gemini API 응답 파싱 실패

**해결**:
1. API Key 확인
2. 인터넷 연결 확인
3. 로그 확인 (`python generate_monthly_challenges.py`)

---

## 📝 체크리스트

배포 전 확인사항:

- [ ] Gemini API Key 발급
- [ ] 환경 변수 설정 (.env 또는 Secret)
- [ ] `google-generativeai` 패키지 설치
- [ ] 로컬 테스트 성공
- [ ] API 엔드포인트 테스트
- [ ] 생성된 챌린지 확인

---

## 🎯 다음 단계

### 선택 1: 수동 실행 유지

매달 1일에 API 호출:
```bash
curl -X POST http://43.203.213.35:8000/api/v1/challenges/generate-next-month
```

### 선택 2: 자동화 추가

**EC2 Cron**:
```bash
# crontab -e
0 0 1 * * curl -X POST http://localhost:8000/api/v1/challenges/generate-next-month
```

**GitHub Actions**:
```yaml
# .github/workflows/generate-challenges.yml
on:
  schedule:
    - cron: '0 15 L * *'  # 매달 마지막 날 00:00 KST
```

---

**작성일**: 2026-02-20
**버전**: 1.0.0
