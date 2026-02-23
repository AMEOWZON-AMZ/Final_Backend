from typing import List, Optional, Dict, Any
from datetime import datetime
from app.services.dynamodb_service import dynamodb_service
import logging

logger = logging.getLogger(__name__)


class FriendService:
    def __init__(self):
        """DynamoDB 기반 친구 서비스"""
        self.dynamodb = dynamodb_service
    
    async def add_friend(self, user_id: str, friend_id: str) -> Dict[str, Any]:
        """친구 추가 요청 (DynamoDB)"""
        if user_id == friend_id:
            raise ValueError("Cannot add yourself as a friend")
        
        # DynamoDB에 친구 요청 추가
        success = await self.dynamodb.add_friend_relationship(user_id, friend_id)
        
        if not success:
            raise ValueError("Failed to add friend relationship")
        
        return {
            "user_id": user_id,
            "friend_user_id": friend_id,
            "status": "pending",
            "created_at": int(datetime.now().timestamp() * 1000)
        }
    
    async def get_user_friends(self, user_id: str) -> List[Dict[str, Any]]:
        """사용자의 친구 목록 조회 (DynamoDB)"""
        return await self.dynamodb.get_user_friends(user_id)
    
    async def accept_friend_request(self, user_id: str, friend_id: str) -> bool:
        """친구 요청 수락 (DynamoDB)"""
        success = await self.dynamodb.accept_friend_relationship(user_id, friend_id)
        
        if not success:
            raise ValueError("Failed to accept friend request")
        
        return True
    
    async def remove_friendship(self, user_id: str, friend_id: str) -> bool:
        """친구 관계 삭제 (DynamoDB)"""
        return await self.dynamodb.remove_friend_relationship(user_id, friend_id)
    
    async def get_pending_requests(self, user_id: str) -> List[Dict[str, Any]]:
        """받은 친구 요청 목록 조회 (DynamoDB)"""
        try:
            # DynamoDB에서 pending 상태의 친구 요청 조회
            response = self.dynamodb.friends_table.query(
                IndexName='friend_user_id-index',  # GSI 필요
                KeyConditionExpression='friend_user_id = :user_id',
                FilterExpression='#status = :status',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':user_id': user_id,
                    ':status': 'pending'
                }
            )
            
            return response.get('Items', [])
            
        except Exception as e:
            logger.error(f"❌ 친구 요청 조회 실패: {e}")
            return []