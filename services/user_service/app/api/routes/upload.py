"""
파일 업로드 API 엔드포인트
프로필 이미지, 야옹 소리, 위험 신호 음성 파일 업로드
"""
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.response import success_response, error_response
from app.services.s3_service import s3_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/profile-image/{user_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def upload_profile_image(
    user_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """프로필 이미지 업로드 (인증 불필요)"""
    try:
        logger.info(f"🖼️ Profile image upload request from user: {user_id}")
        logger.info(f"📁 File info: {file.filename}, {file.content_type}, {file.size if hasattr(file, 'size') else 'unknown size'}")
        
        # 사용자 존재 확인
        from app.services.user_service import UserService
        user_service = UserService(db)
        user = await user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_response(message="User not found", error_code="USER_NOT_FOUND")
            )
        
        # S3에 업로드
        file_url = await s3_service.upload_profile_image(file, user_id)
        
        # 사용자 프로필 이미지 URL 업데이트
        user.profile_image_url = file_url
        db.commit()
        db.refresh(user)
        
        logger.info(f"✅ Profile image uploaded successfully: {file_url}")
        
        return success_response(
            data={
                "file_url": file_url,
                "file_type": "profile_image",
                "user_id": user_id
            },
            message="Profile image uploaded successfully"
        )
        
    except HTTPException as e:
        logger.error(f"❌ Profile image upload failed: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"❌ Unexpected error during profile image upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response(message="Profile image upload failed", error_code="UPLOAD_ERROR")
        )


@router.post("/meow-audio/{user_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def upload_meow_audio(
    user_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """야옹 소리 음성 파일 업로드 with Audio Validation (인증 불필요)"""
    try:
        logger.info(f"🐱 Meow audio upload request from user: {user_id}")
        logger.info(f"📁 File info: {file.filename}, {file.content_type}, {file.size if hasattr(file, 'size') else 'unknown size'}")
        
        # 사용자 존재 확인
        from app.services.user_service import UserService
        user_service = UserService(db)
        user = await user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_response(message="User not found", error_code="USER_NOT_FOUND")
            )
        
        # 파일 읽기
        file_bytes = await file.read()
        
        # Audio Validation & Quality Improvement
        logger.info("🔍 Running audio validation...")
        from app.services.audio_guard import audio_guard
        
        validation_result = audio_guard.process(file_bytes, file.filename)
        
        if validation_result["status"] == "FAIL":
            logger.warning(f"❌ Audio validation failed: {validation_result['reason']}")
            user_notice = validation_result.get("user_notice", {})
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_response(
                    message=user_notice.get("message", "Audio validation failed"),
                    error_code=validation_result["reason"]
                )
            )
        
        logger.info(f"✅ Audio validation passed: {validation_result['reason']}")
        logger.info(f"📊 Metrics: {validation_result['metrics']}")
        
        # 처리된 오디오 사용 (품질 개선 완료)
        processed_audio_bytes = validation_result["audio_bytes"]
        processed_content_type = validation_result["content_type"]
        processed_extension = validation_result["file_extension"]
        
        # S3에 업로드 (처리된 오디오 사용)
        from io import BytesIO
        from fastapi import UploadFile
        
        # UploadFile 객체 재생성 (처리된 오디오로)
        processed_file = UploadFile(
            file=BytesIO(processed_audio_bytes),
            filename=f"{user_id}_meow.{processed_extension}",
            headers={"content-type": processed_content_type}
        )
        
        file_url = await s3_service.upload_meow_audio(processed_file, user_id)
        
        # 사용자 야옹 소리 URL 업데이트
        user.meow_audio_url = file_url
        db.commit()
        db.refresh(user)
        
        logger.info(f"✅ Meow audio uploaded successfully: {file_url}")
        
        return success_response(
            data={
                "file_url": file_url,
                "file_type": "meow_audio",
                "user_id": user_id,
                "validation": {
                    "status": validation_result["status"],
                    "reason": validation_result["reason"],
                    "metrics": validation_result["metrics"],
                    "stt_text": validation_result.get("stt_text")
                }
            },
            message="Meow audio uploaded successfully"
        )
        
    except HTTPException as e:
        logger.error(f"❌ Meow audio upload failed: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"❌ Unexpected error during meow audio upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response(message="Meow audio upload failed", error_code="UPLOAD_ERROR")
        )




@router.post("/batch-upload/{user_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def batch_upload_files(
    user_id: str,
    profile_image: UploadFile = File(None),
    meow_audio: UploadFile = File(None),
    train_voice: Optional[list[UploadFile]] = File(None),  # 3개의 암구호 녹음 파일
    db: Session = Depends(get_db)
):
    """여러 파일 한번에 업로드 (회원가입 시 사용, 인증 불필요)"""
    try:
        logger.info(f"📦 Batch upload request from user: {user_id}")
        
        # 사용자 존재 확인
        from app.services.user_service import UserService
        user_service = UserService(db)
        user = await user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_response(message="User not found", error_code="USER_NOT_FOUND")
            )
        
        uploaded_files = {}
        
        # 프로필 이미지 업로드
        if profile_image:
            file_url = await s3_service.upload_profile_image(profile_image, user_id)
            user.profile_image_url = file_url
            uploaded_files["profile_image"] = file_url
            logger.info(f"✅ Profile image uploaded: {file_url}")
        
        # 야옹 소리 업로드
        if meow_audio:
            file_url = await s3_service.upload_meow_audio(meow_audio, user_id)
            user.meow_audio_url = file_url
            uploaded_files["meow_audio"] = file_url
            logger.info(f"✅ Meow audio uploaded: {file_url}")
        
        # 암구호 학습용 음성 업로드 (3개)
        train_voice_urls = []
        if train_voice:
            for idx, voice_file in enumerate(train_voice[:3], 1):  # 최대 3개만
                try:
                    file_url = await s3_service.upload_train_voice(voice_file, user_id, idx)
                    train_voice_urls.append(file_url)
                    logger.info(f"✅ Train voice {idx} uploaded: {file_url}")
                except Exception as e:
                    logger.error(f"❌ Failed to upload train voice {idx}: {e}")
            
            if train_voice_urls:
                import json
                user.train_voice_urls = json.dumps(train_voice_urls)
                uploaded_files["train_voice"] = train_voice_urls
        
        # DB 업데이트
        db.commit()
        db.refresh(user)
        
        logger.info(f"🎉 Batch upload completed: {len(uploaded_files)} files uploaded")
        
        return success_response(
            data={
                "uploaded_files": uploaded_files,
                "user_id": user_id,
                "total_files": len(uploaded_files)
            },
            message=f"Batch upload completed: {len(uploaded_files)} files uploaded"
        )
        
    except HTTPException as e:
        logger.error(f"❌ Batch upload failed: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"❌ Unexpected error during batch upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response(message="Batch upload failed", error_code="UPLOAD_ERROR")
        )