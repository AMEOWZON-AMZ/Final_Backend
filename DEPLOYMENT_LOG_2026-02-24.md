# 배포 작업 로그 - 2026년 2월 24일

## 작업 개요
user-service Docker 이미지 빌드 및 EKS 배포 업데이트

## 작업 상세

### 1. Docker 이미지 빌드
- **이미지명**: `user-service:latest`
- **빌드 경로**: `services/user_service/`
- **빌드 명령어**:
  ```bash
  docker build -t user-service:latest -f ./services/user_service/Dockerfile ./services/user_service
  ```
- **결과**: 성공 (이미지 크기: 1.66GB)

### 2. ECR 레포지토리 확인
- **AWS 계정 ID**: 715428147916
- **리전**: ap-northeast-2
- **ECR 레포지토리**: user-service
- **전체 URI**: `715428147916.dkr.ecr.ap-northeast-2.amazonaws.com/user-service`

### 3. ECR 로그인
```bash
aws ecr get-login-password --region ap-northeast-2 | docker login --username AWS --password-stdin 715428147916.dkr.ecr.ap-northeast-2.amazonaws.com
```
- **결과**: Login Succeeded

### 4. Docker 이미지 태깅
```bash
docker tag user-service:latest 715428147916.dkr.ecr.ap-northeast-2.amazonaws.com/user-service:latest
```

### 5. ECR 푸시
```bash
docker push 715428147916.dkr.ecr.ap-northeast-2.amazonaws.com/user-service:latest
```
- **결과**: 성공
- **Digest**: sha256:5c4d7ba3e1008ebe194d9f2eb89cb8aac8c0278fea6b2999149fe9d30bdefcfb
- **Size**: 856

### 6. EKS 배포 업데이트
- **네임스페이스**: user-service (ameowzon 아님!)
- **배포 재시작 명령어**:
  ```bash
  kubectl rollout restart deployment/user-service -n user-service
  ```
- **결과**: deployment.apps/user-service restarted

### 7. 배포 확인
- **새 파드**: user-service-76dd7659d7-bq49f
- **상태**: Running (1/1 Ready)
- **이전 파드**: user-service-7df46d798c-4g7fs (Terminated)
- **Health Check**: 정상 (200 OK)
- **로그 확인**: ELB-HealthChecker 및 kube-probe 모두 정상 응답

## 최종 상태
```
NAME                            READY   STATUS    RESTARTS   AGE
user-service-76dd7659d7-bq49f   1/1     Running   0          2m1s
```

## 중요 사항
1. **네임스페이스 주의**: `ameowzon`이 아니라 `user-service` 네임스페이스 사용
2. **ECR 계정 ID**: 715428147916 (533267161065 아님)
3. **이미지 태그**: latest
4. **배포 방식**: rollout restart (새 파드 생성 후 이전 파드 종료)

## 다음 배포 시 참고 명령어
```bash
# 1. 이미지 빌드
docker build -t user-service:latest -f ./services/user_service/Dockerfile ./services/user_service

# 2. ECR 로그인
aws ecr get-login-password --region ap-northeast-2 | docker login --username AWS --password-stdin 715428147916.dkr.ecr.ap-northeast-2.amazonaws.com

# 3. 이미지 태깅
docker tag user-service:latest 715428147916.dkr.ecr.ap-northeast-2.amazonaws.com/user-service:latest

# 4. ECR 푸시
docker push 715428147916.dkr.ecr.ap-northeast-2.amazonaws.com/user-service:latest

# 5. EKS 배포 재시작
kubectl rollout restart deployment/user-service -n user-service

# 6. 상태 확인
kubectl get pods -n user-service
kubectl logs <pod-name> -n user-service --tail=50
```

## 작업 완료 시간
2026-02-24 04:16 (UTC)
