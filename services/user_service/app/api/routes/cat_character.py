"""
고양이 캐릭터 AI 이미지 생성 API (Gemini 2.5 Flash Image)
사용자 사진을 기반으로 맞춤 고양이 캐릭터 생성
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.gemini_image_service import gemini_image_service
from app.services.s3_service import s3_service
from app.services.user_service import UserService
from app.schemas.response import success_response, error_response
import logging
import base64

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/generate/{user_id}", response_model=dict)
async def generate_cat_character(
    user_id: str,
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    사용자 사진으로 AI 고양이 캐릭터 이미지 생성 (Gemini 2.5 Flash Image)
    
    Parameters:
    - user_id: 사용자 ID
    - image: 원본 사진 파일
    
    Returns:
    - generated_url: 생성된 이미지 URL (S3)
    - generated_image_base64: 생성된 이미지 (base64, 프론트엔드 즉시 표시용)
    
    Process:
    1. 원본 이미지를 읽어서 바이트로 변환
    2. Gemini 2.5 Flash Image API로 고양이 캐릭터 생성
    3. 생성된 이미지를 S3에 업로드
    4. 최종 URL 반환 (원본 이미지는 저장하지 않음)
    """
    try:
        logger.info(f"🎨 Cat character generation request for user: {user_id}")
        
        # 사용자 정보 조회 (선택적 - 없어도 진행)
        user_service = UserService(db)
        try:
            user = await user_service.get_user_by_id(user_id)
            if user:
                logger.info(f"✅ User found: {user_id}")
        except Exception as e:
            logger.warning(f"⚠️  User not found in DB, but continuing: {user_id}")
            # 사용자가 없어도 계속 진행
        
        # 1. 원본 이미지 읽기
        logger.info("📖 Reading original image...")
        image_bytes = await image.read()
        image_mime_type = image.content_type or "image/jpeg"
        logger.info(f"✅ Image read: {len(image_bytes)} bytes, MIME: {image_mime_type}")
        
        # 2. Gemini 2.5 Flash Image API로 고양이 캐릭터 생성
        logger.info("🤖 Calling Gemini 2.5 Flash Image API...")
        generated_image_bytes = await gemini_image_service.transform_to_cat_character(
            image_bytes=image_bytes,
            image_mime_type=image_mime_type
        )
        
        if not generated_image_bytes:
            raise HTTPException(
                status_code=500,
                detail=error_response(
                    message="Failed to generate cat character",
                    error_code="GENERATION_FAILED"
                )
            )
        
        logger.info(f"✅ Cat character generated: {len(generated_image_bytes)} bytes")
        
        # 3. 생성된 이미지를 S3에 업로드
        logger.info("📤 Uploading generated image to S3...")
        generated_url = await s3_service.upload_cat_character_image(
            generated_image_bytes, 
            user_id
        )
        logger.info(f"✅ Generated image uploaded: {generated_url}")
        
        # 4. base64 인코딩 (프론트엔드에서 바로 표시 가능)
        generated_image_base64 = base64.b64encode(generated_image_bytes).decode('utf-8')
        
        return success_response(
            data={
                "user_id": user_id,
                "generated_url": generated_url,
                "generated_image_base64": generated_image_base64  # 프론트엔드에서 바로 표시 가능
            },
            message="Cat character generated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to generate cat character: {e}")
        logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail=error_response(
                message="Internal server error",
                error_code="INTERNAL_ERROR"
            )
        )
