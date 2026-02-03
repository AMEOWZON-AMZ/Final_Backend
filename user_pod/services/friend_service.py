from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger

from app.schemas.user import FriendResponse
from app.services.user_service import UserService


class FriendService:
    def __init__(self, db: Session):
        self.db = db
        self.user_service = UserService(db)
        # 메모리 기반 친구 저장소 (테스트용)
        self._friends_storage = {}
    
    async def get_user_friends(self, user_id: str) -> List[FriendResponse]:
        """사용자의 친구 목록 조회"""
        try:
            friends_data = self._friends_storage.get(user_id, [])
            friends = []
            
            # 친구들의 상세 정보 조회
            if friends_data:
                friend_ids = [item['friend_id'] for item in friends_data]
                friend_users = await self.user_service.get_users_by_social_ids(friend_ids)
                
                # 사용자 정보를 딕셔너리로 변환
                user_dict = {str(user.id): user for user in friend_users}
                
                for friend_item in friends_data:
                    friend_id = friend_item['friend_id']
                    friend_user = user_dict.get(friend_id)
                    
                    friend_response = FriendResponse(
                        user_id=user_id,
                        friend_id=friend_id,
                        friend_name=friend_user.full_name if friend_user else None,
                        friend_email=friend_user.email if friend_user else None,
                        friend_profile_image=friend_user.profile_image_url if friend_user else None,
                        created_at=datetime.fromisoformat(friend_item.get('created_at', datetime.utcnow().isoformat())),
                        status=friend_item.get('status', 'active')
                    )
                    friends.append(friend_response)
            
            return friends
            
        except Exception as e:
            logger.error(f"Get user friends failed: {e}")
            return []
    
    async def add_friend(self, user_id: str, friend_id: str) -> Dict[str, Any]:
        """친구 추가"""
        try:
            # 친구로 추가할 사용자가 존재하는지 확인
            friend_user = await self.user_service.get_user_by_id(int(friend_id))
            if not friend_user:
                raise ValueError("Friend user not found")
            
            # 이미 친구인지 확인
            existing_friendship = await self.check_friendship(user_id, friend_id)
            if existing_friendship:
                raise ValueError("Already friends")
            
            current_time = datetime.utcnow().isoformat()
            
            # 양방향 친구 관계 생성
            if user_id not in self._friends_storage:
                self._friends_storage[user_id] = []
            if friend_id not in self._friends_storage:
                self._friends_storage[friend_id] = []
                
            self._friends_storage[user_id].append({
                'friend_id': friend_id,
                'created_at': current_time,
                'status': 'active'
            })
            
            self._friends_storage[friend_id].append({
                'friend_id': user_id,
                'created_at': current_time,
                'status': 'active'
            })
            
            logger.info(f"Friendship created: {user_id} <-> {friend_id}")
            
            return {
                "user_id": user_id,
                "friend_id": friend_id,
                "status": "active",
                "created_at": current_time
            }
            
        except Exception as e:
            logger.error(f"Add friend failed: {e}")
            raise
    
    async def remove_friend(self, user_id: str, friend_id: str) -> Dict[str, Any]:
        """친구 삭제"""
        try:
            # 친구 관계가 존재하는지 확인
            existing_friendship = await self.check_friendship(user_id, friend_id)
            if not existing_friendship:
                raise ValueError("Friendship not found")
            
            # 양방향 친구 관계 삭제
            if user_id in self._friends_storage:
                self._friends_storage[user_id] = [
                    f for f in self._friends_storage[user_id] 
                    if f['friend_id'] != friend_id
                ]
            
            if friend_id in self._friends_storage:
                self._friends_storage[friend_id] = [
                    f for f in self._friends_storage[friend_id] 
                    if f['friend_id'] != user_id
                ]
            
            logger.info(f"Friendship removed: {user_id} <-> {friend_id}")
            
            return {
                "user_id": user_id,
                "friend_id": friend_id,
                "status": "removed",
                "removed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Remove friend failed: {e}")
            raise
    
    async def check_friendship(self, user_id: str, friend_id: str) -> Optional[Dict[str, Any]]:
        """친구 관계 확인"""
        try:
            if user_id in self._friends_storage:
                for friend in self._friends_storage[user_id]:
                    if friend['friend_id'] == friend_id:
                        return friend
            return None
            
        except Exception as e:
            logger.error(f"Check friendship failed: {e}")
            return None