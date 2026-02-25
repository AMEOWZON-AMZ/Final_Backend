# 도커 빌드 및 배포 스크립트 (PowerShell)
param(
    [string]$ImageTag = "latest"
)

$ErrorActionPreference = "Stop"

# 변수 설정
$AWS_ACCOUNT_ID = "715428147916"
$AWS_REGION = "ap-northeast-2"
$ECR_REPOSITORY = "user-service"
$SERVICE_DIR = "services/user_service"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "도커 이미지 빌드 및 배포 시작" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 1. ECR 로그인
Write-Host "1. ECR 로그인 중..." -ForegroundColor Yellow
$password = aws ecr get-login-password --region $AWS_REGION
$password | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"

# 2. 도커 이미지 빌드
Write-Host "2. 도커 이미지 빌드 중..." -ForegroundColor Yellow
Push-Location $SERVICE_DIR
docker build -t "${ECR_REPOSITORY}:${ImageTag}" .
Pop-Location

# 3. 이미지 태그 지정
Write-Host "3. 이미지 태그 지정 중..." -ForegroundColor Yellow
docker tag "${ECR_REPOSITORY}:${ImageTag}" "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/${ECR_REPOSITORY}:${ImageTag}"

# 4. ECR에 푸시
Write-Host "4. ECR에 이미지 푸시 중..." -ForegroundColor Yellow
docker push "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/${ECR_REPOSITORY}:${ImageTag}"

# 5. Kubernetes 배포 업데이트
Write-Host "5. Kubernetes 배포 업데이트 중..." -ForegroundColor Yellow
kubectl rollout restart deployment/user-service -n user-service

# 6. 배포 상태 확인
Write-Host "6. 배포 상태 확인 중..." -ForegroundColor Yellow
kubectl rollout status deployment/user-service -n user-service

Write-Host "==========================================" -ForegroundColor Green
Write-Host "배포 완료!" -ForegroundColor Green
Write-Host "이미지: $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/${ECR_REPOSITORY}:${ImageTag}" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# Pod 상태 확인
Write-Host ""
Write-Host "현재 Pod 상태:" -ForegroundColor Cyan
kubectl get pods -n user-service -l app=user-service
