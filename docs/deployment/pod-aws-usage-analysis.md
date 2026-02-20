# Pod에서 AWS 서비스 사용 분석

## 🔍 현재 설정 분석

### ConfigMap 설정 (k8s/configmap.yaml)
```yaml
USE_LOCAL_DYNAMODB: "false"  # ← 실제 AWS DynamoDB 사용
DYNAMODB_REGION: "ap-northeast-2"
AWS_REGION: "ap-northeast-2"
S3_BUCKET_NAME: "your-s3-bucket-name"
```

### 코드에서 AWS 서비스 사용
1. **aws_dynamodb_service.py**: 실제 AWS DynamoDB 연결
2. **S3 설정**: ConfigMap에 S3 버킷 설정 있음
3. **Cognito**: JWT 토큰 검증용 (읽기 전용)

## 🎯 Pod에서 필요한 AWS 권한

### 1️⃣ DynamoDB 권한 (필수)
```json
{
  "Effect": "Allow",
  "Action": [
    "dynamodb:GetItem",
    "dynamodb:PutItem", 
    "dynamodb:UpdateItem",
    "dynamodb:DeleteItem",
    "dynamodb:Query",
    "dynamodb:CreateTable",
    "dynamodb:DescribeTable"
  ],
  "Resource": "arn:aws:dynamodb:ap-northeast-2:*:table/user_friends"
}
```

### 2️⃣ S3 권한 (설정되어 있음)
```json
{
  "Effect": "Allow",
  "Action": [
    "s3:GetObject",
    "s3:PutObject",
    "s3:DeleteObject"
  ],
  "Resource": "arn:aws:s3:::your-s3-bucket-name/*"
}
```

### 3️⃣ Cognito 권한 (불필요)
- JWT 토큰 검증은 공개 키로 처리
- AWS API 호출 없음

## 🚨 현재 문제점

### ConfigMap vs 실제 사용
```yaml
# ConfigMap에서는 AWS DynamoDB 사용 설정
USE_LOCAL_DYNAMODB: "false"

# 하지만 start.sh에서는 DynamoDB Local 실행
java -jar DynamoDBLocal.jar -port 8008 &
```

**모순된 설정!**

## 🔧 해결 방안

### 옵션 1: DynamoDB Local 사용 (AWS 자격증명 불필요)
```yaml
# ConfigMap 수정
USE_LOCAL_DYNAMODB: "true"
DYNAMODB_ENDPOINT_URL: "http://localhost:8008"

# start.sh 유지 (DynamoDB Local 실행)
```

**장점:**
- AWS 자격증명 불필요
- Pod Identity 설정 불필요
- 빠른 배포 가능

**단점:**
- Pod 재시작 시 데이터 손실
- 확장성 제한
- 프로덕션 부적합

### 옵션 2: 실제 AWS DynamoDB 사용 (AWS 자격증명 필요)
```yaml
# ConfigMap 유지
USE_LOCAL_DYNAMODB: "false"
DYNAMODB_REGION: "ap-northeast-2"

# start.sh 수정 (DynamoDB Local 제거)
```

**필요한 작업:**
- AWS 자격증명 설정 (Secret 또는 Pod Identity)
- DynamoDB 테이블 생성
- start.sh에서 DynamoDB Local 제거

## 💡 권장사항

### 현재 상황에 맞는 선택

#### 🔶 빠른 테스트/데모용 → DynamoDB Local
```bash
# 변경 사항 최소화
# ConfigMap만 수정
USE_LOCAL_DYNAMODB: "true"
```

#### 🔷 실제 프로덕션용 → AWS DynamoDB + Pod Identity
```bash
# 완전한 AWS 통합
# Pod Identity 설정 + DynamoDB 테이블 생성
USE_LOCAL_DYNAMODB: "false"
```

## 📋 각 옵션별 변경 사항

### 옵션 1: DynamoDB Local (간단)
**변경할 파일:**
- `k8s/configmap.yaml`: USE_LOCAL_DYNAMODB="true"
- `k8s/secret.yaml`: AWS 자격증명 제거 가능

**변경하지 않을 파일:**
- `start.sh`: 그대로 유지
- `Dockerfile`: 그대로 유지
- 애플리케이션 코드: 그대로 유지

### 옵션 2: AWS DynamoDB (복잡)
**변경할 파일:**
- `start.sh`: DynamoDB Local 실행 제거
- `k8s/secret.yaml`: AWS 자격증명 추가 또는 IRSA 설정
- AWS: DynamoDB 테이블 생성

**추가 작업:**
- DynamoDB 테이블 생성
- IAM 권한 설정
- IRSA 설정 (선택사항)

## 🎯 결론

**현재 코드 구조를 보면:**
1. **DynamoDB Local이 기본 설정**으로 되어 있음
2. **AWS DynamoDB는 옵션**으로 구현됨
3. **S3는 설정만 있고 실제 사용 안함**

**따라서 Pod 배포 시 Pod Identity가 반드시 필요하지는 않습니다.**

**권장 순서:**
1. **1단계**: DynamoDB Local로 Pod 배포 테스트
2. **2단계**: 필요시 AWS DynamoDB로 마이그레이션
3. **3단계**: Pod Identity 적용 (보안 강화)