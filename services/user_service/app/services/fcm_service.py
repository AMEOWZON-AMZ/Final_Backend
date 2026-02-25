"""
Firebase Cloud Messaging (FCM) 푸시 알림 서비스
"""
import firebase_admin
from firebase_admin import credentials, messaging
from typing import Optional, Dict, Any
import logging
import os

logger = logging.getLogger(__name__)


class FCMService:
    def __init__(self):
        """FCM 서비스 초기화"""
        self.initialized = False
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Firebase Admin SDK 초기화"""
        try:
            # 이미 초기화되어 있는지 확인
            if firebase_admin._apps:
                self.initialized = True
                logger.info("✅ Firebase already initialized")
                return
            
            # Firebase 서비스 계정 키 파일 경로
            cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "/app/firebase-credentials.json")
            
            if os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                self.initialized = True
                logger.info("✅ Firebase initialized successfully")
            else:
                logger.warning(f"⚠️ Firebase credentials not found at {cred_path}")
                self.initialized = False
                
        except Exception as e:
            logger.error(f"❌ Firebase initialization failed: {e}")
            self.initialized = False
    
    async def send_notification(
        self,
        token: str,
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        FCM 푸시 알림 전송
        
        Args:
            token: FCM 디바이스 토큰
            title: 알림 제목
            body: 알림 내용
            data: 추가 데이터 (선택)
        
        Returns:
            성공 여부
        """
        if not self.initialized:
            logger.warning("⚠️ FCM not initialized, skipping notification")
            return False
        
        if not token:
            logger.warning("⚠️ No FCM token provided")
            return False
        
        try:
            # FCM 메시지 생성
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                token=token,
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        sound='default',
                        channel_id='friend_requests'
                    )
                ),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            sound='default',
                            badge=1
                        )
                    )
                )
            )
            
            # 메시지 전송
            response = messaging.send(message)
            logger.info(f"✅ FCM notification sent successfully: {response}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send FCM notification: {e}")
            return False
    
    async def send_friend_request_notification(
        self,
        token: str,
        sender_nickname: str,
        sender_user_id: str
    ) -> bool:
        """
        친구 요청 알림 전송
        
        Args:
            token: 수신자의 FCM 토큰
            sender_nickname: 요청 보낸 사람의 닉네임
            sender_user_id: 요청 보낸 사람의 user_id
        """
        return await self.send_notification(
            token=token,
            title="새로운 친구 요청",
            body=f"{sender_nickname}님이 친구 요청을 보냈습니다.",
            data={
                "type": "friend_request",
                "sender_user_id": sender_user_id,
                "sender_nickname": sender_nickname
            }
        )
    
    async def send_friend_accepted_notification(
        self,
        token: str,
        accepter_nickname: str,
        accepter_user_id: str
    ) -> bool:
        """
        친구 수락 알림 전송
        
        Args:
            token: 수신자의 FCM 토큰 (요청 보낸 사람)
            accepter_nickname: 수락한 사람의 닉네임
            accepter_user_id: 수락한 사람의 user_id
        """
        return await self.send_notification(
            token=token,
            title="친구 요청 수락됨",
            body=f"{accepter_nickname}님이 친구 요청을 수락했습니다.",
            data={
                "type": "friend_accepted",
                "accepter_user_id": accepter_user_id,
                "accepter_nickname": accepter_nickname
            }
        )
    
    async def send_challenge_notification(
        self,
        token: str,
        challenge_title: str,
        challenge_id: str
    ) -> bool:
        """
        챌린지 알림 전송
        
        Args:
            token: 수신자의 FCM 토큰
            challenge_title: 챌린지 제목
            challenge_id: 챌린지 ID
        """
        return await self.send_notification(
            token=token,
            title="새로운 챌린지",
            body=f"오늘의 챌린지: {challenge_title}",
            data={
                "type": "new_challenge",
                "challenge_id": challenge_id,
                "challenge_title": challenge_title
            }
        )


# 싱글톤 인스턴스
fcm_service = FCMService()
