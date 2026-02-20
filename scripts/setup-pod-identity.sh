#!/bin/bash

# EKS Pod Identity 설정 스크립트
set -e

# 설정 변수들
ACCOUNT_ID="715428147916"  # AWS 계정 ID로 변경
REGION="ap-northeast-2"
CLUSTER_NAME="casual-electro-crow"  # EKS 클러스터 이름
NAMESPACE="user-service"
SERVICE_ACCOUNT="user-service-sa"
ROLE_NAME="UserServiceRole"
POLICY_NAME="UserServicePolicy"

echo "🔒 EKS Pod Identity 설정 시작..."
echo "📍 Account ID: $ACCOUNT_ID"
echo "📍 Region: $REGION"
echo "📍 Cluster: $CLUSTER_NAME"
echo "📍 Namespace: $NAMESPACE"
echo "📍 ServiceAccount: $SERVICE_ACCOUNT"
echo "📍 Role: $ROLE_NAME"

# 1. IAM Policy 생성
echo ""
echo "1️⃣ IAM Policy 생성..."
POLICY_ARN="arn:aws:iam::$ACCOUNT_ID:policy/$POLICY_NAME"

# 기존 정책 확인
if aws iam get-policy --policy-arn $POLICY_ARN &>/dev/null; then
    echo "📋 기존 정책 존재: $POLICY_NAME"
    
    # 정책 업데이트
    echo "🔄 정책 업데이트 중..."
    aws iam create-policy-version \
        --policy-arn $POLICY_ARN \
        --policy-document file://iam/user-service-policy.json \
        --set-as-default
    echo "✅ 정책 업데이트 완료"
else
    echo "📦 새 정책 생성 중..."
    aws iam create-policy \
        --policy-name $POLICY_NAME \
        --policy-document file://iam/user-service-policy.json \
        --description "Policy for User Service Pod to access AWS resources"
    echo "✅ 정책 생성 완료: $POLICY_ARN"
fi

# 2. IAM Role 생성 (Pod Identity용 Trust Policy)
echo ""
echo "2️⃣ IAM Role 생성..."

# Trust Policy 생성 (Pod Identity용)
cat > /tmp/pod-identity-trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "pods.eks.amazonaws.com"
      },
      "Action": [
        "sts:AssumeRole",
        "sts:TagSession"
      ]
    }
  ]
}
EOF

# Role 생성 또는 업데이트
if aws iam get-role --role-name $ROLE_NAME &>/dev/null; then
    echo "📋 기존 Role 존재: $ROLE_NAME"
    
    # Trust Policy 업데이트
    echo "🔄 Trust Policy 업데이트 중..."
    aws iam update-assume-role-policy \
        --role-name $ROLE_NAME \
        --policy-document file:///tmp/pod-identity-trust-policy.json
    echo "✅ Trust Policy 업데이트 완료"
else
    echo "📦 새 Role 생성 중..."
    aws iam create-role \
        --role-name $ROLE_NAME \
        --assume-role-policy-document file:///tmp/pod-identity-trust-policy.json \
        --description "Role for User Service Pod Identity"
    echo "✅ Role 생성 완료"
fi

# 3. Policy를 Role에 연결
echo ""
echo "3️⃣ Policy를 Role에 연결..."
aws iam attach-role-policy \
    --role-name $ROLE_NAME \
    --policy-arn $POLICY_ARN
echo "✅ Policy 연결 완료"

# 4. Pod Identity Association 생성
echo ""
echo "4️⃣ Pod Identity Association 생성..."

# 기존 Association 확인
EXISTING_ASSOCIATION=$(aws eks list-pod-identity-associations \
    --cluster-name $CLUSTER_NAME \
    --namespace $NAMESPACE \
    --service-account $SERVICE_ACCOUNT \
    --region $REGION \
    --query 'associations[0].associationArn' \
    --output text 2>/dev/null || echo "None")

if [ "$EXISTING_ASSOCIATION" != "None" ] && [ "$EXISTING_ASSOCIATION" != "" ]; then
    echo "📋 기존 Pod Identity Association 존재"
    echo "   Association ARN: $EXISTING_ASSOCIATION"
    
    # 기존 Association 삭제
    echo "🗑️  기존 Association 삭제 중..."
    aws eks delete-pod-identity-association \
        --cluster-name $CLUSTER_NAME \
        --association-id $(basename $EXISTING_ASSOCIATION) \
        --region $REGION
    
    echo "⏳ 삭제 대기 중..."
    sleep 10
fi

# 새 Association 생성
echo "📦 새 Pod Identity Association 생성 중..."
ASSOCIATION_ARN=$(aws eks create-pod-identity-association \
    --cluster-name $CLUSTER_NAME \
    --namespace $NAMESPACE \
    --service-account $SERVICE_ACCOUNT \
    --role-arn "arn:aws:iam::$ACCOUNT_ID:role/$ROLE_NAME" \
    --region $REGION \
    --query 'association.associationArn' \
    --output text)

echo "✅ Pod Identity Association 생성 완료"
echo "   Association ARN: $ASSOCIATION_ARN"

# 5. 설정 검증
echo ""
echo "5️⃣ 설정 검증..."

# ServiceAccount 확인
echo "📋 ServiceAccount 확인:"
kubectl get serviceaccount $SERVICE_ACCOUNT -n $NAMESPACE 2>/dev/null || echo "   ⚠️  ServiceAccount 없음 (배포 시 생성됨)"

# IAM Role 확인
echo "📋 IAM Role 확인:"
aws iam get-role --role-name $ROLE_NAME --query 'Role.Arn' --output text

# Policy 확인
echo "📋 IAM Policy 확인:"
aws iam get-policy --policy-arn $POLICY_ARN --query 'Policy.Arn' --output text

# Pod Identity Association 확인
echo "📋 Pod Identity Association 확인:"
aws eks describe-pod-identity-association \
    --cluster-name $CLUSTER_NAME \
    --association-id $(basename $ASSOCIATION_ARN) \
    --region $REGION \
    --query 'association.[associationArn,namespace,serviceAccount,roleArn]' \
    --output table

# Cleanup
rm -f /tmp/pod-identity-trust-policy.json

echo ""
echo "🎉 Pod Identity 설정 완료!"
echo ""
echo "📋 다음 단계:"
echo "   1. Kubernetes 리소스 배포"
echo "   2. Pod가 AWS 서비스에 접근할 수 있는지 확인"
echo ""
echo "🔍 검증 명령어:"
echo "   # Pod Identity Association 목록"
echo "   aws eks list-pod-identity-associations --cluster-name $CLUSTER_NAME --region $REGION"
echo ""
echo "   # Pod 내부에서 AWS 자격증명 확인"
echo "   kubectl exec -it <pod-name> -n $NAMESPACE -- aws sts get-caller-identity"