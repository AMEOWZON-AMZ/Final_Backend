# 더미 데이터 실행 가이드

## 🎯 목표
- PostgreSQL에 10명의 더미 사용자 추가
- DynamoDB에 54개의 친구 관계 추가 (daily_status 포함)

## 📍 DynamoDB 작성 위치

### 옵션 1: 로컬 DynamoDB (테스트용) ✅ 권장
```bash
# 1. DynamoDB Local 실행 확인
docker ps | grep dynamodb

# 없으면 실행
docker run -d -p 8008:8000 amazon/dynamodb-local

# 2. 스크립트 실행
cd services/user_service
python setup_dummy_friends_with_status.py
```

### 옵션 2: AWS DynamoDB (운영)
```bash
cd services/user_service

# .env 파일 수정
# USE_LOCAL_DYNAMODB=false

# 스크립트 실행
python setup_dummy_friends_with_status.py
```

### 옵션 3: EKS Pod에서 실행
```bash
# Pod에 접속
kubectl exec -it deployment/user-service -n user-service -- bash

# 스크립트 복사
kubectl cp setup_dummy_friends_with_status.py user-service/pod-name:/tmp/

# Pod 내에서 실행
cd /tmp
python setup_dummy_friends_with_status.py
```

## 🚀 전체 실행 순서

### 1단계: PostgreSQL에 사용자 추가

#### 방법 A: psql 직접 실행 (RDS 접근 가능한 경우)
```bash
cd services/user_service

psql -h user-service-cluster.cluster-cn4w6k04aq5d.ap-northeast-2.rds.amazonaws.com \
     -U user_admin \
     -d postgres \
     -f insert_dummy_users.sql
```

#### 방법 B: EKS Pod에서 실행
```bash
# SQL 파일 복사
kubectl cp insert_dummy_users.sql user-service/pod-name:/tmp/

# Pod 접속
kubectl exec -it deployment/user-service -n user-service -- bash

# psql 실행
psql $DATABASE_URL -f /tmp/insert_dummy_users.sql
```

### 2단계: DynamoDB에 친구 관계 추가

```bash
cd services/user_service

# 로컬 DynamoDB 사용 (기본값)
python setup_dummy_friends_with_status.py
```

## 📊 실행 결과 예시

```
================================================================================
더미 친구 관계 설정 (daily_status 포함)
================================================================================

🗑️  기존 친구 관계 삭제 중...
✅ 총 54개의 기존 관계 삭제 완료

📝 총 54개의 친구 관계를 추가합니다.

✅ b4589ddc... -> dummy-user-001... (냥냥이) 😊 STABLE
✅ b4589ddc... -> dummy-user-002... (야옹선생) 😴 SLEEP
✅ b4589ddc... -> dummy-user-003... (츄르왕) 🆘 CRITICAL
...

================================================================================
결과 요약
================================================================================
🗑️  삭제: 54개
✅ 성공: 54개
❌ 실패: 0개
📊 총: 54개

📊 Daily Status 분포:
   STABLE       (안정        ): 8개
   SLEEP        (수면 불안정  ): 7개
   LETHARGY     (무활동/무기력): 9개
   CHAOTIC      (패턴 혼란    ): 8개
   CRITICAL     (기절        ): 6개
   TRAVEL       (여행        ): 9개
   NO_DATA      (데이터X     ): 7개

🤝 친구 관계 네트워크:
   - 샤미드: 5명의 친구
   - 마릴: 4명의 친구
   - 안냥: 4명의 친구
   - 랄라: 4명의 친구
   - 왕자님: 3명의 친구
   - 더미 사용자들: 각 3-4명의 친구

💡 Tip: 각 친구마다 랜덤한 daily_status가 할당되었습니다!
```

## ✅ 검증

### PostgreSQL 확인
```sql
SELECT user_id, nickname, friend_code, phone_number 
FROM users 
WHERE user_id LIKE 'dummy-user-%'
ORDER BY user_id;
```

### DynamoDB 확인 (로컬)
```bash
aws dynamodb scan \
    --table-name user_friends \
    --endpoint-url http://localhost:8008 \
    --region ap-northeast-2 \
    | grep -A 5 "daily_status"
```

### DynamoDB 확인 (AWS)
```bash
aws dynamodb scan \
    --table-name user_friends \
    --region ap-northeast-2 \
    --max-items 10
```

### API로 확인
```bash
# 샤미드의 친구 목록 조회 (daily_status 포함)
curl "http://your-api-url/api/v1/friends?user_id=b4589ddc-a001-7001-77aa-c2c3f3fd6a98"
```

## 🎨 Daily Status 설명

| Status | 한글 | 설명 | 이모지 |
|--------|------|------|--------|
| STABLE | 안정 | 정상적인 활동 패턴 | 😊 |
| SLEEP | 수면 불안정 | 수면 패턴 이상 | 😴 |
| LETHARGY | 무활동/무기력 | 활동량 급감 | 😑 |
| CHAOTIC | 패턴 혼란 | 불규칙한 패턴 | 😵 |
| CRITICAL | 기절 | 긴급 상황 | 🆘 |
| TRAVEL | 여행 | 여행 중 | ✈️ |
| NO_DATA | 데이터X | 데이터 없음 | ❓ |

## 🔄 재실행

스크립트는 **기존 데이터를 모두 삭제**하고 새로 추가합니다.
- 여러 번 실행해도 안전
- 매번 랜덤한 daily_status 할당

```bash
# 다시 실행하면 새로운 랜덤 status로 재생성
python setup_dummy_friends_with_status.py
```

## 🧹 데이터 삭제만 하기

```python
# Python으로 삭제
python -c "
import boto3
dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8008', region_name='ap-northeast-2')
table = dynamodb.Table('user_friends')
response = table.scan()
for item in response['Items']:
    table.delete_item(Key={'user_id': item['user_id'], 'friend_user_id': item['friend_user_id']})
    print(f\"Deleted: {item['user_id']} -> {item['friend_user_id']}\")
"
```

## 📝 파일 목록

- `insert_dummy_users.sql` - PostgreSQL 사용자 INSERT
- `setup_dummy_friends_with_status.py` - DynamoDB 친구 관계 + daily_status
- `RUN_DUMMY_DATA.md` - 이 가이드

## ⚠️ 주의사항

1. **로컬 vs AWS**: `.env`의 `USE_LOCAL_DYNAMODB` 설정 확인
2. **RDS 접근**: 로컬에서 RDS 접근 시 보안 그룹 설정 필요
3. **기존 데이터**: 스크립트 실행 시 기존 친구 관계 모두 삭제됨
4. **랜덤 할당**: 매번 실행 시 다른 daily_status 할당
