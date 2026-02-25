#!/bin/bash

# 도커 빌드 및 배포 스크립트
set -e

# 변수 설정
AWS_ACCOUNT_ID="715428147916"
AWS_REGION="ap-northeast-2"
ECR_REPOSITORY="user-service"
IMAGE_TAG="${1:-latest}"
SERVICE_DIR="services/user_service"

echo "=========================================="
echo "도커 이미지 빌드 및 배포 시작"
echo "=========================================="

# 1. ECR 로그인
echo "1. ECR 로그인 중..."
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

# 2. 도커 이미지 빌드
echo "2. 도커 이미지 빌드 중..."
cd ${SERVICE_DIR}
docker build -t ${ECR_REPOSITORY}:${IMAGE_TAG} .
cd ../..

# 3. 이미지 태그 지정
echo "3. 이미지 태그 지정 중..."
docker tag ${ECR_REPOSITORY}:${IMAGE_TAG} ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY}:${IMAGE_TAG}

# 4. ECR에 푸시
echo "4. ECR에 이미지 푸시 중..."
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY}:${IMAGE_TAG}

# 5. Kubernetes 배포 업데이트
echo "5. Kubernetes 배포 업데이트 중..."
kubectl rollout restart deployment/user-service -n user-service

# 6. 배포 상태 확인
echo "6. 배포 상태 확인 중..."
kubectl rollout status deployment/user-service -n user-service

echo "=========================================="
echo "배포 완료!"
echo "이미지: ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY}:${IMAGE_TAG}"
echo "=========================================="

# Pod 상태 확인
echo ""
echo "현재 Pod 상태:"
kubectl get pods -n user-service -l app=user-service
