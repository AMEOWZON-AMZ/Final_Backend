# IRSA (IAM Roles for Service Accounts) 설정 계획

## 🎯 변경 목표
현재 Secret 기반 AWS 자격증명을 IRSA로 변경하여 보안 강화

## 📋 현재 구조 분석

### 현재 AWS 서비스 사용
1. **RDS PostgreSQL**: 데이터베이스 연결
2. **DynamoDB**: 친구 관계 관리
3. **S3**: 파일 저장 (설정만 있음)
4. **Cognito**: JWT 토큰 검증

### 현재 권한 요구사항
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem",
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:CreateTable",
        "dynamodb:DescribeTable"
      ],
      "Resource": "arn:aws:dynamodb:ap-northeast-2:*:table/user_friends"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::your-s3-bucket-name/*"
    }
  ]
}
```

## 🏗️ IRSA 설정 단계

### 1단계: IAM Role 생성
```bash
# 1. OIDC Identity Provider 확인/생성
eksctl utils associate-iam-oidc-provider \
    --cluster your-cluster-name \
    --region ap-northeast-2 \
    --approve

# 2. IAM Policy 생성
aws iam create-policy \
    --policy-name UserServicePolicy \
    --policy-document file://user-service-policy.json

# 3. IAM Role 생성 및 ServiceAccount 연결
eksctl create iamserviceaccount \
    --cluster your-cluster-name \
    --namespace user-service \
    --name user-service-sa \
    --role-name UserServiceRole \
    --attach-policy-arn arn:aws:iam::ACCOUNT_ID:policy/UserServicePolicy \
    --region ap-northeast-2 \
    --approve
```

### 2단계: Kubernetes 매니페스트 수정

#### 새로 추가할 파일: `k8s/serviceaccount.yaml`
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: user-service-sa
  namespace: user-service
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::ACCOUNT_ID:role/UserServiceRole
automountServiceAccountToken: true
```

#### 수정할 파일: `k8s/deployment.yaml`
```yaml
# 기존
spec:
  template:
    spec:
      containers:
      - name: user-service
        envFrom:
        - secretRef:
            name: user-service-secret  # 제거

# 변경 후
spec:
  template:
    spec:
      serviceAccountName: user-service-sa  # 추가
      containers:
      - name: user-service
        env:
        - name: AWS_REGION
          value: "ap-northeast-2"
        # AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY 제거
```

#### 수정할 파일: `k8s/secret.yaml`
```yaml
# 기존 (제거할 항목들)
data:
  AWS_ACCESS_KEY_ID: xxx  # 제거
  AWS_SECRET_ACCESS_KEY: xxx  # 제거

# 유지할 항목들
data:
  SECRET_KEY: xxx  # JWT 시크릿 (유지)
  RDS_PASSWORD: xxx  # RDS 비밀번호 (유지)
```

### 3단계: 애플리케이션 코드 수정

#### 현재 코드 (변경 필요)
```python
# app/services/dynamodb_service.py
self.dynamodb = boto3.resource(
    'dynamodb',
    region_name=os.getenv("AWS_REGION", "ap-northeast-2"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),  # 제거
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")  # 제거
)
```

#### IRSA 적용 후 코드
```python
# app/services/dynamodb_service.py
self.dynamodb = boto3.resource(
    'dynamodb',
    region_name=os.getenv("AWS_REGION", "ap-northeast-2")
    # 자격증명 파라미터 제거 - IRSA가 자동 처리
)
```

## 📁 변경할 파일 목록

### 새로 생성할 파일
1. `k8s/serviceaccount.yaml` - ServiceAccount 정의
2. `iam/user-service-policy.json` - IAM Policy 정의
3. `scripts/setup-irsa.sh` - IRSA 설정 스크립트

### 수정할 파일
1. `k8s/deployment.yaml` - ServiceAccount 연결, Secret 제거
2. `k8s/secret.yaml` - AWS 자격증명 제거
3. `k8s/configmap.yaml` - AWS 관련 환경변수 정리
4. `services/user_service/app/services/dynamodb_service.py` - 자격증명 제거
5. `services/user_service/aws_dynamodb_service.py` - 자격증명 제거
6. `deploy-to-eks.sh` - IRSA 설정 단계 추가

### 제거할 수 있는 설정
- `AWS_ACCESS_KEY_ID` 환경변수
- `AWS_SECRET_ACCESS_KEY` 환경변수
- Secret의 AWS 자격증명 부분

## 🔄 마이그레이션 순서

### Phase 1: IRSA 설정
1. OIDC Provider 연결
2. IAM Policy 생성
3. IAM Role 및 ServiceAccount 생성

### Phase 2: Kubernetes 리소스 수정
1. ServiceAccount 매니페스트 생성
2. Deployment에 ServiceAccount 연결
3. Secret에서 AWS 자격증명 제거

### Phase 3: 애플리케이션 코드 수정
1. DynamoDB 서비스 코드 수정
2. 환경변수 정리
3. 테스트 및 검증

### Phase 4: 배포 및 테스트
1. 새로운 매니페스트로 배포
2. AWS 서비스 연결 테스트
3. 기능 검증

## 🎯 예상 효과

### 보안 개선
- ✅ 하드코딩된 자격증명 제거
- ✅ 임시 토큰 자동 로테이션
- ✅ 최소 권한 원칙 적용
- ✅ Secret 노출 위험 제거

### 운영 개선
- ✅ 자격증명 관리 자동화
- ✅ 권한 세밀 제어
- ✅ 감사 로그 개선
- ✅ 컴플라이언스 향상

## ⚠️ 주의사항

### 사전 요구사항
- EKS 클러스터에 OIDC Provider 연결 필요
- eksctl 또는 AWS CLI 권한 필요
- IAM 정책 생성 권한 필요

### 테스트 계획
1. 개발 환경에서 먼저 테스트
2. DynamoDB 연결 확인
3. S3 접근 권한 확인
4. 롤백 계획 준비

## 🚀 실행 여부 결정 기준

### IRSA 적용을 권장하는 경우
- ✅ 프로덕션 환경 배포
- ✅ 보안 요구사항이 높은 경우
- ✅ 장기간 운영 예정
- ✅ 컴플라이언스 요구사항

### 현재 구조 유지를 고려하는 경우
- 🔶 개발/테스트 환경
- 🔶 빠른 프로토타입 필요
- 🔶 IRSA 설정 권한 없음
- 🔶 단기간 사용 예정

## 💡 권장사항

**프로덕션 배포라면 IRSA 적용을 강력히 권장합니다.**

이유:
1. AWS 보안 모범 사례
2. 자격증명 노출 위험 제거
3. 운영 효율성 향상
4. 감사 및 컴플라이언스 대응