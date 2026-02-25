"""
고양이 AI 이미지 생성 API
Nanobanana를 통한 사용자 맞춤 고양이 이미지 생성
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.services.nanobanana_service import nanobanana_service
from app.services.s3_service import s3_service
from app.services.user_service import UserService
from app.schemas.response import success_response, error_response
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/generate/{user_id}", response_model=dict)
async def generate_cat_image(
    user_id: str,
    image: UploadFile = File(...),
    cat_pattern: Optional[str] = Form(None),
    cat_color: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    사용자 사진으로 AI 고양이 이미지 생성
    
    Parameters:
    - user_id: 사용자 ID
    - image: 원본 사진 파일
    - cat_pattern: 고양이 패턴 (선택, 없으면 사용자 프로필에서 가져옴)
    - cat_color: 고양이 색상 (선택, 없으면 사용자 프로필에서 가져옴)
    
    Returns:
    - original_url: 원본 이미지 URL (S3)
    - generated_url: AI 생성 이미지 URL
    - cat_pattern: 사용된 패턴
    - cat_color: 사용된 색상
    
    Process:
    1. 원본 이미지를 S3에 업로드
    2. S3 URL을 Nanobanana API에 전달
    3. AI 생성 이미지 URL 반환
    """
    try:
        logger.info(f"🎨 Cat image generation request for user: {user_id}")
        
        # 사용자 정보 조회
        user_service = UserService(db)
        user = await user_service.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=404,
                detail=error_response(
                    message="User not found",
                    error_code="USER_NOT_FOUND"
                )
            )
        
        # 패턴/색상이 없으면 사용자 프로필에서 가져오기
        final_pattern = cat_pattern or user.cat_pattern
        final_color = cat_color or user.cat_color
        
        if not final_pattern or not final_color:
            raise HTTPException(
                status_code=400,
                detail=error_response(
                    message="Cat pattern and color are required",
                    error_code="MISSING_CAT_INFO"
                )
            )
        
        logger.info(f"   Using pattern: {final_pattern}, color: {final_color}")
        
        # 1. 원본 이미지를 S3에 업로드
        logger.info("📤 Uploading original image to S3...")
        original_url = await s3_service.upload_profile_image(image, user_id)
        logger.info(f"✅ Original image uploaded: {original_url}")
        
        # 2. Nanobanana API로 AI 이미지 생성
        logger.info("🤖 Calling Nanobanana API...")
        generated_url = await nanobanana_service.generate_cat_image(
            source_image_url=original_url,
            cat_pattern=final_pattern,
            cat_color=final_color,
            user_id=user_id
        )
        
        if not generated_url:
            raise HTTPException(
                status_code=500,
                detail=error_response(
                    message="Failed to generate cat image",
                    error_code="GENERATION_FAILED"
                )
            )
        
        logger.info(f"✅ Cat image generated successfully")
        
        return success_response(
            data={
                "user_id": user_id,
                "original_url": original_url,
                "generated_url": generated_url,
                "cat_pattern": final_pattern,
                "cat_color": final_color
            },
            message="Cat image generated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to generate cat image: {e}")
        raise HTTPException(
            status_code=500,
            detail=error_response(
                message="Internal server error",
                error_code="INTERNAL_ERROR"
            )
        )


@router.post("/generate-from-url/{user_id}", response_model=dict)
async def generate_cat_image_from_url(
    user_id: str,
    image_url: str = Form(...),
    cat_pattern: Optional[str] = Form(None),
    cat_color: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    이미 업로드된 이미지 URL로 AI 고양이 이미지 생성
    
    Parameters:
    - user_id: 사용자 ID
    - image_url: 원본 이미지 URL (S3)
    - cat_pattern: 고양이 패턴 (선택)
    - cat_color: 고양이 색상 (선택)
    
    Returns:
    - original_url: 원본 이미지 URL
    - generated_url: AI 생성 이미지 URL
    """
    try:
        logger.info(f"🎨 Cat image generation from URL for user: {user_id}")
        
        # 사용자 정보 조회
        user_service = UserService(db)
        user = await user_service.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=404,
                detail=error_response(
                    message="User not found",
                    error_code="USER_NOT_FOUND"
                )
            )
        
        # 패턴/색상 결정
        final_pattern = cat_pattern or user.cat_pattern
        final_color = cat_color or user.cat_color
        
        if not final_pattern or not final_color:
            raise HTTPException(
                status_code=400,
                detail=error_response(
                    message="Cat pattern and color are required",
                    error_code="MISSING_CAT_INFO"
                )
            )
        
        # Nanobanana API로 AI 이미지 생성
        logger.info("🤖 Calling Nanobanana API...")
        generated_url = await nanobanana_service.generate_cat_image(
            source_image_url=image_url,
            cat_pattern=final_pattern,
            cat_color=final_color,
            user_id=user_id
        )
        
        if not generated_url:
            raise HTTPException(
                status_code=500,
                detail=error_response(
                    message="Failed to generate cat image",
                    error_code="GENERATION_FAILED"
                )
            )
        
        logger.info(f"✅ Cat image generated successfully")
        
        return success_response(
            data={
                "user_id": user_id,
                "original_url": image_url,
                "generated_url": generated_url,
                "cat_pattern": final_pattern,
                "cat_color": final_color
            },
            message="Cat image generated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to generate cat image: {e}")
        raise HTTPException(
            status_code=500,
            detail=error_response(
                message="Internal server error",
                error_code="INTERNAL_ERROR"
            )
        )


@router.get("/status/{job_id}", response_model=dict)
async def check_generation_status(job_id: str):
    """
    AI 이미지 생성 작업 상태 확인 (비동기 생성 시)
    
    Parameters:
    - job_id: 생성 작업 ID
    
    Returns:
    - status: 작업 상태 (pending, processing, completed, failed)
    - image_url: 생성된 이미지 URL (완료 시)
    """
    try:
        result = await nanobanana_service.check_generation_status(job_id)
        
        return success_response(
            data=result,
            message="Status retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to check status: {e}")
        raise HTTPException(
            status_code=500,
            detail=error_response(
                message="Failed to check generation status",
                error_code="STATUS_CHECK_FAILED"
            )
        )
