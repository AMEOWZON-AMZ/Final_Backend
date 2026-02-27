"""
Audio Validation API
음성 파일 검증 전용 API
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.schemas.response import success_response, error_response
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/validate", response_model=dict)
async def validate_audio(
    audio: UploadFile = File(None)
):
    """
    음성 파일 검증 API
    
    Parameters:
    - audio: 음성 파일 (mp3, wav, m4a, mp4)
    
    Returns:
    - status: PASS/FAIL
    - reason: 검증 결과 이유
    - metrics: 검증 메트릭 (길이, 주파수 등)
    - user_notice: 사용자에게 보여줄 메시지 (FAIL 시)
    
    Process:
    1. 파일 읽기
    2. Audio Guard 검증
       - 길이 검증 (0.5초 ~ 5초)
       - 주파수 분석 (100Hz ~ 8000Hz)
       - 품질 개선 (노이즈 제거, 정규화)
       - AWS Transcribe STT
       - Gemini LLM 판단
    3. 검증 결과 반환
    """
    try:
        logger.info("=" * 80)
        logger.info("🎤 [AUDIO_VALIDATION_API] New validation request received")
        logger.info("=" * 80)
        
        # 파일이 없는 경우 명확한 에러 메시지
        if audio is None:
            logger.error("❌ [AUDIO_VALIDATION_API] No audio file provided in request")
            logger.error("💡 [AUDIO_VALIDATION_API] Hint: Check if 'audio' field is sent with multipart/form-data")
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Audio file is required",
                    "error_code": "MISSING_AUDIO_FILE",
                    "hint": "Please send audio file with field name 'audio' using multipart/form-data"
                }
            )
        
        logger.info(f"📁 [AUDIO_VALIDATION_API] File received: {audio.filename}")
        logger.info(f"📝 [AUDIO_VALIDATION_API] Content-Type: {audio.content_type}")
        
        # 1. 파일 읽기
        logger.info("📖 [AUDIO_VALIDATION_API] Step 1/3: Reading audio file...")
        file_bytes = await audio.read()
        logger.info(f"✅ [AUDIO_VALIDATION_API] File read complete: {len(file_bytes):,} bytes ({len(file_bytes)/1024:.2f} KB)")
        
        # 2. Audio Guard 검증
        logger.info("🛡️ [AUDIO_VALIDATION_API] Step 2/3: Starting Audio Guard validation...")
        from app.services.audio_guard import audio_guard
        
        validation_result = audio_guard.process(file_bytes, audio.filename)
        
        logger.info("=" * 80)
        logger.info(f"🏁 [AUDIO_VALIDATION_API] Validation completed")
        logger.info(f"   Status: {validation_result['status']}")
        logger.info(f"   Reason: {validation_result['reason']}")
        logger.info(f"   Metrics: {validation_result.get('metrics', {})}")
        if validation_result.get('stt_text'):
            logger.info(f"   STT Text: '{validation_result['stt_text']}'")
        logger.info("=" * 80)
        
        # 3. 결과 반환
        logger.info("📦 [AUDIO_VALIDATION_API] Step 3/3: Preparing response...")
        is_valid = validation_result["status"] == "PASS"
        
        response_data = {
            "is_valid": is_valid,
            "status": validation_result["status"],
            "reason": validation_result["reason"],
            "metrics": validation_result.get("metrics", {}),
        }
        
        # FAIL인 경우 사용자 메시지 추가
        if not is_valid:
            response_data["user_notice"] = validation_result.get("user_notice", {})
            
            logger.info("❌ [AUDIO_VALIDATION_API] Validation FAILED - returning error response")
            return success_response(
                data=response_data,
                message="Audio validation failed"
            )
        
        # PASS인 경우
        logger.info("✅ [AUDIO_VALIDATION_API] Validation PASSED - returning success response")
        return success_response(
            data=response_data,
            message="Audio validation passed"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("=" * 80)
        logger.error(f"💥 [AUDIO_VALIDATION_API] Unexpected error occurred")
        logger.error(f"   Error type: {type(e).__name__}")
        logger.error(f"   Error message: {str(e)}")
        logger.error("=" * 80)
        logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail=error_response(
                message="Audio validation failed",
                error_code="VALIDATION_ERROR"
            )
        )
