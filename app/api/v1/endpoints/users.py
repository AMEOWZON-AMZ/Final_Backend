from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from loguru import logger

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.schemas.user import (
    UserResponse, UserUpdate, UserListResponse,
    FriendCreate, FriendResponse, FriendListResponse, SocialProvider
)
from app.schemas.response import success_response, error_response, paginated_response
from app.services.user_service import UserService
from app.services.friend_service import FriendService

router = APIRouter()


@router.get("/me")
async def get_my_profile(
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """내 프로필 정보 조회"""
    try:
        user_service = UserService(db)
        user = await user_service.get_user_by_id(int(current_user["user_id"]))
        
        if not user:
            return error_response(
                message="User not found",
                error_code="USER_NOT_FOUND"
            )
        
        return success_response(
            data={
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "nickname": user.nickname,
                "profile_image_url": user.profile_image_url,
                "bio": user.bio,
                "phone_number": user.phone_number,
                "provider": user.social_provider.value,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None,
                "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None
            },
            message="Profile retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Get my profile failed: {e}")
        return error_response(
            message="Failed to retrieve profile",
            error_code="PROFILE_FETCH_ERROR",
            details={"error": str(e)}
        )


@router.put("/me")
async def update_my_profile(
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """내 프로필 정보 수정"""
    try:
        user_service = UserService(db)
        
        # 현재 사용자 조회
        user = await user_service.get_user_by_id(int(current_user["user_id"]))
        if not user:
            return error_response(
                message="User not found",
                error_code="USER_NOT_FOUND"
            )
        
        # 프로필 업데이트
        updated_user = await user_service.update_user_by_social_id(
            user.social_provider,
            user.social_id,
            user_update
        )
        
        if not updated_user:
            return error_response(
                message="Failed to update profile",
                error_code="PROFILE_UPDATE_ERROR"
            )
        
        logger.info(f"User profile updated: {current_user['user_id']}")
        
        return success_response(
            data={
                "id": updated_user.id,
                "email": updated_user.email,
                "username": updated_user.username,
                "full_name": updated_user.full_name,
                "nickname": updated_user.nickname,
                "profile_image_url": updated_user.profile_image_url,
                "bio": updated_user.bio,
                "phone_number": updated_user.phone_number,
                "provider": updated_user.social_provider.value,
                "updated_at": updated_user.updated_at.isoformat() if updated_user.updated_at else None
            },
            message="Profile updated successfully"
        )
        
    except Exception as e:
        logger.error(f"Update profile failed: {e}")
        return error_response(
            message="Failed to update profile",
            error_code="PROFILE_UPDATE_ERROR",
            details={"error": str(e)}
        )


@router.get("/search")
async def search_users(
    q: str = Query(..., min_length=2, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=50, description="Items per page"),
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """사용자 검색"""
    try:
        user_service = UserService(db)
        result = await user_service.search_users(
            query=q,
            page=page,
            limit=limit,
            exclude_user_id=int(current_user["user_id"])
        )
        
        # 사용자 데이터 변환
        users_data = []
        for user in result.users:
            users_data.append({
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "nickname": user.nickname,
                "profile_image_url": user.profile_image_url,
                "provider": user.social_provider.value
            })
        
        return paginated_response(
            data=users_data,
            page=page,
            limit=limit,
            total=result.total,
            message="Users found successfully"
        )
        
    except Exception as e:
        logger.error(f"User search failed: {e}")
        return error_response(
            message="Failed to search users",
            error_code="USER_SEARCH_ERROR",
            details={"error": str(e)}
        )


@router.get("/{user_id}")
async def get_user_profile(
    user_id: int,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """다른 사용자 프로필 조회"""
    try:
        user_service = UserService(db)
        user = await user_service.get_user_by_id(user_id)
        
        if not user:
            return error_response(
                message="User not found",
                error_code="USER_NOT_FOUND"
            )
        
        return success_response(
            data={
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "nickname": user.nickname,
                "profile_image_url": user.profile_image_url,
                "bio": user.bio,
                "provider": user.social_provider.value,
                "created_at": user.created_at.isoformat() if user.created_at else None
            },
            message="User profile retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Get user profile failed: {e}")
        return error_response(
            message="Failed to retrieve user profile",
            error_code="PROFILE_FETCH_ERROR",
            details={"error": str(e)}
        )


# Friends endpoints
@router.get("/me/friends")
async def get_my_friends(
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """내 친구 목록 조회"""
    try:
        friend_service = FriendService(db)
        friends = await friend_service.get_user_friends(current_user["user_id"])
        
        friends_data = []
        for friend in friends:
            friends_data.append({
                "user_id": friend.user_id,
                "friend_id": friend.friend_id,
                "friend_name": friend.friend_name,
                "friend_email": friend.friend_email,
                "friend_profile_image": friend.friend_profile_image,
                "created_at": friend.created_at.isoformat() if friend.created_at else None,
                "status": friend.status
            })
        
        return success_response(
            data={
                "friends": friends_data,
                "total": len(friends_data)
            },
            message="Friends retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Get friends failed: {e}")
        return error_response(
            message="Failed to retrieve friends",
            error_code="FRIENDS_FETCH_ERROR",
            details={"error": str(e)}
        )


@router.post("/me/friends")
async def add_friend(
    friend_data: FriendCreate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """친구 추가"""
    try:
        if friend_data.friend_id == current_user["user_id"]:
            return error_response(
                message="Cannot add yourself as friend",
                error_code="INVALID_FRIEND_REQUEST"
            )
        
        friend_service = FriendService(db)
        result = await friend_service.add_friend(
            current_user["user_id"], 
            friend_data.friend_id
        )
        
        logger.info(f"Friend added: {current_user['user_id']} -> {friend_data.friend_id}")
        
        return success_response(
            data=result,
            message="Friend added successfully"
        )
        
    except ValueError as e:
        return error_response(
            message=str(e),
            error_code="FRIEND_ADD_ERROR"
        )
    except Exception as e:
        logger.error(f"Add friend failed: {e}")
        return error_response(
            message="Failed to add friend",
            error_code="FRIEND_ADD_ERROR",
            details={"error": str(e)}
        )


@router.delete("/me/friends/{friend_id}")
async def remove_friend(
    friend_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """친구 삭제"""
    try:
        friend_service = FriendService(db)
        result = await friend_service.remove_friend(
            current_user["user_id"], 
            friend_id
        )
        
        logger.info(f"Friend removed: {current_user['user_id']} -> {friend_id}")
        
        return success_response(
            data=result,
            message="Friend removed successfully"
        )
        
    except ValueError as e:
        return error_response(
            message=str(e),
            error_code="FRIEND_REMOVE_ERROR"
        )
    except Exception as e:
        logger.error(f"Remove friend failed: {e}")
        return error_response(
            message="Failed to remove friend",
            error_code="FRIEND_REMOVE_ERROR",
            details={"error": str(e)}
        )