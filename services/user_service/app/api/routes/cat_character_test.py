"""
고양이 캐릭터 AI 이미지 생성 API - 테스트용
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.gemini_image_service import gemini_image_service
from app.schemas.response import success_response, error_response
import logging
import base64

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/test-generate", response_model=dict)
async def test_generate_cat_character(
    image: UploadFile = File(...)
):
    """
    테스트용: Gemini 2.5 Flash Image로 고양이 캐릭터 생성
    
    Parameters:
    - image: 원본 사진 파일 (사람 얼굴)
    
    Returns:
    - generated_image_base64: 생성된 이미지 (base64)
    """
    try:
        logger.info(f"🎨 Test cat character generation with Gemini 2.5 Flash Image")
        logger.info(f"   Uploaded file: {image.filename}, type: {image.content_type}")
        
        # 이미지 읽기
        image_bytes = await image.read()
        logger.info(f"   Image size: {len(image_bytes)} bytes")
        
        # Gemini 2.5 Flash Image로 고양이 캐릭터 변환
        logger.info("🤖 Calling Gemini 2.5 Flash Image API...")
        
        generated_bytes = await gemini_image_service.transform_to_cat_character(
            image_bytes=image_bytes,
            image_mime_type=image.content_type or "image/jpeg"
        )
        
        if not generated_bytes:
            raise HTTPException(
                status_code=500,
                detail=error_response(
                    message="Failed to generate cat character with Gemini.",
                    error_code="GENERATION_FAILED"
                )
            )
        
        # Base64 인코딩
        image_base64 = base64.b64encode(generated_bytes).decode('utf-8')
        
        logger.info(f"✅ Cat character generated successfully")
        
        return success_response(
            data={
                "generated_image_base64": image_base64,
                "message": "Generated successfully with Gemini 2.5 Flash Image"
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
                message=f"Internal server error: {str(e)}",
                error_code="INTERNAL_ERROR"
            )
        )


