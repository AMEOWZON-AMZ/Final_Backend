"""
DynamoDB user_friends 테이블에서 cat_color가 null인 레코드를 #FFDEAD로 업데이트
"""
import boto3
from decimal import Decimal
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# DynamoDB 클라이언트 초기화
dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-2')
table = dynamodb.Table('user_friends')

def update_null_cat_colors():
    """cat_color가 null인 모든 레코드를 #FFDEAD로 업데이트"""
    
    default_color = "#FFDEAD"
    updated_count = 0
    scanned_count = 0
    
    print("🔍 Scanning user_friends table for null cat_color...")
    
    # 전체 테이블 스캔
    response = table.scan()
    items = response.get('Items', [])
    
    while True:
        for item in items:
            scanned_count += 1
            user_id = item.get('user_id')
            friend_user_id = item.get('friend_user_id')
            cat_color = item.get('cat_color')
            
            # cat_color가 None이거나 빈 문자열인 경우
            if not cat_color:
                print(f"📝 Updating: user_id={user_id}, friend_user_id={friend_user_id}")
                
                try:
                    # DynamoDB 업데이트
                    table.update_item(
                        Key={
                            'user_id': user_id,
                            'friend_user_id': friend_user_id
                        },
                        UpdateExpression='SET cat_color = :color',
                        ExpressionAttributeValues={
                            ':color': default_color
                        }
                    )
                    updated_count += 1
                    print(f"✅ Updated: {user_id} -> cat_color={default_color}")
                    
                except Exception as e:
                    print(f"❌ Failed to update {user_id}: {e}")
        
        # 다음 페이지가 있으면 계속
        if 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items = response.get('Items', [])
        else:
            break
    
    print(f"\n🎉 Update completed!")
    print(f"📊 Total scanned: {scanned_count}")
    print(f"✅ Total updated: {updated_count}")
    
    return updated_count


if __name__ == "__main__":
    print("=" * 60)
    print("DynamoDB cat_color NULL -> #FFDEAD Update Script")
    print("=" * 60)
    print()
    
    # 확인 메시지
    confirm = input("⚠️  This will update all null cat_color to #FFDEAD. Continue? (yes/no): ")
    
    if confirm.lower() == 'yes':
        updated = update_null_cat_colors()
        print(f"\n✅ Successfully updated {updated} records!")
    else:
        print("❌ Update cancelled.")
