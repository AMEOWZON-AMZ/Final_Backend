from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from app.schemas.response import success_response, error_response
from app.schemas.user import FriendRequestData, FriendActionData
from app.services.user_service import UserService

router = APIRouter()




@router.get("/pending/{user_id}", response_model=dict)
async def get_pending_requests(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    받은 친구 요청 목록 조회 (pending)
    
    - user_id는 URL 맨 뒤에 명시
    - 인증 없음
    - 다른 사람이 나한테 보낸 친구 요청 목록
    """
    user_service = UserService(db)
    
    # 사용자 존재 확인
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail=error_response(
                message="User not found",
                error_code="USER_NOT_FOUND"
            )
        )
    
    pending_list = await user_service.get_pending_requests(user_id)
    
    return success_response(
        data={
            "pending_requests": pending_list,
            "total_pending": len(pending_list)
        },
        message="Pending requests retrieved successfully"
    )


@router.get("/sending/{user_id}", response_model=dict)
async def get_sending_requests(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    보낸 친구 요청 목록 조회 (sending)
    
    - user_id는 URL 맨 뒤에 명시
    - 인증 없음
    - 내가 다른 사람한테 보낸 친구 요청 목록 (아직 수락 안 됨)
    """
    user_service = UserService(db)
    
    # 사용자 존재 확인
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail=error_response(
                message="User not found",
                error_code="USER_NOT_FOUND"
            )
        )
    
    sending_list = await user_service.get_sending_requests(user_id)
    
    return success_response(
        data={
            "sending_requests": sending_list,
            "total_sending": len(sending_list)
        },
        message="Sending requests retrieved successfully"
    )


@router.get("/list/{user_id}", response_model=dict)
async def get_friends_list(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    수락된 친구 목록 조회 (accepted)
    
    - user_id는 URL 맨 뒤에 명시
    - 인증 없음
    - 수락된 친구들만 조회
    """
    user_service = UserService(db)
    
    # 사용자 존재 확인
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail=error_response(
                message="User not found",
                error_code="USER_NOT_FOUND"
            )
        )
    
    friends_list = await user_service.get_accepted_friends(user_id)
    
    return success_response(
        data={
            "friends": friends_list,
            "total_friends": len(friends_list)
        },
        message="Friends list retrieved successfully"
    )




@router.post("/request", response_model=dict)
async def send_friend_request(
    request_data: FriendRequestData,
    db: Session = Depends(get_db)
):
    """
    친구 코드로 친구 요청 보내기 (pending 상태)
    
    Request Body:
    - user_id: 요청 보내는 사람 (본인)
    - friend_code: 친구 코드
    
    요청 보내면 상대방은 pending, 본인은 sending 상태
    """
    try:
        user_service = UserService(db)
        friend_response = await user_service.send_friend_request(request_data.user_id, request_data.friend_code)
        return success_response(
            data=friend_response,
            message="Friend request sent successfully"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response(message=str(e), error_code="FRIEND_REQUEST_ERROR")
        )


@router.post("/accept", response_model=dict)
async def accept_friend_request(
    action_data: FriendActionData,
    db: Session = Depends(get_db)
):
    """
    친구 요청 수락 (pending → accepted)
    
    Request Body:
    - user_id: 요청 받은 사람 (수락하는 사람)
    - friend_user_id: 요청 보낸 사람
    """
    try:
        user_service = UserService(db)
        success = await user_service.accept_friend_request(action_data.user_id, action_data.friend_user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_response(message="Failed to accept friend request", error_code="ACCEPT_ERROR")
            )
        return success_response(message="Friend request accepted successfully")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response(message=str(e), error_code="ACCEPT_ERROR")
        )


@router.post("/reject", response_model=dict)
async def reject_friend_request(
    action_data: FriendActionData,
    db: Session = Depends(get_db)
):
    """
    친구 요청 거절 (레코드 삭제)
    
    Request Body:
    - user_id: 요청 받은 사람 (거절하는 사람)
    - friend_user_id: 요청 보낸 사람
    
    거절하면 양쪽 레코드 모두 삭제됨
    """
    try:
        user_service = UserService(db)
        success = await user_service.reject_friend_request(action_data.user_id, action_data.friend_user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_response(message="Failed to reject friend request", error_code="REJECT_ERROR")
            )
        return success_response(message="Friend request rejected successfully")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response(message=str(e), error_code="REJECT_ERROR")
        )


@router.post("/cancel", response_model=dict)
async def cancel_friend_request(
    action_data: FriendActionData,
    db: Session = Depends(get_db)
):
    """
    친구 요청 취소 (보낸 요청 취소)
    
    Request Body:
    - user_id: 요청 보낸 사람 (취소하는 사람)
    - friend_user_id: 요청 받은 사람
    
    취소하면 양쪽 레코드 모두 삭제됨
    """
    try:
        user_service = UserService(db)
        success = await user_service.cancel_friend_request(action_data.user_id, action_data.friend_user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_response(message="Failed to cancel friend request", error_code="CANCEL_ERROR")
            )
        return success_response(message="Friend request cancelled successfully")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response(message=str(e), error_code="CANCEL_ERROR")
        )


@router.delete("/{user_id}/{friend_user_id}", response_model=dict)
async def remove_friend(
    user_id: str,
    friend_user_id: str,
    db: Session = Depends(get_db)
):
    """
    친구 삭제
    
    - user_id는 URL 맨 뒤에서 두 번째
    - friend_user_id는 URL 맨 뒤
    - 인증 없음
    """
    try:
        user_service = UserService(db)
        success = await user_service.remove_friend(user_id, friend_user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_response(message="Failed to remove friend", error_code="FRIEND_REMOVE_ERROR")
            )
        return success_response(message="Friend removed successfully")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_response(message=str(e), error_code="FRIEND_REMOVE_ERROR")
        )

