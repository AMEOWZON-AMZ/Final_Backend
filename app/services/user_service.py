from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import Optional, Dict, Any, List
from datetime import datetime
from loguru import logger

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserListResponse, SocialUserInfo, SocialProvider
from app.core.database import get_db


class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """ID로 사용자 조회"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    async def get_user_by_social_id(self, social_provider: SocialProvider, social_id: str) -> Optional[User]:
        """소셜 ID로 사용자 조회"""
        return self.db.query(User).filter(
            User.social_provider == social_provider,
            User.social_id == social_id
        ).first()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """이메일로 사용자 조회"""
        return self.db.query(User).filter(User.email == email).first()
    
    async def create_user(self, user_data: UserCreate) -> User:
        """새 사용자 생성"""
        try:
            db_user = User(
                social_provider=user_data.social_provider,
                social_id=user_data.social_id,
                email=user_data.email,
                username=user_data.username,
                full_name=user_data.full_name,
                nickname=user_data.nickname,
                bio=user_data.bio,
                phone_number=user_data.phone_number,
                is_active=True,
                is_verified=False
            )
            
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            
            logger.info(f"User created: {db_user.email} via {db_user.social_provider.value}")
            return db_user
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"User creation failed: {e}")
            raise
    
    async def update_user_by_social_id(
        self, 
        social_provider: SocialProvider, 
        social_id: str, 
        user_update: UserUpdate
    ) -> Optional[User]:
        """소셜 ID로 사용자 정보 업데이트"""
        try:
            db_user = await self.get_user_by_social_id(social_provider, social_id)
            if not db_user:
                return None
            
            update_data = user_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_user, field, value)
            
            db_user.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(db_user)
            
            logger.info(f"User updated: {db_user.email}")
            return db_user
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"User update failed: {e}")
            raise
    
    async def delete_user_by_social_id(
        self, 
        social_provider: SocialProvider, 
        social_id: str
    ) -> bool:
        """소셜 ID로 사용자 삭제 (비활성화)"""
        try:
            db_user = await self.get_user_by_social_id(social_provider, social_id)
            if not db_user:
                return False
            
            db_user.is_active = False
            db_user.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"User deactivated: {db_user.email}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"User deletion failed: {e}")
            raise
    
    async def get_or_create_user_from_social(self, social_user_info: SocialUserInfo) -> User:
        """소셜 로그인 정보로부터 사용자 조회 또는 생성"""
        try:
            # 기존 사용자 조회
            existing_user = await self.get_user_by_social_id(
                social_user_info.provider, 
                social_user_info.social_id
            )
            
            if existing_user:
                # 마지막 로그인 시간 업데이트
                existing_user.last_login_at = datetime.utcnow()
                
                # 프로필 정보 업데이트 (소셜에서 변경된 경우)
                if social_user_info.name and not existing_user.full_name:
                    existing_user.full_name = social_user_info.name
                if social_user_info.nickname and not existing_user.nickname:
                    existing_user.nickname = social_user_info.nickname
                if social_user_info.profile_image and not existing_user.profile_image_url:
                    existing_user.profile_image_url = social_user_info.profile_image
                
                self.db.commit()
                return existing_user
            
            # 새 사용자 생성
            user_create = UserCreate(
                social_provider=social_user_info.provider,
                social_id=social_user_info.social_id,
                email=social_user_info.email,
                full_name=social_user_info.name,
                nickname=social_user_info.nickname
            )
            
            new_user = await self.create_user(user_create)
            
            # 프로필 이미지 설정
            if social_user_info.profile_image:
                new_user.profile_image_url = social_user_info.profile_image
            
            new_user.last_login_at = datetime.utcnow()
            self.db.commit()
            
            return new_user
            
        except Exception as e:
            logger.error(f"Get or create user from social failed: {e}")
            raise
    
    async def search_users(
        self, 
        query: str, 
        page: int = 1, 
        limit: int = 10,
        exclude_user_id: Optional[int] = None
    ) -> UserListResponse:
        """사용자 검색"""
        try:
            offset = (page - 1) * limit
            
            # 검색 쿼리 구성
            search_filter = or_(
                User.username.ilike(f"%{query}%"),
                User.full_name.ilike(f"%{query}%"),
                User.nickname.ilike(f"%{query}%"),
                User.email.ilike(f"%{query}%")
            )
            
            base_query = self.db.query(User).filter(
                and_(
                    User.is_active == True,
                    search_filter
                )
            )
            
            # 현재 사용자 제외
            if exclude_user_id:
                base_query = base_query.filter(User.id != exclude_user_id)
            
            # 총 개수 조회
            total = base_query.count()
            
            # 페이징된 결과 조회
            users = base_query.offset(offset).limit(limit).all()
            
            return UserListResponse(
                users=[UserResponse.from_orm(user) for user in users],
                total=total,
                page=page,
                limit=limit,
                has_next=(offset + limit) < total
            )
            
        except Exception as e:
            logger.error(f"User search failed: {e}")
            raise
    
    async def get_users_by_social_ids(self, social_ids: List[str]) -> List[User]:
        """여러 소셜 ID로 사용자들 조회"""
        return self.db.query(User).filter(
            User.social_id.in_(social_ids),
            User.is_active == True
        ).all()