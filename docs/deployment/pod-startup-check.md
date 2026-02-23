# Pod 시작 시 필요한 사항 체크

## 🔍 현재 문제점

### 1. main.py에서 잘못된 DynamoDB 서비스 사용
```python
# app/main.py
from app.services.dynamodb_service import dynamodb_service  # ← DynamoDB Local용!
```

**문제:**
- `dynamodb_service`는 DynamoDB Local (포트 8008) 전용
- Pod Identity로 AWS DynamoDB를 사용하려면 `aws_dynamodb_service` 사용 필요

### 2. 환경변수에 따른 서비스 선택 필요
```python
# 현재: 하드코딩
from app.services.dynamodb_service import dynamodb_service

# 필요: 환경변수에 따라 선택
if USE_LOCAL_DYNAMODB:
    from app.services.dynamodb_service import dynamodb_service
else:
    from aws_dynamodb_service import aws_dynamodb_service as dynamodb_service
```

## 🔧 필요한 추가 수정

### 1. app/services/__init__.py 생성
환경변수에 따라 적절한 DynamoDB 서비스 선택

### 2. main.py 수정
동적으로 DynamoDB 서비스 임포트

### 3. DynamoDB 테이블 생성
AWS DynamoDB에 `user_friends` 테이블 필요

## 🚨 현재 상태로 Pod 올리면?

### 시나리오 1: USE_LOCAL_DYNAMODB="true"
✅ **작동함**
- DynamoDB Local이 Pod 내부에서 실행됨
- 자격증명 불필요
- 데이터는 Pod 재시작 시 손실

### 시나리오 2: USE_LOCAL_DYNAMODB="false" (Pod Identity)
❌ **작동 안함**
- `main.py`가 여전히 `dynamodb_service` (Local용) 임포트
- AWS DynamoDB 연결 실패
- Pod 시작 실패 가능

## 💡 해결 방안

### 옵션 1: 간단한 수정 (권장)
ConfigMap에서 `USE_LOCAL_DYNAMODB="true"`로 설정
→ DynamoDB Local 사용, Pod Identity 불필요

### 옵션 2: 완전한 Pod Identity 적용
1. `app/services/__init__.py` 생성
2. `main.py` 수정
3. DynamoDB 테이블 생성
4. Pod Identity 설정

## 🎯 결론

**현재 상태로는 Pod Identity 설정 후 Pod를 올려도 제대로 작동하지 않습니다.**

**이유:**
1. `main.py`가 DynamoDB Local용 서비스를 하드코딩으로 임포트
2. 환경변수에 따른 동적 선택 로직 없음
3. AWS DynamoDB 테이블 미생성

**권장:**
- 일단 `USE_LOCAL_DYNAMODB="true"`로 설정하고 Pod 테스트
- 나중에 AWS DynamoDB로 마이그레이션