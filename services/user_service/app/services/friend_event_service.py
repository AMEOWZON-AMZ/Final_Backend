"""
친구 이벤트 서비스
DynamoDB outbox_events 테이블에 이벤트 저장
Push Worker Pod가 이를 읽어서 FCM 전송
"""
import boto3
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional, Set
from app.core.config import settings

logger = logging.getLogger(__name__)


def now_utc_iso() -> str:
    """UTC 현재 시간을 ISO 8601 형식으로 반환"""
    return datetime.now(timezone.utc).isoformat()


class FriendEventService:
    """친구 관련 이벤트를 DynamoDB outbox_events에 저장"""
    
    def __init__(self):
        """DynamoDB 클라이언트 초기화"""
        self.dynamodb = None
        self.table = None
        self.table_name = 'OutboxEvents'
        
        try:
            self.dynamodb = boto3.resource(
                'dynamodb',
                region_name=settings.AWS_REGION
            )
            self.table = self.dynamodb.Table(self.table_name)
            logger.info(f"✅ FriendEventService initialized with table: {self.table_name}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize FriendEventService: {e}")
    
    def _enqueue_friend_event(
        self,
        event_type: str,
        to_user_id: str,
        from_user_id: str,
        from_nickname: str
    ) -> bool:
        """
        친구 이벤트를 outbox_events 테이블에 저장
        
        Args:
            event_type: 이벤트 타입 (FRIEND_REQUEST, FRIEND_ACCEPTED, FRIEND_REJECTED)
            to_user_id: 이벤트를 받을 사용자 ID
            from_user_id: 이벤트를 발생시킨 사용자 ID
            from_nickname: 이벤트를 발생시킨 사용자 닉네임
        
        Returns:
            성공 여부
        """
        if not self.table:
            logger.error("❌ DynamoDB table not initialized")
            return False
        
        try:
            created_at = now_utc_iso()
            event_id = f"{event_type}#{created_at[:10]}#{to_user_id}#{uuid.uuid4().hex[:8]}"
            
            item = {
                "pk": f"EVENT#{event_id}",
                "sk": "EVENT",
                "event_id": event_id,
                "event_type": event_type,
                "to_user_id": to_user_id,
                "from_user_id": from_user_id,
                "from_nickname": from_nickname,
                "created_at": created_at,
                "status": "pending"
            }
            
            self.table.put_item(Item=item)
            logger.info(f"✅ Friend event enqueued: {event_type} to {to_user_id} from {from_user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to enqueue friend event: {e}")
            return False
    
    def enqueue_friend_request(
        self,
        to_user_id: str,
        from_user_id: str,
        from_nickname: str
    ) -> bool:
        """
        친구 요청 이벤트 저장
        
        Args:
            to_user_id: 요청을 받는 사용자 ID
            from_user_id: 요청을 보낸 사용자 ID
            from_nickname: 요청을 보낸 사용자 닉네임
        """
        return self._enqueue_friend_event(
            event_type="FRIEND_REQUEST",
            to_user_id=to_user_id,
            from_user_id=from_user_id,
            from_nickname=from_nickname
        )
    
    def enqueue_friend_accepted(
        self,
        to_user_id: str,
        from_user_id: str,
        from_nickname: str
    ) -> bool:
        """
        친구 수락 이벤트 저장
        
        Args:
            to_user_id: 수락 알림을 받을 사용자 ID (요청 보낸 사람)
            from_user_id: 수락한 사용자 ID
            from_nickname: 수락한 사용자 닉네임
        """
        return self._enqueue_friend_event(
            event_type="FRIEND_ACCEPTED",
            to_user_id=to_user_id,
            from_user_id=from_user_id,
            from_nickname=from_nickname
        )
    
    def enqueue_friend_rejected(
        self,
        to_user_id: str,
        from_user_id: str,
        from_nickname: str
    ) -> bool:
        """
        친구 거절 이벤트 저장 (선택적)
        
        Args:
            to_user_id: 거절 알림을 받을 사용자 ID (요청 보낸 사람)
            from_user_id: 거절한 사용자 ID
            from_nickname: 거절한 사용자 닉네임
        """
        return self._enqueue_friend_event(
            event_type="FRIEND_REJECTED",
            to_user_id=to_user_id,
            from_user_id=from_user_id,
            from_nickname=from_nickname
        )


# 전역 인스턴스
friend_event_service = FriendEventService()
