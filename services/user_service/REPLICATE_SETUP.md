# Replicate API 설정 가이드

## Replicate란?
- **확실하게 작동하는** AI 이미지 생성 API
- Stable Diffusion 모델 완벽 지원
- 첫 50회 무료, 이후 이미지당 $0.01-0.02

## 1. Replicate 계정 생성

1. https://replicate.com 접속
2. "Sign up" 클릭
3. GitHub 계정으로 로그인 (또는 이메일로 가입)

## 2. API 토큰 발급

1. 로그인 후 https://replicate.com/account/api-tokens 접속
2. "Create token" 버튼 클릭
3. 토큰 이름 입력 (예: "cat-character-generator")
4. 생성된 토큰 복사 (예: `r8_...`)

## 3. 토큰 설정

`.env` 파일에 토큰 추가:

```env
REPLICATE_TOKEN=r8_your_token_here
```

## 4. 테스트

```bash
python test_simple.py
```

## 가격 정보

- **무료**: 첫 50회 요청
- **유료**: 이미지당 $0.01-0.02 (1-2센트)
- 예산: $10 = 약 500-1000개 이미지

## 사용 모델

- `stability-ai/stable-diffusion` (Stable Diffusion v1.5)
- 512x512 해상도
- 고품질 이미지 생성

## 참고 링크

- Replicate 홈페이지: https://replicate.com
- API 문서: https://replicate.com/docs
- 가격 정보: https://replicate.com/pricing
- Stable Diffusion 모델: https://replicate.com/stability-ai/stable-diffusion
