"""
빠른 등록 서비스 (QR 코드용)
사용자 생성 + 친구 등록 + 음성 파일 업로드를 한 번에 처리
"""
from sqlalchemy.orm import Session
from typing import Dict, Optional
from fastapi import UploadFile
import uuid
import random
import string
from datetime import datetime
from app.models.user import User
from loguru import logger


class QuickRegisterService:
    """빠른 등록 서비스"""
    
    @staticmethod
    def generate_user_id() -> str:
        """UUID 기반 사용자 ID 생성"""
        return str(uuid.uuid4())
    
    @staticmethod
    def generate_friend_code() -> str:
        """6자리 친구 코드 생성 (영문 대문자 + 숫자)"""
        characters = string.ascii_uppercase + string.digits
        while True:
            code = ''.join(random.choices(characters, k=6))
            # 숫자만 있거나 문자만 있는 경우 제외
            if any(c.isdigit() for c in code) and any(c.isalpha() for c in code):
                return code
    
    @staticmethod
    async def create_user_and_add_friend(
        db: Session,
        nickname: str,
        target_user_id: str,
        phone_number: str = None,
        cat_pattern: str = "solid",
        cat_color: str = "#FF6B6B",
        meow_audio: Optional[UploadFile] = None,
        train_voice: Optional[list[UploadFile]] = None
    ) -> Dict:
        """
        사용자 생성 + 친구 등록 + 음성 파일 업로드 (한 번에 처리)
        
        Args:
            db: 데이터베이스 세션
            nickname: 새 사용자 닉네임
            target_user_id: 친구로 등록할 대상 사용자 ID
            phone_number: 전화번호 (선택)
            cat_pattern: 고양이 무늬
            cat_color: 고양이 색상
            meow_audio: 야옹 소리 파일 (선택)
            train_voice: 암구호 학습용 음성 파일 3개 (선택)
        
        Returns:
            {
                'user_id': str,
                'nickname': str,
                'friend_code': str,
                'friend_added': bool,
                'target_nickname': str,
                'meow_audio_url': str (optional),
                'train_voice_urls': list[str] (optional)
            }
        """
        try:
            # 1. 대상 사용자 존재 확인
            target_user = db.query(User).filter(User.user_id == target_user_id).first()
            if not target_user:
                raise ValueError(f"Target user not found: {target_user_id}")
            
            # 2. 새 사용자 생성
            new_user_id = QuickRegisterService.generate_user_id()
            friend_code = QuickRegisterService.generate_friend_code()
            
            # 친구 코드 중복 체크
            while db.query(User).filter(User.friend_code == friend_code).first():
                friend_code = QuickRegisterService.generate_friend_code()
            
            timestamp = int(datetime.now().timestamp() * 1000)
            
            new_user = User(
                user_id=new_user_id,
                email=f"quick_{new_user_id[:8]}@demo.com",  # 임시 이메일
                nickname=nickname,
                phone_number=phone_number,
                friend_code=friend_code,
                cat_pattern=cat_pattern,
                cat_color=cat_color,
                provider="demo",  # 데모 계정 표시
                profile_setup_completed=True,
                created_at_timestamp=timestamp,
                updated_at_timestamp=timestamp
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            logger.info(f"✅ Quick register: Created user {new_user_id} ({nickname})")
            
            # 3. 음성 파일 업로드 (S3)
            meow_audio_url = None
            train_voice_urls = []
            
            if meow_audio or train_voice:
                from app.services.s3_service import s3_service
                
                if meow_audio:
                    try:
                        meow_audio_url = await s3_service.upload_meow_audio(meow_audio, new_user_id)
                        new_user.meow_audio_url = meow_audio_url
                        logger.info(f"✅ Meow audio uploaded: {meow_audio_url}")
                    except Exception as e:
                        logger.error(f"❌ Failed to upload meow audio: {e}")
                
                if train_voice:
                    # 3개의 암구호 파일 업로드
                    for idx, voice_file in enumerate(train_voice[:3], 1):  # 최대 3개만
                        try:
                            voice_url = await s3_service.upload_train_voice(voice_file, new_user_id, idx)
                            train_voice_urls.append(voice_url)
                            logger.info(f"✅ Train voice {idx} uploaded: {voice_url}")
                        except Exception as e:
                            logger.error(f"❌ Failed to upload train voice {idx}: {e}")
                    
                    # JSON 배열로 저장
                    if train_voice_urls:
                        import json
                        new_user.train_voice_urls = json.dumps(train_voice_urls)
                
                # 음성 파일 URL 저장
                db.commit()
                db.refresh(new_user)
            
            # 4. 양방향 친구 관계 추가 (DynamoDB)
            friend_added = False
            try:
                import boto3
                from app.core.config import settings
                
                logger.info(f"🔗 Attempting to add friend relationship to DynamoDB...")
                
                dynamodb = boto3.resource('dynamodb', region_name=settings.AWS_REGION)
                friends_table = dynamodb.Table('user_friends')
                
                current_timestamp = int(datetime.now().timestamp() * 1000)
                
                # daily_status 랜덤 선택
                daily_status_options = ['STABLE', 'SLEEP', 'LETHARGY', 'CHAOS', 'TRAVEL']
                random_status_1 = random.choice(daily_status_options)
                random_status_2 = random.choice(daily_status_options)
                
                logger.info(f"📝 Adding: {new_user_id} → {target_user_id}")
                logger.info(f"   - nickname: {target_user.nickname}")
                logger.info(f"   - cat_pattern: {target_user.cat_pattern or ''}")
                logger.info(f"   - cat_color: {target_user.cat_color or ''}")
                logger.info(f"   - daily_status: {random_status_1}")
                
                # 새 사용자 → 대상 사용자
                friends_table.put_item(
                    Item={
                        'user_id': new_user_id,
                        'friend_user_id': target_user_id,
                        'nickname': target_user.nickname,
                        'cat_pattern': target_user.cat_pattern or '',
                        'cat_color': target_user.cat_color or '',
                        'status': 'accepted',
                        'daily_status': random_status_1,
                        'created_at': current_timestamp,
                        'updated_at': current_timestamp
                    }
                )
                logger.info(f"✅ Added: {new_user_id} → {target_user_id}")
                
                logger.info(f"📝 Adding: {target_user_id} → {new_user_id}")
                logger.info(f"   - nickname: {nickname}")
                logger.info(f"   - cat_pattern: {cat_pattern or ''}")
                logger.info(f"   - cat_color: {cat_color or ''}")
                logger.info(f"   - daily_status: {random_status_2}")
                
                # 대상 사용자 → 새 사용자
                friends_table.put_item(
                    Item={
                        'user_id': target_user_id,
                        'friend_user_id': new_user_id,
                        'nickname': nickname,
                        'cat_pattern': cat_pattern or '',
                        'cat_color': cat_color or '',
                        'status': 'accepted',
                        'daily_status': random_status_2,
                        'created_at': current_timestamp,
                        'updated_at': current_timestamp
                    }
                )
                logger.info(f"✅ Added: {target_user_id} → {new_user_id}")
                
                friend_added = True
                logger.info(f"✅ Quick register: Added friend relationship {new_user_id} ↔ {target_user_id}")
                
                # 5. OutboxEvents에 친구 수락 이벤트 추가 (Push 알림용)
                try:
                    from app.services.friend_event_service import friend_event_service
                    
                    # 새 사용자에게 알림: "OOO님과 친구가 되었습니다"
                    friend_event_service.enqueue_friend_accepted(
                        to_user_id=new_user_id,
                        from_user_id=target_user_id,
                        from_nickname=target_user.nickname
                    )
                    
                    # 대상 사용자에게 알림: "OOO님과 친구가 되었습니다"
                    friend_event_service.enqueue_friend_accepted(
                        to_user_id=target_user_id,
                        from_user_id=new_user_id,
                        from_nickname=nickname
                    )
                    
                    logger.info(f"✅ Friend accepted events enqueued for both users")
                except Exception as e:
                    logger.error(f"❌ Failed to enqueue friend events: {e}")
                    # 이벤트 추가 실패해도 친구 관계는 이미 추가됨
                
            except Exception as e:
                logger.error(f"❌ Failed to add friend relationship: {e}")
                logger.exception(e)  # 전체 스택 트레이스 출력
                # 친구 추가 실패해도 사용자는 생성됨
            
            return {
                'user_id': new_user_id,
                'nickname': nickname,
                'friend_code': friend_code,
                'friend_added': friend_added,
                'target_nickname': target_user.nickname,
                'meow_audio_url': meow_audio_url,
                'train_voice_urls': train_voice_urls
            }
            
        except ValueError as e:
            logger.error(f"❌ Quick register validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Quick register failed: {e}")
            db.rollback()
            raise


# 전역 인스턴스
quick_register_service = QuickRegisterService()
