# User Service - EKS Deployment

FastAPI 기반의 사용자 관리 서비스를 AWS EKS에 배포하기 위한 프로젝트입니다.

## 📁 프로젝트 구조

```
EKS_Test/
├── services/
│   └── user_service/          # FastAPI 애플리케이션
│       ├── app/               # 애플리케이션 코드
│       ├── Dockerfile         # Docker 이미지 빌드
│       ├── requirements.txt   # Python 의존성
│       └── start.sh          # 컨테이너 시작 스크립트
│
├── k8s/                       # Kubernetes 매니페스트
│   ├── namespace.yaml         # 네임스페이스
│   ├── configmap.yaml         # 환경변수 설정
│   ├── secret.yaml            # 민감 정보
│   ├── serviceaccount.yaml    # Pod Identity ServiceAccount
│   ├── deployment.yaml        # Pod 배포
│   └── service.yaml           # LoadBalancer Service
│
├── iam/                       # AWS IAM 정책
│   └── user-service-policy.json
│
├── scripts/                   # 배포 스크립트
│   └── setup-pod-identity.sh # Pod Identity 설정
│
├── docs/                      # 문서
│   ├── deployment/            # 배포 관련 문서
│   ├── api_contracts.md       # API 명세
│   └── architecture.md        # 아키텍처 문서
│
├── tests/                     # 테스트 스크립트
│   ├── check_db_schema.py
│   ├── test_friend_features.py
│   └── verify-pod-identity-changes.sh
│
├── deploy-to-eks.sh          # EKS 배포 스크립트 (Linux/Mac)
├── deploy-to-eks.ps1         # EKS 배포 스크립트 (Windows)
├── pre-deployment-check.sh   # 배포 전 체크
└── test-deployment.sh        # 배포 후 테스트
```

## 🚀 빠른 시작

### 1. 사전 준비

```bash
# AWS CLI 설정
aws configure

# kubectl 설치 및 EKS 연결
aws eks update-kubeconfig --region ap-northeast-2 --name your-cluster-name

# Docker 실행 확인
docker ps
```

### 2. 배포 전 체크

```bash
./pre-deployment-check.sh
```

### 3. 배포 실행

#### Linux/Mac
```bash
./deploy-to-eks.sh
```

#### Windows (PowerShell)
```powershell
.\deploy-to-eks.ps1 -AccountId "123456789012" -ClusterName "your-cluster-name"
```

### 4. 배포 테스트

```bash
./test-deployment.sh
```

## 🔧 주요 기능

### 사용자 관리
- Cognito 기반 인증
- 사용자 CRUD
- 친구 시스템 (Friend Code)

### 데이터베이스
- **RDS PostgreSQL**: 사용자 데이터
- **DynamoDB**: 친구 관계 (선택사항)
  - Local: Pod 내부 DynamoDB Local
  - AWS: 실제 AWS DynamoDB (Pod Identity)

### AWS 통합
- **RDS**: 사용자 데이터 저장
- **DynamoDB**: 친구 관계 관리
- **Cognito**: JWT 토큰 인증
- **S3**: 파일 저장 (설정됨)
- **Pod Identity**: EKS Pod Identity (최신 방식)

## 📋 환경 설정

### ConfigMap (k8s/configmap.yaml)
```yaml
USE_RDS: "true"                    # RDS 사용
USE_LOCAL_DYNAMODB: "true"         # DynamoDB Local 사용
RDS_HOST: "your-rds-endpoint"
COGNITO_USER_POOL_ID: "..."
```

### Secret (k8s/secret.yaml)
```yaml
SECRET_KEY: <base64>               # JWT 시크릿
RDS_PASSWORD: <base64>             # RDS 비밀번호
```

## 🔐 Pod Identity 설정 (선택사항)

AWS DynamoDB를 사용하려면 Pod Identity 설정이 필요합니다.

### 1. Pod Identity 설정 스크립트 수정
```bash
vim scripts/setup-pod-identity.sh
# ACCOUNT_ID="your-account-id"
# CLUSTER_NAME="your-cluster-name"
```

### 2. Pod Identity 설정 실행
```bash
./scripts/setup-pod-identity.sh
```

### 3. ConfigMap 수정
```yaml
USE_LOCAL_DYNAMODB: "false"  # AWS DynamoDB 사용
```

자세한 내용은 [Pod Identity 설정 가이드](docs/deployment/POD_IDENTITY_CHANGES_SUMMARY.md)를 참고하세요.

## 🧪 테스트

### 로컬 테스트
```bash
cd tests
python test_friend_features.py
python check_db_schema.py
```

### 배포 후 테스트
```bash
# Health Check
kubectl port-forward svc/user-service 8080:80 -n user-service
curl http://localhost:8080/health/

# API 테스트
curl http://localhost:8080/api/v1/users/
```

## 📚 문서

- [배포 가이드](docs/deployment/eks_deployment_guide.md)
- [Pod Identity 설정](docs/deployment/POD_IDENTITY_CHANGES_SUMMARY.md)
- [RDS 연동](docs/deployment/AWS_RDS_IMPLEMENTATION.md)
- [구현 요약](docs/deployment/IMPLEMENTATION_SUMMARY.md)
- [API 명세](docs/api_contracts.md)
- [아키텍처](docs/architecture.md)

## 🔍 모니터링

### Pod 상태 확인
```bash
kubectl get pods -n user-service
kubectl logs -f deployment/user-service -n user-service
```

### Service 확인
```bash
kubectl get svc -n user-service
kubectl describe svc user-service -n user-service
```

### 리소스 사용량
```bash
kubectl top pods -n user-service
kubectl top nodes
```

## 🛠️ 트러블슈팅

### Pod가 시작되지 않는 경우
```bash
kubectl describe pod <pod-name> -n user-service
kubectl logs <pod-name> -n user-service
```

### RDS 연결 실패
```bash
# Pod 내부에서 연결 테스트
kubectl exec -it <pod-name> -n user-service -- /bin/bash
curl -v telnet://rds-host:5432
```

### DynamoDB 연결 실패
```bash
# Pod Identity 설정 확인
kubectl get sa user-service-sa -n user-service -o yaml
aws eks list-pod-identity-associations --cluster-name your-cluster-name --region ap-northeast-2
aws iam get-role --role-name UserServiceRole
```

## 🔄 업데이트 및 롤백

### 이미지 업데이트
```bash
# 새 이미지 빌드 및 푸시
docker build -t user-service:v2 services/user_service/
docker push <ecr-uri>:v2

# Deployment 업데이트
kubectl set image deployment/user-service user-service=<ecr-uri>:v2 -n user-service
```

### 롤백
```bash
kubectl rollout undo deployment/user-service -n user-service
```

## 📞 지원

문제가 발생하면 다음을 확인하세요:
1. [트러블슈팅 가이드](docs/deployment/eks_deployment_guide.md#트러블슈팅)
2. Pod 로그: `kubectl logs -f deployment/user-service -n user-service`
3. 이벤트: `kubectl get events -n user-service --sort-by='.lastTimestamp'`

## 📝 라이선스

이 프로젝트는 내부 사용을 위한 것입니다.