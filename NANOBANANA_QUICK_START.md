# Nanobanana 통합 빠른 시작 가이드

## 🎯 목표

사용자가 업로드한 사진을 Nanobanana API를 통해 AI 고양이 이미지로 변환

## 📋 준비사항

1. **Nanobanana API 키 발급**
   - Nanobanana 웹사이트에서 계정 생성
   - API 키 발급 받기
   - API 엔드포인트 URL 확인

2. **필요한 정보**
   - API URL: `https://api.nanobanana.com/v1` (예시)
   - API Key: `your_api_key_here`

## 🚀 설정 단계

### 1단계: 환경 변수 설정

**로컬 개발 (.env)**
```bash
# services/user_service/.env 파일에 추가
NANOBANANA_API_URL=https://api.nanobanana.com/v1
NANOBANANA_API_KEY=your_nanobanana_api_key_here
```

**EKS 배포 (k8s/secret.yaml)**
```yaml
# k8s/secret.yaml 파일에 추가
apiVersion: v1
kind: Secret
metadata:
  name: user-service-secret
  namespace: user-service
type: Opaque
stringData:
  # ... 기존 설정 유지 ...
  
  # Nanobanana API 추가
  NANOBANANA_API_URL: "https://api.nanobanana.com/v1"
  NANOBANANA_API_KEY: "your_nanobanana_api_key_here"
```

### 2단계: Deployment 업데이트

**k8s/deployment.yaml**의 env 섹션에 추가:
```yaml
env:
  # ... 기존 환경 변수 유지 ...
  
  # Nanobanana API 추가
  - name: NANOBANANA_API_URL
    valueFrom:
      secretKeyRef:
        name: user-service-secret
        key: NANOBANANA_API_URL
  - name: NANOBANANA_API_KEY
    valueFrom:
      secretKeyRef:
        name: user-service-secret
        key: NANOBANANA_API_KEY
```

### 3단계: Secret 적용 및 배포

```bash
# 1. Secret 업데이트
kubectl apply -f k8s/secret.yaml

# 2. Deployment 업데이트
kubectl apply -f k8s/deployment.yaml

# 3. Pod 재시작 (환경 변수 적용)
kubectl rollout restart deployment/user-service -n user-service

# 4. 상태 확인
kubectl get pods -n user-service
kubectl logs -f deployment/user-service -n user-service
```

## 📡 API 사용법

### 방법 1: 이미지 파일 직접 업로드

```bash
curl -X POST "http://your-api-url/api/v1/cats/generate/USER_ID" \
  -H "Content-Type: multipart/form-data" \
  -F "image=@photo.jpg" \
  -F "cat_pattern=tabby" \
  -F "cat_color=orange"
```

**응답:**
```json
{
  "success": true,
  "data": {
    "user_id": "USER_ID",
    "original_url": "https://s3.../original.jpg",
    "generated_url": "https://nanobanana.../generated.jpg",
    "cat_pattern": "tabby",
    "cat_color": "orange"
  }
}
```

### 방법 2: S3 URL로 생성

```bash
curl -X POST "http://your-api-url/api/v1/cats/generate-from-url/USER_ID" \
  -d "image_url=https://s3.amazonaws.com/bucket/image.jpg" \
  -d "cat_pattern=calico" \
  -d "cat_color=multicolor"
```

## 🔄 통합 시나리오

### 시나리오 A: 회원가입 시 자동 생성

```
1. 사용자 회원가입 (POST /api/v1/users/signup)
   → 프로필 이미지 S3 저장
   
2. AI 이미지 생성 (POST /api/v1/cats/generate-from-url/{user_id})
   → Nanobanana로 고양이 이미지 생성
   
3. 생성된 URL을 사용자 프로필에 저장
   → 앱에서 AI 고양이 이미지 표시
```

### 시나리오 B: 프로필 수정 시 재생성

```
1. 사용자가 새 사진 업로드 (PUT /api/v1/users/profile/{user_id})
   
2. AI 이미지 재생성 (POST /api/v1/cats/generate/{user_id})
   
3. 새 이미지 표시
```

### 시나리오 C: 챌린지 제출 시 변환

```
1. 챌린지 사진 제출 (POST /api/v1/challenges/{id}/submit)
   → 원본 이미지 S3 저장
   
2. AI 변환 (POST /api/v1/cats/generate-from-url/{user_id})
   
3. 원본 + AI 이미지 모두 표시
```

## 🧪 테스트

### 로컬 테스트

```bash
# 1. 로컬 서버 실행
cd services/user_service
uvicorn app.main:app --reload --port 8000

# 2. 테스트 스크립트 실행
python test_nanobanana.py
```

### EKS 테스트

```bash
# 1. EKS 엔드포인트 확인
kubectl get ingress -n user-service

# 2. API 테스트
curl -X POST "http://k8s-userserv-userserv-xxx.elb.amazonaws.com/api/v1/cats/generate/USER_ID" \
  -F "image=@test.jpg"
```

## ⚠️ 주의사항

1. **API 키 보안**
   - API 키는 절대 코드에 하드코딩하지 말 것
   - Secret으로만 관리
   - Git에 커밋하지 않도록 주의

2. **비용 관리**
   - Nanobanana API 호출 횟수 모니터링
   - 필요시 호출 제한 설정
   - 캐싱 전략 고려

3. **타임아웃**
   - 기본 60초 설정
   - 생성 시간이 긴 경우 비동기 처리 고려

4. **에러 처리**
   - API 키 미설정 시 로그 확인
   - 생성 실패 시 원본 이미지 사용
   - 재시도 로직 구현 권장

## 📊 모니터링

### 로그 확인

```bash
# Pod 로그 확인
kubectl logs -f deployment/user-service -n user-service | grep "🎨"

# 에러 로그 필터링
kubectl logs deployment/user-service -n user-service | grep "❌"
```

### 주요 로그 메시지

- `🎨 Cat image generation request` - 생성 요청 시작
- `📤 Uploading original image to S3` - S3 업로드
- `🤖 Calling Nanobanana API` - API 호출
- `✅ Cat image generated successfully` - 생성 성공
- `❌ Failed to generate cat image` - 생성 실패

## 🔧 트러블슈팅

### 문제 1: API 키 미설정

**증상:**
```
⚠️  NANOBANANA_API_KEY not configured
```

**해결:**
1. `.env` 또는 `k8s/secret.yaml` 확인
2. Secret 재적용: `kubectl apply -f k8s/secret.yaml`
3. Pod 재시작: `kubectl rollout restart deployment/user-service -n user-service`

### 문제 2: 생성 실패

**증상:**
```
❌ Nanobanana API error: 500
```

**해결:**
1. Nanobanana API 상태 확인
2. 이미지 URL 접근 가능 여부 확인
3. API 키 유효성 확인
4. 로그에서 상세 에러 메시지 확인

### 문제 3: 타임아웃

**증상:**
```
❌ Nanobanana API timeout
```

**해결:**
1. 타임아웃 시간 증가 (nanobanana_service.py)
2. 비동기 처리 방식으로 변경 고려
3. 네트워크 연결 상태 확인

## 📚 관련 문서

- 상세 가이드: `NANOBANANA_INTEGRATION_GUIDE.md`
- S3 업로드: `S3_UPLOAD_GUIDE.md`
- 프로젝트 보고서: `PROJECT_COMPREHENSIVE_REPORT_2026_02_23.md`

## ✅ 체크리스트

배포 전 확인사항:

- [ ] Nanobanana API 키 발급 완료
- [ ] `.env` 파일에 설정 추가
- [ ] `k8s/secret.yaml` 업데이트
- [ ] `k8s/deployment.yaml` 환경 변수 추가
- [ ] Secret 적용 (`kubectl apply -f k8s/secret.yaml`)
- [ ] Deployment 적용 (`kubectl apply -f k8s/deployment.yaml`)
- [ ] Pod 재시작 완료
- [ ] 로컬 테스트 성공
- [ ] EKS 테스트 성공
- [ ] 로그 모니터링 설정
- [ ] 에러 알림 설정 (선택)

## 🎉 완료!

이제 사용자 사진을 AI 고양이 이미지로 변환할 수 있습니다!
