"""
AWS S3 파일 업로드 서비스
이미지 및 음성 파일을 S3에 업로드하고 URL을 반환
"""
import boto3
import uuid
from datetime import datetime
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException
from botocore.exceptions import ClientError, NoCredentialsError
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class S3Service:
    def __init__(self):
        """S3 클라이언트 초기화"""
        try:
            # AWS 자격증명이 있으면 사용, 없으면 IAM Role 사용 (EC2)
            if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
                logger.info("Using AWS credentials from environment variables")
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_REGION
                )
            else:
                logger.info("Using IAM Role for AWS credentials (EC2)")
                self.s3_client = boto3.client(
                    's3',
                    region_name=settings.AWS_REGION
                )
            
            self.bucket_name = settings.S3_BUCKET_NAME
            self.base_url = settings.S3_BASE_URL
            logger.info(f"S3 Service initialized - Bucket: {self.bucket_name}, Region: {settings.AWS_REGION}")
        except NoCredentialsError:
            logger.error("AWS credentials not found")
            self.s3_client = None
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}")
            self.s3_client = None
    
    def _generate_file_key(self, user_id: str, file_type: str, file_extension: str, challenge_date: str = None) -> str:
        """고유한 파일 키 생성"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        
        if file_type == "profile_image":
            return f"profiles/images/{user_id}_{timestamp}_{unique_id}.{file_extension}"
        elif file_type == "meow_audio":
            return f"profiles/audio/meow/{user_id}_{timestamp}_{unique_id}.{file_extension}"
        elif file_type == "duress_audio":
            return f"profiles/audio/duress/{user_id}_{timestamp}_{unique_id}.{file_extension}"
        elif file_type == "challenge_image" and challenge_date:
            # 챌린지 이미지는 날짜 기반 고정 파일명 (자동 덮어쓰기)
            # 예: challenges/2026-02-14/a408ad9c-5011-70ef-006b-c93c46126c29.jpg
            return f"challenges/{challenge_date}/{user_id}.jpg"
        else:
            return f"uploads/{file_type}/{user_id}_{timestamp}_{unique_id}.{file_extension}"
    
    def _get_file_extension(self, filename: str) -> str:
        """파일 확장자 추출"""
        return filename.split('.')[-1].lower() if '.' in filename else ''
    
    def _validate_file(self, file: UploadFile, file_type: str) -> Tuple[bool, str]:
        """기본 파일 검증"""
        # 파일 크기 체크
        if hasattr(file, 'size') and file.size > settings.MAX_FILE_SIZE:
            return False, f"File size exceeds {settings.MAX_FILE_SIZE / (1024*1024)}MB limit"
        
        # 파일 확장자 추출
        file_extension = self._get_file_extension(file.filename) if file.filename else ''
        
        # MIME 타입 체크 (content_type과 확장자 둘 다 확인)
        if file_type == "image":
            # 허용된 이미지 확장자
            allowed_extensions = ['jpg', 'jpeg', 'png', 'webp']
            
            # content_type이 None이거나 비어있으면 확장자로 판단
            if not file.content_type:
                logger.warning(f"⚠️  content_type is None, checking extension: {file_extension}")
                if file_extension not in allowed_extensions:
                    return False, f"Invalid image extension. Allowed: {allowed_extensions}"
            else:
                # content_type이 있으면 MIME 타입 체크
                logger.info(f"🔍 Validating content_type: {file.content_type}")
                if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
                    # 확장자로 한번 더 체크 (fallback)
                    if file_extension in allowed_extensions:
                        logger.warning(f"⚠️  content_type mismatch but extension is valid: {file_extension}")
                    else:
                        return False, f"Invalid image type. content_type: {file.content_type}, Allowed: {settings.ALLOWED_IMAGE_TYPES}"
        elif file_type == "audio":
            allowed_extensions = ['mp3', 'wav', 'mp4', 'm4a']
            
            if not file.content_type:
                logger.warning(f"⚠️  content_type is None, checking extension: {file_extension}")
                if file_extension not in allowed_extensions:
                    return False, f"Invalid audio extension. Allowed: {allowed_extensions}"
            else:
                if file.content_type not in settings.ALLOWED_AUDIO_TYPES:
                    if file_extension in allowed_extensions:
                        logger.warning(f"⚠️  content_type mismatch but extension is valid: {file_extension}")
                    else:
                        return False, f"Invalid audio type. content_type: {file.content_type}, Allowed: {settings.ALLOWED_AUDIO_TYPES}"
        
        return True, "Valid file"
    
    async def upload_profile_image(self, file: UploadFile, user_id: str) -> str:
        """프로필 이미지 업로드"""
        if not self.s3_client:
            raise HTTPException(status_code=500, detail="S3 service not available")
        
        # 파일 검증
        is_valid, message = self._validate_file(file, "image")
        if not is_valid:
            raise HTTPException(status_code=400, detail=message)
        
        try:
            # 파일 키 생성
            file_extension = self._get_file_extension(file.filename)
            file_key = self._generate_file_key(user_id, "profile_image", file_extension)
            
            # S3 업로드
            file_content = await file.read()
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=file_content,
                ContentType=file.content_type,
                Metadata={
                    'user_id': user_id,
                    'file_type': 'profile_image',
                    'original_filename': file.filename
                }
            )
            
            # URL 생성
            file_url = f"{self.base_url}/{file_key}"
            logger.info(f"Profile image uploaded successfully: {file_url}")
            return file_url
            
        except ClientError as e:
            logger.error(f"S3 upload error: {e}")
            raise HTTPException(status_code=500, detail="Failed to upload file to S3")
        except Exception as e:
            logger.error(f"Unexpected error during upload: {e}")
            raise HTTPException(status_code=500, detail="File upload failed")

    async def upload_meow_audio(self, file: UploadFile, user_id: str) -> str:
        """야옹 소리 음성 파일 업로드 (AudioGuard 통과 시 WAV로 정규화 저장)"""
        if not self.s3_client:
            raise HTTPException(status_code=500, detail="S3 service not available")

        # 기본 파일 검증 (확장자/콘텐트 타입 정도만)
        is_valid, message = self._validate_file(file, "audio")
        if not is_valid:
            raise HTTPException(status_code=400, detail=message)

        # 1) 원본 bytes 읽기 (seek 불필요: 여기서 1회만 read)
        raw_bytes = await file.read()

        # 2) AudioGuard 처리
        from app.services.audio_guard import audio_guard
        guard = audio_guard.process(raw_bytes=raw_bytes, filename=file.filename or "")

        if guard.get("status") != "OK":
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Invalid meow audio",
                    "reason": guard.get("reason"),
                    "metrics": guard.get("metrics"),
                    "stt_text": guard.get("stt_text"),
                }
            )

        # 3) OK면 항상 WAV로 저장 (audio_bytes 방어)
        wav_bytes = guard.get("audio_bytes")
        if not wav_bytes:
            raise HTTPException(
                status_code=500,
                detail={
                    "message": "AudioGuard returned OK but no audio_bytes",
                    "reason": guard.get("reason"),
                    "metrics": guard.get("metrics"),
                },
            )

        file_key = self._generate_file_key(user_id, "meow_audio", "wav")

        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=wav_bytes,
                ContentType="audio/wav",
                Metadata={
                    "user_id": user_id,
                    "file_type": "meow_audio",
                    "original_filename": file.filename or "",
                    "guard_reason": guard.get("reason", ""),
                    "stt_text": (guard.get("stt_text") or "")[:200],
                }
            )

            file_url = f"{self.base_url}/{file_key}"
            logger.info(f"Meow audio uploaded (WAV) successfully: {file_url}")
            return file_url

        except ClientError as e:
            logger.error(f"S3 upload error: {e}")
            raise HTTPException(status_code=500, detail="Failed to upload audio to S3")
        except Exception as e:
            logger.error(f"Unexpected error during upload: {e}")
            raise HTTPException(status_code=500, detail="Audio upload failed")
    
    async def upload_duress_audio(self, file: UploadFile, user_id: str) -> str:
        """위험 신호 음성 파일 업로드"""
        if not self.s3_client:
            raise HTTPException(status_code=500, detail="S3 service not available")
        
        # 파일 검증
        is_valid, message = self._validate_file(file, "audio")
        if not is_valid:
            raise HTTPException(status_code=400, detail=message)
        
        try:
            # 파일 키 생성
            file_extension = self._get_file_extension(file.filename)
            file_key = self._generate_file_key(user_id, "duress_audio", file_extension)
            
            # S3 업로드
            file_content = await file.read()
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=file_content,
                ContentType=file.content_type,
                Metadata={
                    'user_id': user_id,
                    'file_type': 'duress_audio',
                    'original_filename': file.filename
                }
            )
            
            # URL 생성
            file_url = f"{self.base_url}/{file_key}"
            logger.info(f"Duress audio uploaded successfully: {file_url}")
            return file_url
            
        except ClientError as e:
            logger.error(f"S3 upload error: {e}")
            raise HTTPException(status_code=500, detail="Failed to upload audio to S3")
        except Exception as e:
            logger.error(f"Unexpected error during upload: {e}")
            raise HTTPException(status_code=500, detail="Audio upload failed")
    
    async def upload_challenge_image(self, file: UploadFile, user_id: str, challenge_date: str) -> str:
        """챌린지 이미지 업로드"""
        if not self.s3_client:
            raise HTTPException(status_code=500, detail="S3 service not available")
        
        # 파일 정보 로깅
        logger.info(f"📸 Challenge image upload - user_id: {user_id}, date: {challenge_date}")
        logger.info(f"📸 File info - filename: {file.filename}, content_type: '{file.content_type}', size: {getattr(file, 'size', 'unknown')}")
        logger.info(f"📸 content_type type: {type(file.content_type)}, repr: {repr(file.content_type)}")
        logger.info(f"📸 Allowed types: {settings.ALLOWED_IMAGE_TYPES}")
        logger.info(f"📸 Is content_type in allowed? {file.content_type in settings.ALLOWED_IMAGE_TYPES}")
        
        # 파일 검증
        is_valid, message = self._validate_file(file, "image")
        if not is_valid:
            logger.error(f"❌ File validation failed: {message}")
            logger.error(f"❌ content_type: '{file.content_type}' (type: {type(file.content_type)})")
            logger.error(f"❌ Allowed: {settings.ALLOWED_IMAGE_TYPES}")
            raise HTTPException(status_code=400, detail=message)
        
        try:
            # 파일 키 생성
            file_extension = self._get_file_extension(file.filename)
            file_key = self._generate_file_key(user_id, "challenge_image", file_extension, challenge_date)
            
            # S3 업로드
            file_content = await file.read()
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=file_content,
                ContentType=file.content_type,
                Metadata={
                    'user_id': user_id,
                    'challenge_date': challenge_date,
                    'file_type': 'challenge_image',
                    'original_filename': file.filename
                }
            )
            
            # URL 생성
            file_url = f"{self.base_url}/{file_key}"
            logger.info(f"Challenge image uploaded successfully: {file_url}")
            return file_url
            
        except ClientError as e:
            logger.error(f"S3 upload error: {e}")
            raise HTTPException(status_code=500, detail="Failed to upload file to S3")
        except Exception as e:
            logger.error(f"Unexpected error during upload: {e}")
            raise HTTPException(status_code=500, detail="File upload failed")
    
    def generate_presigned_url(self, file_url: str, expiration: int = 3600) -> str:
        """
        S3 파일에 대한 presigned URL 생성
        
        Args:
            file_url: S3 파일의 전체 URL
            expiration: URL 유효 시간 (초, 기본 1시간)
        
        Returns:
            임시 접근 가능한 presigned URL
        """
        if not self.s3_client:
            logger.warning("S3 client not available, returning original URL")
            return file_url
        
        try:
            # URL에서 파일 키 추출
            file_key = file_url.replace(f"{self.base_url}/", "")
            
            # Presigned URL 생성
            presigned_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': file_key
                },
                ExpiresIn=expiration
            )
            
            logger.debug(f"Generated presigned URL for: {file_key}")
            return presigned_url
            
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            return file_url
        except Exception as e:
            logger.error(f"Unexpected error generating presigned URL: {e}")
            return file_url
    
    def delete_file(self, file_url: str) -> bool:
        """S3에서 파일 삭제"""
        if not self.s3_client:
            return False
        
        try:
            # URL에서 파일 키 추출
            file_key = file_url.replace(f"{self.base_url}/", "")
            
            # S3에서 삭제
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            
            logger.info(f"File deleted successfully: {file_key}")
            return True
            
        except ClientError as e:
            logger.error(f"S3 delete error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during delete: {e}")
            return False


# 전역 S3 서비스 인스턴스
s3_service = S3Service()