"""
손상된 profile_image_url 직접 수정 (RDS + DynamoDB)
Pod에서 실행
"""
import os
import sys
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import boto3
from urllib.parse import unquote

# 환경 변수에서 DB 정보 가져오기
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "ameowzon")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

USER_ID = "c478cd4c-5071-7060-2991-cc9b3bb59dff"
CORRECT_URL = "https://ameowzon-test-files.s3.amazonaws.com/cat-characters/c478cd4c-5071-7060-2991-cc9b3bb59dff_20260226_121004_031757c7.png"

print(f"🔧 손상된 URL 수정 시작...")
print(f"📍 User ID: {USER_ID}")
print(f"✅ 올바른 URL: {CORRECT_URL}\n")

# RDS 연결
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # 1. RDS 업데이트
    print("1️⃣ RDS 업데이트 중...")
    result = db.execute(
        "UPDATE users SET profile_image_url = :url WHERE user_id = :user_id",
        {"url": CORRECT_URL, "user_id": USER_ID}
    )
    db.commit()
    print(f"   ✅ RDS 업데이트 완료 (affected rows: {result.rowcount})")
    
    # 2. DynamoDB 업데이트
    print("\n2️⃣ DynamoDB 업데이트 중...")
    dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-2')
    friends_table = dynamodb.Table('user_friends')
    
    # 이 사용자를 친구로 가진 모든 레코드 조회
    response = friends_table.scan(
        FilterExpression='friend_user_id = :friend_id',
        ExpressionAttributeValues={
            ':friend_id': USER_ID
        }
    )
    
    updated_count = 0
    for item in response['Items']:
        friends_table.update_item(
            Key={
                'user_id': item['user_id'],
                'friend_user_id': USER_ID
            },
            UpdateExpression='SET profile_image_url = :url',
            ExpressionAttributeValues={
                ':url': CORRECT_URL
            }
        )
        updated_count += 1
        print(f"   - Updated: {item['user_id']} → {USER_ID}")
    
    print(f"   ✅ DynamoDB 업데이트 완료 ({updated_count} records)")
    
    print("\n🎉 모든 수정 완료!")
    
except Exception as e:
    print(f"\n❌ 오류 발생: {e}")
    db.rollback()
finally:
    db.close()
