"""
DynamoDB 수동 업데이트 스크립트
"""
import boto3
from dotenv import load_dotenv

load_dotenv()

# DynamoDB 클라이언트
dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-2')
table = dynamodb.Table('user_friends')

def update_to_empty_string(user_id: str, friend_user_id: str):
    """cat_color를 빈 문자열로 업데이트"""
    response = table.update_item(
        Key={
            'user_id': user_id,
            'friend_user_id': friend_user_id
        },
        UpdateExpression='SET cat_color = :color',
        ExpressionAttributeValues={
            ':color': ''  # 빈 문자열
        },
        ReturnValues='ALL_NEW'
    )
    print(f"✅ Updated to empty string: {response['Attributes']}")
    return response

def update_to_null(user_id: str, friend_user_id: str):
    """cat_color를 NULL로 업데이트"""
    response = table.update_item(
        Key={
            'user_id': user_id,
            'friend_user_id': friend_user_id
        },
        UpdateExpression='SET cat_color = :color',
        ExpressionAttributeValues={
            ':color': None  # NULL
        },
        ReturnValues='ALL_NEW'
    )
    print(f"✅ Updated to NULL: {response['Attributes']}")
    return response

def remove_field(user_id: str, friend_user_id: str):
    """cat_color 필드 제거"""
    response = table.update_item(
        Key={
            'user_id': user_id,
            'friend_user_id': friend_user_id
        },
        UpdateExpression='REMOVE cat_color',
        ReturnValues='ALL_NEW'
    )
    print(f"✅ Removed field: {response['Attributes']}")
    return response

def update_to_color(user_id: str, friend_user_id: str, color: str):
    """cat_color를 특정 색상으로 업데이트"""
    response = table.update_item(
        Key={
            'user_id': user_id,
            'friend_user_id': friend_user_id
        },
        UpdateExpression='SET cat_color = :color',
        ExpressionAttributeValues={
            ':color': color
        },
        ReturnValues='ALL_NEW'
    )
    print(f"✅ Updated to {color}: {response['Attributes']}")
    return response

def get_item(user_id: str, friend_user_id: str):
    """아이템 조회"""
    response = table.get_item(
        Key={
            'user_id': user_id,
            'friend_user_id': friend_user_id
        }
    )
    if 'Item' in response:
        print(f"📋 Item found:")
        for key, value in response['Item'].items():
            print(f"  - {key}: {value}")
        return response['Item']
    else:
        print(f"❌ Item not found")
        return None

def scan_all():
    """전체 테이블 스캔"""
    response = table.scan()
    items = response.get('Items', [])
    
    print(f"📊 Total items: {len(items)}")
    for idx, item in enumerate(items, 1):
        print(f"\n[{idx}] user_id: {item.get('user_id')}, friend_user_id: {item.get('friend_user_id')}")
        print(f"    cat_color: {item.get('cat_color')}")
        print(f"    nickname: {item.get('nickname')}")
    
    return items


if __name__ == "__main__":
    print("=" * 60)
    print("DynamoDB Manual Update Script")
    print("=" * 60)
    print()
    
    # 사용 예시
    print("사용 가능한 함수:")
    print("1. scan_all() - 전체 데이터 조회")
    print("2. get_item(user_id, friend_user_id) - 특정 아이템 조회")
    print("3. update_to_empty_string(user_id, friend_user_id) - 빈 문자열로 업데이트")
    print("4. update_to_null(user_id, friend_user_id) - NULL로 업데이트")
    print("5. remove_field(user_id, friend_user_id) - 필드 제거")
    print("6. update_to_color(user_id, friend_user_id, '#FFDEAD') - 특정 색상으로 업데이트")
    print()
    print("예시:")
    print("  python -i dynamodb_manual_update.py")
    print("  >>> scan_all()")
    print("  >>> update_to_color('user123', 'friend456', '#FFDEAD')")
    print()
