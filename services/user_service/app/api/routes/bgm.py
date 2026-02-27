"""
BGM API 라우트
SageMaker에서 생성한 BGM을 DynamoDB에 저장
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.services.dynamodb_service import dynamodb_service
from app.schemas.response import success_response, error_response
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class BGMUpdateRequest(BaseModel):
    """BGM 업데이트 요청"""
    user_id: str
    bgm_url: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "c478cd4c-5071-7060-2991-cc9b3bb59dff",
                "bgm_url": "https://ameowzon-test-files.s3.ap-northeast-2.amazonaws.com/bgm/user123_bgm.mp3"
            }
        }


@router.post("/update", response_model=dict, status_code=status.HTTP_200_OK)
async def update_user_bgm(request: BGMUpdateRequest):
    """
    사용자 BGM URL 업데이트
    
    SageMaker에서 BGM을 생성하고 S3에 저장한 후, 이 API를 호출하여 DynamoDB에 저장합니다.
    
    Request Body:
    - user_id: 사용자 ID (필수)
    - bgm_url: S3에 저장된 BGM 파일의 전체 URL (필수)
    
    Returns:
    - success: 성공 여부
    - message: 결과 메시지
    - data: 업데이트된 정보
    
    Example:
    ```json
    {
        "user_id": "c478cd4c-5071-7060-2991-cc9b3bb59dff",
        "bgm_url": "https://ameowzon-test-files.s3.ap-northeast-2.amazonaws.com/bgm/user123_bgm.mp3"
    }
    ```
    
    DynamoDB 저장 위치:
    - 테이블: user_friends
    - 레코드: friend_user_id = user_id인 모든 레코드 (Self-friend + 모든 친구들의 레코드)
    - 컬럼: bgm_url
    """
    logger.info(f"🎵 BGM UPDATE REQUEST: user_id={request.user_id}")
    logger.info(f"📀 BGM URL: {request.bgm_url}")
    
    try:
        # DynamoDB에 BGM URL 저장
        success = await dynamodb_service.update_bgm_url(request.user_id, request.bgm_url)
        
        if not success:
            logger.error(f"❌ Failed to update BGM URL for user: {request.user_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_response(
                    message="Failed to update BGM URL. No records found with this user as friend.",
                    error_code="BGM_UPDATE_FAILED"
                )
            )
        
        logger.info(f"✅ BGM URL updated successfully: user_id={request.user_id}")
        
        return success_response(
            data={
                "user_id": request.user_id,
                "bgm_url": request.bgm_url
            },
            message="BGM URL updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ BGM UPDATE ERROR: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response(
                message="Internal server error while updating BGM URL",
                error_code="INTERNAL_ERROR"
            )
        )


@router.get("/{user_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def get_user_bgm(user_id: str):
    """
    사용자 BGM URL 조회
    
    Parameters:
    - user_id: 사용자 ID
    
    Returns:
    - user_id: 사용자 ID
    - bgm_url: BGM URL (없으면 null)
    """
    logger.info(f"🎵 BGM GET REQUEST: user_id={user_id}")
    
    try:
        # Self-friend 레코드에서 BGM URL 조회
        from boto3.dynamodb.conditions import Key
        
        if not dynamodb_service.friends_table:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_response(
                    message="DynamoDB service not available",
                    error_code="SERVICE_UNAVAILABLE"
                )
            )
        
        response = dynamodb_service.friends_table.query(
            KeyConditionExpression=Key('user_id').eq(user_id) & Key('friend_user_id').eq(user_id)
        )
        
        items = response.get('Items', [])
        if not items:
            logger.warning(f"⚠️ Self-friend record not found for user: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_response(
                    message="User not found",
                    error_code="USER_NOT_FOUND"
                )
            )
        
        bgm_url = items[0].get('bgm_url')
        logger.info(f"✅ BGM URL retrieved: user_id={user_id}, bgm_url={bgm_url}")
        
        return success_response(
            data={
                "user_id": user_id,
                "bgm_url": bgm_url
            },
            message="BGM URL retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ BGM GET ERROR: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response(
                message="Internal server error while retrieving BGM URL",
                error_code="INTERNAL_ERROR"
            )
        )
