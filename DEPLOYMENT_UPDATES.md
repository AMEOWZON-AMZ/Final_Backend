# 배포 환경 설정 업데이트 완료

## 📋 변경 사항

### 1. ✅ requirements.txt 업데이트
**추가된 패키지:**
```txt
audioop-lts==0.2.2  # Python 3.13 호환성 (audioop 모듈 대체)
```

**위치:** `services/user_service/requirements.txt`

**이유:** Python 3.13에서 제거된 audioop 모듈을 대체하여 pydub가 정상 작동하도록 함

---

### 2. ✅ Dockerfile 업데이트
**추가된 시스템 패키지:**
```dockerfile
ffmpeg  # 오디오 파일 변환 및 처리
```

**변경 내용:**
```dockerfile
# Before:
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# After:
RUN apt-get update && apt-get install -y \
    curl \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*
```

**위치:** `services/user_service/Dockerfile`

**이유:** pydub가 오디오 파일 변환 시 FFmpeg를 사용하므로 필수

---

### 3. ✅ Kubernetes 리소스 (변경 없음)
**현재 설정:**
```yaml
resources:
  requests:
    memory: "1Gi"
    cpu: "250m"
  limits:
    memory: "2Gi"
    cpu: "1000m"
```

**판단:** 오디오 처리를 고려해도 현재 메모리 설정(1-2Gi)으로 충분함

---

## 🚀 배포 방법

### 1. Docker 이미지 빌드 및 푸시
```bash
cd services/user_service

# 이미지 빌드
docker build -t 715428147916.dkr.ecr.ap-northeast-2.amazonaws.com/user-service:latest .

# ECR 로그인
aws ecr get-login-password --region ap-northeast-2 | \
  docker login --username AWS --password-stdin \
  715428147916.dkr.ecr.ap-northeast-2.amazonaws.com

# 이미지 푸시
docker push 715428147916.dkr.ecr.ap-northeast-2.amazonaws.com/user-service:latest
```

### 2. Kubernetes 리소스 적용
```bash
# ConfigMap 적용
kubectl apply -f k8s/configmap.yaml

# Secret 적용 (Gemini API 키 포함)
kubectl apply -f k8s/secret.yaml

# Deployment 적용
kubectl apply -f k8s/deployment.yaml
```

### 3. 배포 확인
```bash
# Pod 상태 확인
kubectl get pods -n user-service

# 로그 확인
kubectl logs -f <pod-name> -n user-service

# 서비스 확인
kubectl get svc -n user-service
```

---

## 🔍 배포 후 확인 사항

### 1. FFmpeg 설치 확인
```bash
kubectl exec -it <pod-name> -n user-service -- ffmpeg -version
```

### 2. Python 패키지 확인
```bash
kubectl exec -it <pod-name> -n user-service -- pip list | grep -E "pydub|audioop|amazon-transcribe"
```

### 3. API 테스트
```bash
# Health check
curl https://your-domain/health

# 오디오 업로드 테스트
curl -X POST https://your-domain/api/v1/upload/meow-audio/test_user \
  -F "file=@test_audio.wav"
```

---

## 📊 새로운 기능

### 1. 고양이 캐릭터 AI 이미지 생성
**엔드포인트:** `POST /api/v1/cat-character/generate/{user_id}`

**기능:**
- Gemini 2.5 Flash Image로 사람 얼굴을 고양이 캐릭터로 변환
- 3D 스타일 렌더링
- 실제 고양이 패턴 (치즈냥이, 삼색냥이, 턱시도냥이, 고등어냥이)
- 표정 보존
- 다양한 털 색상

### 2. 오디오 검증 (Audio Guard)
**엔드포인트:** `POST /api/v1/upload/meow-audio/{user_id}`

**기능:**
- 오디오 품질 검증 (무음, 클리핑, 길이)
- 발화 시작점 자동 검출
- AWS Transcribe로 STT
- 텍스트 판정 (냐옹 어휘 / 문장 / LLM)
- 품질 개선 (볼륨 정규화, 무음 제거)
- 처리된 오디오 자동 저장

---

## ⚠️ 주의사항

### 1. API 키 관리
- `GEMINI_API_KEY`: 고양이 캐릭터 생성용
- `AUDIO_GUARD_GEMINI_API_KEY`: 오디오 텍스트 판정용
- 두 키 모두 k8s/secret.yaml에 설정됨

### 2. AWS 권한
- **Transcribe**: 오디오 STT 변환
- **S3**: 파일 업로드/다운로드
- **RDS**: 데이터베이스
- Pod Identity로 자동 관리됨

### 3. 비용
- **Gemini API**: 유료 (이미지 생성 + LLM 판정)
- **AWS Transcribe**: 사용량 기반 과금
- **S3**: 저장 및 전송 비용

---

## 🎯 배포 체크리스트

- [x] requirements.txt에 audioop-lts 추가
- [x] Dockerfile에 ffmpeg 추가
- [x] k8s/secret.yaml에 AUDIO_GUARD_GEMINI_API_KEY 추가
- [x] audio_guard.py 버그 수정 (reason 변수)
- [x] cat_character.py에 gemini_image_service 통합
- [x] upload.py에 audio_guard 통합
- [ ] Docker 이미지 빌드 및 푸시
- [ ] Kubernetes 리소스 적용
- [ ] 배포 후 테스트

---

## 📚 관련 문서

- `GEMINI_CAT_CHARACTER_GUIDE.md` - 고양이 캐릭터 생성 가이드
- `AUDIO_GUARD_TEST_GUIDE.md` - 오디오 검증 테스트 가이드
- `docs/API_DOCUMENTATION.md` - API 문서

---

## 🐛 알려진 이슈

### 로컬 개발 환경
- Python 3.13 사용 시 audioop-lts 필수
- FFmpeg 설치 필요 (Windows: choco install ffmpeg)

### 해결 방법
```bash
pip install audioop-lts
choco install ffmpeg  # Windows
brew install ffmpeg   # Mac
```

---

**업데이트 날짜:** 2026-02-24
**버전:** 1.0.0
