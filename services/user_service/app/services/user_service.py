from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.models.user import User
from app.models.friend import Friend
from app.schemas.user import UserCreate, UserUpdate, TokenInfo, LobbyFriend, CatProfile
import logging

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """이메일로 사용자 조회"""
        return self.db.query(User).filter(User.email == email).first()
    
    async def create_or_update_user_from_token(self, token_info: TokenInfo) -> User:
        """토큰 정보로부터 사용자 생성 또는 업데이트"""
        
        # 기존 사용자 확인 (user_id = sub)
        existing_user = self.db.query(User).filter(
            User.user_id == token_info.sub
        ).first()
        
        if existing_user:
            # 기존 사용자 정보 업데이트
            if token_info.email and existing_user.email != token_info.email:
                existing_user.email = token_info.email
            
            self.db.commit()
            self.db.refresh(existing_user)
            
            return existing_user
        
        # 새 사용자 생성
        # TEST_TOKEN 사용 시 email이 None일 수 있음
        # 이 경우 임시 email 생성하되, 사용자가 프로필 설정에서 변경 가능
        if not token_info.email:
            # 임시 이메일 생성 (프로필 설정 필요)
            temp_email = f"{token_info.sub}@temp.example.com"
            temp_nickname = token_info.sub[:20]  # user_id 앞 20자
        else:
            temp_email = token_info.email
            temp_nickname = token_info.email.split('@')[0]
        
        new_user = User(
            user_id=token_info.sub,  # Google/Cognito sub를 user_id로 사용
            email=temp_email,
            nickname=temp_nickname,
            provider="google"  # 또는 "cognito"
        )
        
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        
        return new_user
    
    async def create_user_from_signup(self, signup_data) -> User:
        """회원가입으로 사용자 생성 (Google/Cognito 전용)"""
        from app.services.dynamodb_service import dynamodb_service
        
        # 중복 확인 (user_id, 이메일, 닉네임)
        existing_user = self.db.query(User).filter(
            (User.user_id == signup_data.user_id) |
            (User.email == signup_data.email) | 
            (User.nickname == signup_data.nickname)
        ).first()
        
        if existing_user:
            if existing_user.user_id == signup_data.user_id:
                raise ValueError("이미 가입된 사용자입니다")
            elif existing_user.email == signup_data.email:
                raise ValueError("이미 사용 중인 이메일입니다")
            else:
                raise ValueError("이미 사용 중인 닉네임입니다")
        
        # 고유한 친구 코드 생성
        from app.models.user import generate_friend_code
        
        while True:
            friend_code = generate_friend_code()
            existing_code = self.db.query(User).filter(User.friend_code == friend_code).first()
            if not existing_code:
                break
        
        # 사용자 생성 (user_id = Google/Cognito sub)
        import json
        
        new_user = User(
            user_id=signup_data.user_id,  # 프론트엔드에서 받은 Google/Cognito sub 사용
            email=signup_data.email,
            nickname=signup_data.nickname,
            provider="google",  # 또는 "cognito"
            friend_code=friend_code,
            # 고양이 프로필 정보
            cat_pattern=signup_data.cat_pattern,
            cat_color=signup_data.cat_color,
            # 음성 파일 정보
            meow_audio_url=signup_data.meow_audio_url,
            train_voice_urls=json.dumps(signup_data.train_voice_urls) if hasattr(signup_data, 'train_voice_urls') and signup_data.train_voice_urls else '[]',
            # 프로필 이미지
            profile_image_url=signup_data.profile_image_url if hasattr(signup_data, 'profile_image_url') else None,
            # FCM 토큰
            token=signup_data.token if hasattr(signup_data, 'token') else None,
            # 프로필 완성도 체크
            profile_setup_completed=self._is_profile_complete(signup_data)
        )
        
        try:
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
            
            # Self-Friend 레코드 생성 (본인 status 저장용)
            import json
            train_voice_urls = json.loads(new_user.train_voice_urls) if new_user.train_voice_urls else []
            
            profile_data = {
                'email': new_user.email,
                'nickname': new_user.nickname,
                'profile_image_url': new_user.profile_image_url,
                'cat_pattern': new_user.cat_pattern,
                'cat_color': new_user.cat_color,
                'meow_audio_url': new_user.meow_audio_url,
                'train_voice_urls': train_voice_urls
            }
            
            await dynamodb_service.create_self_friend_record(new_user.user_id, profile_data)
            logger.info(f"✅ Self-friend 레코드 생성 완료: {new_user.user_id}")
            
            return new_user
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"사용자 생성 중 오류가 발생했습니다: {str(e)}")
    
    def _is_profile_complete(self, signup_data) -> bool:
        """프로필 완성도 체크"""
        has_cat_info = signup_data.cat_pattern and signup_data.cat_color
        has_audio_info = signup_data.meow_audio_url or (hasattr(signup_data, 'train_voice_urls') and signup_data.train_voice_urls)
        return bool(has_cat_info and has_audio_info)

    async def get_lobby_friends(self, user_id: str) -> List[LobbyFriend]:
        """
        로비용 친구 목록 조회 (DynamoDB만 사용)
        - DynamoDB: 친구 관계 레코드에 친구의 모든 프로필 정보가 비정규화되어 저장됨
        """
        from app.services.dynamodb_service import dynamodb_service
        
        # DynamoDB에서 친구 목록 조회 (한 번의 쿼리로 모든 정보 조회)
        friends_data = await dynamodb_service.get_lobby_friends(user_id)
        
        lobby_friends = []
        for friend_data in friends_data:
            lobby_friend = LobbyFriend(
                user_id=friend_data.get('friend_user_id'),
                email=friend_data.get('email', ''),
                nickname=friend_data.get('nickname', ''),
                profile_image_url=friend_data.get('profile_image_url'),
                cat_pattern=friend_data.get('cat_pattern'),
                cat_color=friend_data.get('cat_color'),
                meow_audio_url=friend_data.get('meow_audio_url'),
                train_voice_urls=friend_data.get('train_voice_urls', []),
                daily_status=friend_data.get('daily_status'),
                created_at_timestamp=friend_data.get('created_at', 0),
                updated_at_timestamp=friend_data.get('updated_at', 0)
            )
            lobby_friends.append(lobby_friend)
        
        return lobby_friends
    
    async def setup_user_profile(self, user_id: str, profile_data: dict) -> Optional[User]:
        """사용자 프로필 설정 (고양이 정보 포함)"""
        user = self.db.query(User).filter(User.user_id == user_id).first()
        if not user:
            return None
        
        # 프로필 정보 업데이트 (DB에서 가져온 기존 값 유지)
        if "nickname" in profile_data:
            user.nickname = profile_data["nickname"]
        if "cat_pattern" in profile_data:
            user.cat_pattern = profile_data["cat_pattern"]
        if "cat_color" in profile_data:
            user.cat_color = profile_data["cat_color"]
        if "meow_audio_url" in profile_data:
            user.meow_audio_url = profile_data["meow_audio_url"]
        if "train_voice_urls" in profile_data:
            import json
            user.train_voice_urls = json.dumps(profile_data["train_voice_urls"]) if isinstance(profile_data["train_voice_urls"], list) else profile_data["train_voice_urls"]
        
        user.profile_setup_completed = True
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    async def create_user(self, user_data: UserCreate) -> User:
        """새 사용자 생성 (관리자용)"""
        from app.core.security import generate_sub
        
        # 중복 확인
        existing_user = self.db.query(User).filter(
            User.email == user_data.email
        ).first()
        
        if existing_user:
            raise ValueError("User with this email already exists")
        
        # 사용자 생성
        db_user = User(
            user_id=generate_sub(),  # Google/Cognito sub 생성하여 user_id로 사용
            email=user_data.email,
            nickname=user_data.nickname,
            provider=user_data.provider,
            profile_image_url=user_data.profile_image_url,
            cat_pattern=user_data.cat_pattern,
            cat_color=user_data.cat_color,
            meow_audio_url=user_data.meow_audio_url,
            train_voice_urls=json.dumps(user_data.train_voice_urls) if hasattr(user_data, 'train_voice_urls') and user_data.train_voice_urls else '[]'
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    async def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """사용자 목록 조회"""
        return self.db.query(User).offset(skip).limit(limit).all()
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """user_id로 사용자 조회 (user_id = Google/Cognito sub)"""
        return self.db.query(User).filter(User.user_id == user_id).first()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """이메일로 사용자 조회"""
        return self.db.query(User).filter(User.email == email).first()
    
    async def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[User]:
        """사용자 정보 수정 + DynamoDB 친구 레코드 동기화"""
        from app.services.dynamodb_service import dynamodb_service
        
        db_user = self.db.query(User).filter(User.user_id == user_id).first()
        if not db_user:
            return None
        
        # exclude_unset=True로 실제 전송된 필드만 가져오기
        update_data = user_data.model_dump(exclude_unset=True)
        
        # None이 아닌 값만 업데이트 (email 같은 NOT NULL 필드 보호)
        for field, value in update_data.items():
            if value is not None:
                setattr(db_user, field, value)
        
        # updated_at_timestamp 갱신
        import time
        db_user.updated_at_timestamp = int(time.time() * 1000)
        
        self.db.commit()
        self.db.refresh(db_user)
        
        # DynamoDB 친구 레코드 동기화 (비정규화된 프로필 정보 업데이트)
        import json
        train_voice_urls = json.loads(db_user.train_voice_urls) if db_user.train_voice_urls else []
        
        profile_data = {
            'email': db_user.email,
            'nickname': db_user.nickname,
            'profile_image_url': db_user.profile_image_url,
            'cat_pattern': db_user.cat_pattern,
            'cat_color': db_user.cat_color,
            'meow_audio_url': db_user.meow_audio_url,
            'train_voice_urls': train_voice_urls
        }
        
        try:
            await dynamodb_service.update_user_profile_in_friends(user_id, profile_data)
        except Exception as e:
            logger.error(f"Failed to sync profile to DynamoDB: {str(e)}")
            # DynamoDB 동기화 실패해도 RDS 업데이트는 성공으로 처리
        
        return db_user
    
    async def delete_user(self, user_id: str) -> bool:
        """사용자 삭제"""
        db_user = self.db.query(User).filter(User.user_id == user_id).first()
        if not db_user:
            return False
        
        self.db.delete(db_user)
        self.db.commit()
        return True
    
    async def search_users_by_email(self, email_query: str, limit: int = 10) -> List[User]:
        """이메일로 사용자 검색"""
        return self.db.query(User).filter(
            User.email.ilike(f"%{email_query}%")
        ).limit(limit).all()
    
    async def get_user_by_friend_code(self, friend_code: str) -> Optional[User]:
        """친구 코드로 사용자 조회"""
        return self.db.query(User).filter(User.friend_code == friend_code).first()
    
    async def send_friend_request(self, user_id: str, friend_code: str) -> dict:
        """친구 코드로 친구 요청 보내기 (pending 상태)"""
        from app.services.dynamodb_service import dynamodb_service
        from app.schemas.user import CatProfile
        import time
        
        # 현재 사용자 확인
        current_user = self.db.query(User).filter(User.user_id == user_id).first()
        if not current_user:
            raise ValueError("Current user not found")
        
        # 친구 코드로 대상 사용자 찾기
        target_user = await self.get_user_by_friend_code(friend_code)
        if not target_user:
            raise ValueError("User not found with this friend code")
        
        # 자기 자신에게 친구 요청 방지
        if current_user.user_id == target_user.user_id:
            raise ValueError("Cannot send friend request to yourself")
        
        # 기존 관계 확인 (중복 요청 방지)
        existing_relation = await dynamodb_service.get_friend_relation(user_id, target_user.user_id)
        if existing_relation:
            status = existing_relation.get('status')
            if status == 'sending':
                raise ValueError("Friend request already sent")
            elif status == 'pending':
                raise ValueError("You have a pending request from this user. Please accept it instead.")
            elif status == 'accepted':
                raise ValueError("Already friends with this user")
        
        # 현재 사용자 프로필 정보
        import json
        current_train_voice_urls = json.loads(current_user.train_voice_urls) if current_user.train_voice_urls else []
        friend_train_voice_urls = json.loads(target_user.train_voice_urls) if target_user.train_voice_urls else []
        
        current_profile = {
            'email': current_user.email,
            'nickname': current_user.nickname,
            'profile_image_url': current_user.profile_image_url,
            'cat_pattern': current_user.cat_pattern,
            'cat_color': current_user.cat_color,
            'meow_audio_url': current_user.meow_audio_url,
            'train_voice_urls': current_train_voice_urls,
            'daily_status': ''
        }
        
        # 친구 프로필 정보
        friend_profile = {
            'email': target_user.email,
            'nickname': target_user.nickname,
            'profile_image_url': target_user.profile_image_url,
            'cat_pattern': target_user.cat_pattern,
            'cat_color': target_user.cat_color,
            'meow_audio_url': target_user.meow_audio_url,
            'train_voice_urls': friend_train_voice_urls,
            'daily_status': ''
        }
        
        # DynamoDB에 친구 요청 전송 (pending 상태)
        success = await dynamodb_service.send_friend_request(
            current_user.user_id, 
            target_user.user_id,
            current_profile,
            friend_profile
        )
        if not success:
            raise ValueError("Failed to send friend request")
        
        # 응답 데이터 구성
        cat_image_url = f"/api/v1/cats/generate/{target_user.user_id}"
        return {
            "user_id": target_user.user_id,
            "nickname": target_user.nickname,
            "friend_code": target_user.friend_code,
            "cat_profile": {
                "pattern": target_user.cat_pattern,
                "color": target_user.cat_color,
                "image_url": cat_image_url
            },
            "status": "sending"
        }
    
    async def accept_friend_request(self, user_id: str, friend_user_id: str) -> bool:
        """친구 요청 수락 (pending → accepted) + FCM 푸시 알림"""
        from app.services.dynamodb_service import dynamodb_service
        from app.services.fcm_service import fcm_service
        
        # 사용자 존재 확인
        user = self.db.query(User).filter(User.user_id == user_id).first()
        friend_user = self.db.query(User).filter(User.user_id == friend_user_id).first()
        
        if not user or not friend_user:
            raise ValueError("User not found")
        
        # 현재 관계 상태 확인
        relation = await dynamodb_service.get_friend_relation(user_id, friend_user_id)
        if not relation:
            raise ValueError("No friend request found")
        
        status = relation.get('status')
        if status != 'pending':
            if status == 'accepted':
                raise ValueError("Already friends with this user")
            elif status == 'sending':
                raise ValueError("Cannot accept your own friend request")
            else:
                raise ValueError(f"Invalid request status: {status}")
        
        # DynamoDB에서 친구 요청 수락
        success = await dynamodb_service.accept_friend_request(user_id, friend_user_id)
        if success:
            logger.info(f"✅ Friend request accepted: {user_id} <-> {friend_user_id}")
            
            # FCM 푸시 알림 전송 (요청 보낸 사람에게)
            if friend_user.token:
                try:
                    await fcm_service.send_friend_accepted_notification(
                        token=friend_user.token,
                        accepter_nickname=user.nickname,
                        accepter_user_id=user.user_id
                    )
                    logger.info(f"✅ FCM notification sent to {friend_user_id}")
                except Exception as e:
                    logger.error(f"❌ Failed to send FCM notification: {e}")
            else:
                logger.warning(f"⚠️ No FCM token for user {friend_user_id}")
        
        return success
    
    async def reject_friend_request(self, user_id: str, friend_user_id: str) -> bool:
        """친구 요청 거절 (레코드 삭제)"""
        from app.services.dynamodb_service import dynamodb_service
        
        # 사용자 존재 확인
        user = self.db.query(User).filter(User.user_id == user_id).first()
        friend_user = self.db.query(User).filter(User.user_id == friend_user_id).first()
        
        if not user or not friend_user:
            raise ValueError("User not found")
        
        # 현재 관계 상태 확인
        relation = await dynamodb_service.get_friend_relation(user_id, friend_user_id)
        if not relation:
            raise ValueError("No friend request found")
        
        status = relation.get('status')
        if status != 'pending':
            if status == 'sending':
                raise ValueError("Cannot reject your own friend request. Use cancel instead.")
            elif status == 'accepted':
                raise ValueError("Cannot reject accepted friend. Use remove friend instead.")
            else:
                raise ValueError(f"Invalid request status: {status}")
        
        # DynamoDB에서 친구 요청 거절
        success = await dynamodb_service.reject_friend_request(user_id, friend_user_id)
        if success:
            logger.info(f"Friend request rejected: {user_id} X {friend_user_id}")
        return success
    
    async def cancel_friend_request(self, user_id: str, friend_user_id: str) -> bool:
        """친구 요청 취소 (보낸 요청 취소)"""
        from app.services.dynamodb_service import dynamodb_service
        
        # 사용자 존재 확인
        user = self.db.query(User).filter(User.user_id == user_id).first()
        friend_user = self.db.query(User).filter(User.user_id == friend_user_id).first()
        
        if not user or not friend_user:
            raise ValueError("User not found")
        
        # 현재 관계 상태 확인
        relation = await dynamodb_service.get_friend_relation(user_id, friend_user_id)
        if not relation:
            raise ValueError("No friend request found")
        
        status = relation.get('status')
        if status != 'sending':
            if status == 'pending':
                raise ValueError("Cannot cancel received request. Use reject instead.")
            elif status == 'accepted':
                raise ValueError("Cannot cancel accepted friend. Use remove friend instead.")
            else:
                raise ValueError(f"Invalid request status: {status}")
        
        # DynamoDB에서 친구 요청 취소
        success = await dynamodb_service.cancel_friend_request(user_id, friend_user_id)
        if success:
            logger.info(f"Friend request cancelled: {user_id} -> {friend_user_id}")
        return success
    
    async def remove_friend(self, user_id: str, friend_user_id: str) -> bool:
        """친구 삭제"""
        from app.services.dynamodb_service import dynamodb_service
        
        # 사용자 존재 확인
        user = self.db.query(User).filter(User.user_id == user_id).first()
        friend_user = self.db.query(User).filter(User.user_id == friend_user_id).first()
        
        if not user or not friend_user:
            raise ValueError("User not found")
        
        # DynamoDB에서 친구 관계 삭제
        success = await dynamodb_service.remove_friend(user_id, friend_user_id)
        return success
    
    async def get_pending_requests(self, user_id: str) -> List[dict]:
        """받은 친구 요청 목록 조회 (pending)"""
        from app.services.dynamodb_service import dynamodb_service
        
        pending_data = await dynamodb_service.get_pending_requests(user_id)
        
        pending_list = []
        for data in pending_data:
            pending_user = {
                'user_id': data.get('friend_user_id'),
                'nickname': data.get('nickname', ''),
                'profile_image_url': data.get('profile_image_url'),
                'cat_pattern': data.get('cat_pattern'),
                'cat_color': data.get('cat_color'),
                'created_at': data.get('created_at', 0)
            }
            pending_list.append(pending_user)
        
        return pending_list
    
    async def get_sending_requests(self, user_id: str) -> List[dict]:
        """보낸 친구 요청 목록 조회 (sending)"""
        from app.services.dynamodb_service import dynamodb_service
        
        sending_data = await dynamodb_service.get_sending_requests(user_id)
        
        sending_list = []
        for data in sending_data:
            sending_user = {
                'user_id': data.get('friend_user_id'),
                'nickname': data.get('nickname', ''),
                'profile_image_url': data.get('profile_image_url'),
                'cat_pattern': data.get('cat_pattern'),
                'cat_color': data.get('cat_color'),
                'created_at': data.get('created_at', 0)
            }
            sending_list.append(sending_user)
        
        return sending_list
    
    async def get_accepted_friends(self, user_id: str) -> List[dict]:
        """수락된 친구 목록 조회 (accepted)"""
        from app.services.dynamodb_service import dynamodb_service
        
        friends_data = await dynamodb_service.get_accepted_friends(user_id)
        
        friends_list = []
        for data in friends_data:
            friend = {
                'user_id': data.get('friend_user_id'),
                'nickname': data.get('nickname', ''),
                'profile_image_url': data.get('profile_image_url'),
                'cat_pattern': data.get('cat_pattern'),
                'cat_color': data.get('cat_color'),
                'meow_audio_url': data.get('meow_audio_url'),
                'train_voice_urls': data.get('train_voice_urls', []),
                'daily_status': data.get('daily_status', ''),
                'created_at': data.get('created_at', 0)
            }
            friends_list.append(friend)
        
        return friends_list
    
    async def update_fcm_token(self, user_id: str, token: str) -> Optional[User]:
        """FCM 토큰 업데이트"""
        user = self.db.query(User).filter(User.user_id == user_id).first()
        if not user:
            return None
        
        user.token = token
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    async def get_fcm_token(self, user_id: str) -> Optional[str]:
        """FCM 토큰 조회"""
        user = self.db.query(User).filter(User.user_id == user_id).first()
        if not user:
            return None
        
        return user.token