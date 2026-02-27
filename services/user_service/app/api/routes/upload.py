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
    """야옹 소리 음성 파일 업로드 (Audio Guard 제거됨 - /api/v1/audio/validate 사용)"""
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
        
        # S3에 업로드 (Audio Guard는 별도 API에서 처리)
        file_url = await s3_service.upload_meow_audio(file, user_id)
        
        # 사용자 야옹 소리 URL 업데이트
        user.meow_audio_url = file_url
        db.commit()
        db.refresh(user)
        
        logger.info(f"✅ Meow audio uploaded successfully: {file_url}")
        
        return success_response(
            data={
                "file_url": file_url,
                "file_type": "meow_audio",
                "user_id": user_id
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
        train_voice_files_data = []  # 합치기 위해 파일 데이터 저장
        
        if train_voice:
            for idx, voice_file in enumerate(train_voice[:3], 1):  # 최대 3개만
                try:
                    # 개별 파일 업로드
                    file_url = await s3_service.upload_train_voice(voice_file, user_id, idx)
                    train_voice_urls.append(file_url)
                    logger.info(f"✅ Train voice {idx} uploaded: {file_url}")
                    
                    # 파일 데이터 저장 (합치기 위해)
                    await voice_file.seek(0)  # 파일 포인터 리셋
                    file_data = await voice_file.read()
                    train_voice_files_data.append(file_data)
                    
                except Exception as e:
                    logger.error(f"❌ Failed to upload train voice {idx}: {e}")
            
            # 3개 파일을 합쳐서 추가 업로드
            if len(train_voice_files_data) == 3:
                try:
                    from pydub import AudioSegment
                    import io
                    
                    logger.info("🔗 Merging 3 train voice files...")
                    
                    # 각 파일을 AudioSegment로 변환
                    audio_segments = []
                    for idx, file_data in enumerate(train_voice_files_data, 1):
                        try:
                            audio = AudioSegment.from_file(io.BytesIO(file_data))
                            audio_segments.append(audio)
                            logger.info(f"  - File {idx} loaded: {len(audio)}ms")
                        except Exception as e:
                            logger.error(f"❌ Failed to load audio file {idx}: {e}")
                            raise
                    
                    # 3개 파일 합치기 (순차적으로 이어붙이기)
                    merged_audio = audio_segments[0] + audio_segments[1] + audio_segments[2]
                    logger.info(f"✅ Merged audio length: {len(merged_audio)}ms")
                    
                    # WAV 형식으로 변환
                    merged_buffer = io.BytesIO()
                    merged_audio.export(merged_buffer, format="wav")
                    merged_bytes = merged_buffer.getvalue()
                    
                    # S3에 업로드
                    merged_url = await s3_service.upload_merged_train_voice(merged_bytes, user_id)
                    train_voice_urls.append(merged_url)  # 4번째 URL로 추가
                    logger.info(f"✅ Merged train voice uploaded: {merged_url}")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to merge and upload train voices: {e}")
                    # 합치기 실패해도 개별 파일은 이미 업로드됨
            
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