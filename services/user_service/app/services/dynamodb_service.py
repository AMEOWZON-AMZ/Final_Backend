"""
DynamoDB 서비스 - 사용자 프로필 + 친구 관계 관리
user_friends 테이블: 본인 프로필 정보 + 친구 ID 목록
"""
import boto3
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from dotenv import load_dotenv
from app.core.config import settings
from botocore.exceptions import ClientError
import logging

# .env 파일 명시적으로 로드
load_dotenv()

logger = logging.getLogger(__name__)


class DynamoDBService:
    def __init__(self):
        """DynamoDB 클라이언트 초기화 (AWS DynamoDB 사용)"""
        # 기본값 설정 (예외 발생 시에도 속성 존재 보장)
        self.dynamodb = None
        self.friends_table = None
        self.friends_table_name = 'user_friends'
        
        try:
            # 로컬 DynamoDB 사용 여부 확인
            use_local = os.getenv("USE_LOCAL_DYNAMODB", "false").lower() == "true"
            
            if use_local:
                # 로컬 DynamoDB
                self.dynamodb = boto3.resource(
                    'dynamodb',
                    endpoint_url=settings.DYNAMODB_ENDPOINT_URL,
                    region_name=settings.DYNAMODB_REGION,
                    aws_access_key_id=settings.DYNAMODB_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.DYNAMODB_SECRET_ACCESS_KEY
                )
                logger.info("✅ DynamoDB Local connected (port 8008)")
            else:
                # AWS DynamoDB (Pod Identity 사용 - 자격증명 자동 제공)
                self.dynamodb = boto3.resource(
                    'dynamodb',
                    region_name=os.getenv("AWS_REGION", "ap-northeast-2")
                    # Pod Identity가 자동으로 자격증명 제공
                )
                logger.info("✅ AWS DynamoDB connected (using Pod Identity)")
            
            # 테이블 초기화 (로컬에서만)
            if use_local:
                self._initialize_tables()
            else:
                # AWS DynamoDB에서는 테이블이 이미 존재한다고 가정
                self.friends_table = self.dynamodb.Table(self.friends_table_name)
                logger.info("✅ Using existing AWS DynamoDB table: user_friends")
            
        except Exception as e:
            logger.error(f"❌ DynamoDB connection failed: {e}")
            self.dynamodb = None
            self.friends_table = None
    
    def _initialize_tables(self):
        """DynamoDB 테이블 생성 (로컬 전용)"""
        try:
            # user_friends 테이블 생성
            try:
                self.friends_table = self.dynamodb.create_table(
                    TableName=self.friends_table_name,
                    KeySchema=[
                        {'AttributeName': 'user_id', 'KeyType': 'HASH'},  # Partition Key
                        {'AttributeName': 'friend_user_id', 'KeyType': 'RANGE'}  # Sort Key
                    ],
                    AttributeDefinitions=[
                        {'AttributeName': 'user_id', 'AttributeType': 'S'},
                        {'AttributeName': 'friend_user_id', 'AttributeType': 'S'}
                    ],
                    BillingMode='PAY_PER_REQUEST'
                )
                self.friends_table.wait_until_exists()
                logger.info("✅ user_friends 테이블 생성 완료")
            except ClientError as e:
                if e.response['Error']['Code'] == 'ResourceInUseException':
                    self.friends_table = self.dynamodb.Table(self.friends_table_name)
                    logger.info("📋 user_friends 테이블 이미 존재")
                else:
                    raise e
                    
            # 더미 데이터 삽입 (로컬 전용)
            self._insert_dummy_data()
            
        except Exception as e:
            logger.error(f"❌ 테이블 초기화 실패: {e}")
    
    def _insert_dummy_data(self):
        """테스트용 더미 데이터 삽입 (로컬 전용)"""
        # 로컬 테스트용 더미 데이터는 별도 스크립트로 관리
        pass
    
    async def get_lobby_friends(self, user_id: str) -> List[Dict]:
        """
        로비 친구 목록 조회 (한 번의 쿼리로 모든 정보 조회)
        친구 관계 레코드에 친구의 모든 프로필 정보가 비정규화되어 저장됨
        자기 자신(self-friend)은 제외
        
        Returns:
            친구 목록 (각 친구의 모든 프로필 정보 포함)
        """
        if not self.dynamodb or not self.friends_table:
            logger.error("DynamoDB 연결 없음")
            return []
        
        try:
            response = self.friends_table.query(
                KeyConditionExpression='user_id = :user_id',
                FilterExpression='#status = :status AND #friend_user_id <> :user_id',  # 자기 자신 제외
                ExpressionAttributeNames={
                    '#status': 'status',
                    '#friend_user_id': 'friend_user_id'
                },
                ExpressionAttributeValues={
                    ':user_id': user_id,
                    ':status': 'accepted'
                }
            )
            
            logger.info(f"✅ 로비 친구 목록 조회: {user_id} - {len(response['Items'])}명")
            return response['Items']
            
        except ClientError as e:
            logger.error(f"❌ 로비 친구 목록 조회 실패: {e}")
            return []
    
    async def get_friend_relation(self, user_id: str, friend_user_id: str) -> Optional[Dict]:
        """
        두 사용자 간의 친구 관계 조회
        
        Args:
            user_id: 조회하는 사용자 ID
            friend_user_id: 대상 사용자 ID
        
        Returns:
            친구 관계 레코드 또는 None
        """
        if not self.dynamodb or not self.friends_table:
            logger.error("DynamoDB 연결 없음")
            return None
        
        try:
            response = self.friends_table.get_item(
                Key={
                    'user_id': user_id,
                    'friend_user_id': friend_user_id
                }
            )
            
            item = response.get('Item')
            if item:
                logger.info(f"✅ 친구 관계 조회: {user_id} -> {friend_user_id} (status: {item.get('status')})")
            return item
            
        except ClientError as e:
            logger.error(f"❌ 친구 관계 조회 실패: {e}")
            return None
    
    async def send_friend_request(
        self, 
        user_id: str, 
        friend_user_id: str,
        current_user_profile: Dict[str, Any],
        friend_profile: Dict[str, Any]
    ) -> bool:
        """
        친구 요청 보내기 (pending 상태)
        
        Args:
            user_id: 요청 보내는 사람 (본인)
            friend_user_id: 요청 받는 사람 (친구)
            current_user_profile: 본인의 프로필 정보
            friend_profile: 친구의 프로필 정보
        """
        if not self.dynamodb or not self.friends_table:
            logger.error("DynamoDB 연결 없음")
            return False
        
        try:
            timestamp = int(datetime.now().timestamp() * 1000)
            
            # 본인 → 친구: sending (내가 보낸 요청)
            self.friends_table.put_item(
                Item={
                    'user_id': user_id,
                    'friend_user_id': friend_user_id,
                    # 친구 프로필 정보 (비정규화)
                    'email': friend_profile.get('email', ''),
                    'nickname': friend_profile.get('nickname', ''),
                    'profile_image_url': friend_profile.get('profile_image_url', ''),
                    'cat_pattern': friend_profile.get('cat_pattern', ''),
                    'cat_color': friend_profile.get('cat_color', ''),
                    'meow_audio_url': friend_profile.get('meow_audio_url', ''),
                    'train_voice_urls': friend_profile.get('train_voice_urls', []),
                    'daily_status': friend_profile.get('daily_status', ''),
                    # 관계 정보
                    'status': 'sending',
                    'created_at': timestamp,
                    'updated_at': timestamp
                }
            )
            
            # 친구 → 본인: pending (친구가 받은 요청)
            self.friends_table.put_item(
                Item={
                    'user_id': friend_user_id,
                    'friend_user_id': user_id,
                    # 본인 프로필 정보 (비정규화)
                    'email': current_user_profile.get('email', ''),
                    'nickname': current_user_profile.get('nickname', ''),
                    'profile_image_url': current_user_profile.get('profile_image_url', ''),
                    'cat_pattern': current_user_profile.get('cat_pattern', ''),
                    'cat_color': current_user_profile.get('cat_color', ''),
                    'meow_audio_url': current_user_profile.get('meow_audio_url', ''),
                    'train_voice_urls': current_user_profile.get('train_voice_urls', []),
                    'daily_status': current_user_profile.get('daily_status', ''),
                    # 관계 정보
                    'status': 'pending',
                    'created_at': timestamp,
                    'updated_at': timestamp
                }
            )
            
            logger.info(f"✅ 친구 요청 전송: {user_id} -> {friend_user_id} (pending)")
            return True
            
        except ClientError as e:
            logger.error(f"❌ 친구 요청 전송 실패: {e}")
            return False
    
    async def accept_friend_request(self, user_id: str, friend_user_id: str) -> bool:
        """
        친구 요청 수락 (pending → accepted)
        
        Args:
            user_id: 요청 받은 사람 (수락하는 사람)
            friend_user_id: 요청 보낸 사람
        """
        if not self.dynamodb or not self.friends_table:
            logger.error("DynamoDB 연결 없음")
            return False
        
        try:
            timestamp = int(datetime.now().timestamp() * 1000)
            
            # 본인 레코드: pending → accepted
            self.friends_table.update_item(
                Key={
                    'user_id': user_id,
                    'friend_user_id': friend_user_id
                },
                UpdateExpression='SET #status = :status, updated_at = :timestamp',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':status': 'accepted',
                    ':timestamp': timestamp
                }
            )
            
            # 친구 레코드: sending → accepted
            self.friends_table.update_item(
                Key={
                    'user_id': friend_user_id,
                    'friend_user_id': user_id
                },
                UpdateExpression='SET #status = :status, updated_at = :timestamp',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':status': 'accepted',
                    ':timestamp': timestamp
                }
            )
            
            logger.info(f"✅ 친구 요청 수락: {user_id} <-> {friend_user_id}")
            return True
            
        except ClientError as e:
            logger.error(f"❌ 친구 요청 수락 실패: {e}")
            return False
    
    async def reject_friend_request(self, user_id: str, friend_user_id: str) -> bool:
        """
        친구 요청 거절 (레코드 삭제)
        
        Args:
            user_id: 요청 받은 사람 (거절하는 사람)
            friend_user_id: 요청 보낸 사람
        """
        if not self.dynamodb or not self.friends_table:
            logger.error("DynamoDB 연결 없음")
            return False
        
        try:
            # 본인 레코드 삭제 (pending)
            self.friends_table.delete_item(
                Key={
                    'user_id': user_id,
                    'friend_user_id': friend_user_id
                }
            )
            
            # 친구 레코드 삭제 (sending)
            self.friends_table.delete_item(
                Key={
                    'user_id': friend_user_id,
                    'friend_user_id': user_id
                }
            )
            
            logger.info(f"✅ 친구 요청 거절: {user_id} X {friend_user_id}")
            return True
            
        except ClientError as e:
            logger.error(f"❌ 친구 요청 거절 실패: {e}")
            return False
    
    async def cancel_friend_request(self, user_id: str, friend_user_id: str) -> bool:
        """
        친구 요청 취소 (보낸 요청 취소)
        
        Args:
            user_id: 요청 보낸 사람 (취소하는 사람)
            friend_user_id: 요청 받은 사람
        """
        if not self.dynamodb or not self.friends_table:
            logger.error("DynamoDB 연결 없음")
            return False
        
        try:
            # 본인 레코드 삭제 (sending)
            self.friends_table.delete_item(
                Key={
                    'user_id': user_id,
                    'friend_user_id': friend_user_id
                }
            )
            
            # 친구 레코드 삭제 (pending)
            self.friends_table.delete_item(
                Key={
                    'user_id': friend_user_id,
                    'friend_user_id': user_id
                }
            )
            
            logger.info(f"✅ 친구 요청 취소: {user_id} -> {friend_user_id}")
            return True
            
        except ClientError as e:
            logger.error(f"❌ 친구 요청 취소 실패: {e}")
            return False
    
    async def remove_friend(self, user_id: str, friend_user_id: str) -> bool:
        """
        친구 삭제 (양방향)
        
        Args:
            user_id: 본인 ID
            friend_user_id: 친구 ID
        """
        if not self.dynamodb or not self.friends_table:
            logger.error("DynamoDB 연결 없음")
            return False
        
        try:
            # 본인 → 친구 관계 삭제
            self.friends_table.delete_item(
                Key={
                    'user_id': user_id,
                    'friend_user_id': friend_user_id
                }
            )
            
            # 친구 → 본인 관계 삭제 (양방향)
            self.friends_table.delete_item(
                Key={
                    'user_id': friend_user_id,
                    'friend_user_id': user_id
                }
            )
            
            logger.info(f"✅ 친구 삭제: {user_id} <-> {friend_user_id}")
            return True
            
        except ClientError as e:
            logger.error(f"❌ 친구 삭제 실패: {e}")
            return False
    
    async def update_daily_status(self, user_id: str, daily_status: str) -> bool:
        """
        일일 상태 업데이트 (하루 1회 AI 추론)
        해당 사용자를 친구로 가진 모든 레코드를 업데이트
        
        Args:
            user_id: 사용자 ID
            daily_status: 추론된 상태 메시지
        """
        if not self.dynamodb or not self.friends_table:
            logger.error("DynamoDB 연결 없음")
            return False
        
        try:
            timestamp = int(datetime.now().timestamp() * 1000)
            
            # 이 사용자를 친구로 가진 모든 레코드 조회
            # GSI가 없으므로 scan 사용 (프로덕션에서는 GSI 추가 권장)
            response = self.friends_table.scan(
                FilterExpression='friend_user_id = :friend_id',
                ExpressionAttributeValues={
                    ':friend_id': user_id
                }
            )
            
            # 각 레코드의 daily_status 업데이트
            for item in response['Items']:
                self.friends_table.update_item(
                    Key={
                        'user_id': item['user_id'],
                        'friend_user_id': user_id
                    },
                    UpdateExpression='SET daily_status = :status, updated_at = :timestamp',
                    ExpressionAttributeValues={
                        ':status': daily_status,
                        ':timestamp': timestamp
                    }
                )
            
            logger.info(f"✅ 일일 상태 업데이트: {user_id} - {len(response['Items'])}개 레코드 업데이트")
            return True
            
        except ClientError as e:
            logger.error(f"❌ 일일 상태 업데이트 실패: {e}")
            return False
    
    async def update_user_profile_in_friends(self, user_id: str, profile_data: Dict[str, Any]) -> bool:
        """
        사용자 프로필 업데이트 시 모든 친구 레코드의 해당 사용자 정보 업데이트
        
        Args:
            user_id: 사용자 ID
            profile_data: 업데이트할 프로필 정보
        """
        if not self.dynamodb or not self.friends_table:
            logger.error("DynamoDB 연결 없음")
            return False
        
        try:
            timestamp = int(datetime.now().timestamp() * 1000)
            
            # 이 사용자를 친구로 가진 모든 레코드 조회
            response = self.friends_table.scan(
                FilterExpression='friend_user_id = :friend_id',
                ExpressionAttributeValues={
                    ':friend_id': user_id
                }
            )
            
            # 업데이트 표현식 구성
            update_parts = []
            expr_values = {':timestamp': timestamp}
            
            if 'nickname' in profile_data:
                update_parts.append('nickname = :nickname')
                expr_values[':nickname'] = profile_data['nickname']
            if 'profile_image_url' in profile_data:
                update_parts.append('profile_image_url = :profile_image_url')
                expr_values[':profile_image_url'] = profile_data['profile_image_url']
            if 'cat_pattern' in profile_data:
                update_parts.append('cat_pattern = :cat_pattern')
                expr_values[':cat_pattern'] = profile_data['cat_pattern']
            if 'cat_color' in profile_data:
                update_parts.append('cat_color = :cat_color')
                expr_values[':cat_color'] = profile_data['cat_color']
            if 'meow_audio_url' in profile_data:
                update_parts.append('meow_audio_url = :meow_audio_url')
                expr_values[':meow_audio_url'] = profile_data['meow_audio_url']
            if 'train_voice_urls' in profile_data:
                update_parts.append('train_voice_urls = :train_voice_urls')
                expr_values[':train_voice_urls'] = profile_data['train_voice_urls']
            
            if not update_parts:
                logger.warning("업데이트할 프로필 정보 없음")
                return True
            
            update_parts.append('updated_at = :timestamp')
            update_expression = 'SET ' + ', '.join(update_parts)
            
            # 각 레코드 업데이트
            for item in response['Items']:
                self.friends_table.update_item(
                    Key={
                        'user_id': item['user_id'],
                        'friend_user_id': user_id
                    },
                    UpdateExpression=update_expression,
                    ExpressionAttributeValues=expr_values
                )
            
            logger.info(f"✅ 프로필 업데이트 전파: {user_id} - {len(response['Items'])}개 레코드 업데이트")
            return True
            
        except ClientError as e:
            logger.error(f"❌ 프로필 업데이트 전파 실패: {e}")
            return False
    
    async def get_pending_requests(self, user_id: str) -> List[Dict]:
        """
        받은 친구 요청 목록 조회 (pending)
        
        Args:
            user_id: 조회하는 사용자 ID
        
        Returns:
            받은 친구 요청 목록
        """
        if not self.dynamodb or not self.friends_table:
            logger.error("DynamoDB 연결 없음")
            return []
        
        try:
            response = self.friends_table.query(
                KeyConditionExpression='user_id = :user_id',
                FilterExpression='#status = :status',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':user_id': user_id,
                    ':status': 'pending'
                }
            )
            
            logger.info(f"✅ 받은 친구 요청 조회: {user_id} - {len(response['Items'])}개")
            return response['Items']
            
        except ClientError as e:
            logger.error(f"❌ 받은 친구 요청 조회 실패: {e}")
            return []
    
    async def get_sending_requests(self, user_id: str) -> List[Dict]:
        """
        보낸 친구 요청 목록 조회 (sending)
        
        Args:
            user_id: 조회하는 사용자 ID
        
        Returns:
            보낸 친구 요청 목록
        """
        if not self.dynamodb or not self.friends_table:
            logger.error("DynamoDB 연결 없음")
            return []
        
        try:
            response = self.friends_table.query(
                KeyConditionExpression='user_id = :user_id',
                FilterExpression='#status = :status',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':user_id': user_id,
                    ':status': 'sending'
                }
            )
            
            logger.info(f"✅ 보낸 친구 요청 조회: {user_id} - {len(response['Items'])}개")
            return response['Items']
            
        except ClientError as e:
            logger.error(f"❌ 보낸 친구 요청 조회 실패: {e}")
            return []
    
    async def get_accepted_friends(self, user_id: str) -> List[Dict]:
        """
        수락된 친구 목록 조회 (accepted)
        
        Args:
            user_id: 조회하는 사용자 ID
        
        Returns:
            친구 목록
        """
        if not self.dynamodb or not self.friends_table:
            logger.error("DynamoDB 연결 없음")
            return []
        
        try:
            response = self.friends_table.query(
                KeyConditionExpression='user_id = :user_id',
                FilterExpression='#status = :status',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':user_id': user_id,
                    ':status': 'accepted'
                }
            )
            
            logger.info(f"✅ 친구 목록 조회: {user_id} - {len(response['Items'])}명")
            return response['Items']
            
        except ClientError as e:
            logger.error(f"❌ 친구 목록 조회 실패: {e}")
            return []
    
    async def create_self_friend_record(self, user_id: str, profile_data: Dict[str, Any]) -> bool:
        """
        자기 자신을 친구로 추가 (본인 status 저장용)
        
        Args:
            user_id: 사용자 ID
            profile_data: 사용자 프로필 정보
        
        Returns:
            성공 여부
        """
        if not self.dynamodb or not self.friends_table:
            logger.error("DynamoDB 연결 없음")
            return False
        
        try:
            timestamp = int(datetime.now().timestamp() * 1000)
            
            self.friends_table.put_item(
                Item={
                    'user_id': user_id,
                    'friend_user_id': user_id,  # 자기 자신
                    'status': 'self',  # 특별한 상태
                    'daily_status': '',  # 초기값
                    'email': profile_data.get('email', ''),
                    'nickname': profile_data.get('nickname', ''),
                    'profile_image_url': profile_data.get('profile_image_url', ''),
                    'cat_pattern': profile_data.get('cat_pattern', ''),
                    'cat_color': profile_data.get('cat_color', ''),
                    'meow_audio_url': profile_data.get('meow_audio_url', ''),
                    'train_voice_urls': profile_data.get('train_voice_urls', []),
                    'created_at': timestamp,
                    'updated_at': timestamp
                }
            )
            
            logger.info(f"✅ Self-friend 레코드 생성: {user_id}")
            return True
            
        except ClientError as e:
            logger.error(f"❌ Self-friend 레코드 생성 실패: {e}")
            return False
    
    async def update_my_daily_status(self, user_id: str, daily_status: str) -> bool:
        """
        본인의 일일 상태 업데이트
        
        Args:
            user_id: 사용자 ID
            daily_status: 상태 메시지
        
        Returns:
            성공 여부
        """
        if not self.dynamodb or not self.friends_table:
            logger.error("DynamoDB 연결 없음")
            return False
        
        try:
            timestamp = int(datetime.now().timestamp() * 1000)
            
            self.friends_table.update_item(
                Key={
                    'user_id': user_id,
                    'friend_user_id': user_id  # 자기 자신
                },
                UpdateExpression='SET daily_status = :status, updated_at = :timestamp',
                ExpressionAttributeValues={
                    ':status': daily_status,
                    ':timestamp': timestamp
                }
            )
            
            logger.info(f"✅ 본인 status 업데이트: {user_id} - {daily_status}")
            return True
            
        except ClientError as e:
            logger.error(f"❌ 본인 status 업데이트 실패: {e}")
            return False
    
    async def get_my_daily_status(self, user_id: str) -> Optional[str]:
        """
        본인의 일일 상태 조회
        
        Args:
            user_id: 사용자 ID
        
        Returns:
            상태 메시지 또는 None
        """
        if not self.dynamodb or not self.friends_table:
            logger.error("DynamoDB 연결 없음")
            return None
        
        try:
            response = self.friends_table.get_item(
                Key={
                    'user_id': user_id,
                    'friend_user_id': user_id
                }
            )
            
            item = response.get('Item')
            if item:
                daily_status = item.get('daily_status', '')
                logger.info(f"✅ 본인 status 조회: {user_id} - {daily_status}")
                return daily_status
            else:
                logger.warning(f"⚠️ Self-friend 레코드 없음: {user_id}")
                return None
            
        except ClientError as e:
            logger.error(f"❌ 본인 status 조회 실패: {e}")
            return None


# 전역 DynamoDB 서비스 인스턴스
dynamodb_service = DynamoDBService()
