"""
AWS S3 파일 업로드 서비스
이미지 및 음성 파일을 S3에 업로드하고 URL을 반환
EXIF 메타데이터에서 GPS 좌표 추출 지원
"""
import boto3
import uuid
from datetime import datetime
from typing import Optional, Tuple, Dict
from fastapi import UploadFile, HTTPException
from botocore.exceptions import ClientError, NoCredentialsError
from app.core.config import settings
import logging
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import io

logger = logging.getLogger(__name__)


class S3Service:
    def __init__(self):
        """S3 클라이언트 초기화"""
        try:
            # IRSA/Pod Identity 환경에서는 boto3가 자동으로 WebIdentity 사용
            # 명시적으로 session을 생성하지 않고 기본 credential chain 사용
            logger.info("Initializing S3 client with default credential chain (IRSA/Pod Identity)")
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
        elif file_type.startswith("train_voice_"):
            return f"profiles/audio/train/{user_id}_{timestamp}_{unique_id}_{file_type}.{file_extension}"
        elif file_type == "challenge_image" and challenge_date:
            # 챌린지 미디어: 여러 장 제출 가능 (timestamp로 고유성 보장)
            # 예: challenges/2026-02-14/a408ad9c_20260214_153045.jpg (이미지)
            # 예: challenges/2026-02-14/a408ad9c_20260214_153045.mp4 (비디오)
            timestamp_ms = datetime.now().strftime("%Y%m%d_%H%M%S%f")[:-3]  # millisecond 포함
            return f"challenges/{challenge_date}/{user_id}_{timestamp_ms}.{file_extension}"
        else:
            return f"uploads/{file_type}/{user_id}_{timestamp}_{unique_id}.{file_extension}"
    
    def _get_file_extension(self, filename: str) -> str:
        """파일 확장자 추출"""
        return filename.split('.')[-1].lower() if '.' in filename else ''
    
    def _extract_gps_from_exif(self, image_bytes: bytes) -> Optional[Dict[str, float]]:
        """
        이미지 EXIF 데이터에서 GPS 좌표 추출
        
        Returns:
            {
                'latitude': 37.5665,
                'longitude': 126.9780
            }
            또는 None (GPS 정보 없음)
        """
        try:
            image = Image.open(io.BytesIO(image_bytes))
            
            # getexif() 사용 (최신 Pillow 버전 호환)
            exif_data = image.getexif()
            
            if not exif_data:
                logger.info("📍 No EXIF data found in image")
                return None
            
            # GPS 정보 추출
            gps_info = {}
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                if tag == 'GPSInfo':
                    logger.info(f"📍 Found GPSInfo in EXIF: {value}")
                    for gps_tag_id in value:
                        gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                        gps_info[gps_tag] = value[gps_tag_id]
                        logger.info(f"  - {gps_tag}: {value[gps_tag_id]}")
            
            if not gps_info:
                logger.info("📍 No GPS info found in EXIF data")
                return None
            
            # GPS 좌표 변환
            def convert_to_degrees(value):
                """GPS 좌표를 도(degree) 단위로 변환"""
                try:
                    # Tuple 또는 List 형태 처리
                    if isinstance(value, (tuple, list)) and len(value) >= 3:
                        d, m, s = value[0], value[1], value[2]
                        return float(d) + (float(m) / 60.0) + (float(s) / 3600.0)
                    # 단일 값인 경우
                    return float(value)
                except Exception as e:
                    logger.error(f"GPS conversion error: {e}, value: {value}")
                    return None
            
            result = {}
            
            # 위도
            if 'GPSLatitude' in gps_info and 'GPSLatitudeRef' in gps_info:
                lat = convert_to_degrees(gps_info['GPSLatitude'])
                if lat is not None:
                    if gps_info['GPSLatitudeRef'] == 'S':
                        lat = -lat
                    result['latitude'] = lat
                    logger.info(f"📍 Latitude: {lat}")
            
            # 경도
            if 'GPSLongitude' in gps_info and 'GPSLongitudeRef' in gps_info:
                lon = convert_to_degrees(gps_info['GPSLongitude'])
                if lon is not None:
                    if gps_info['GPSLongitudeRef'] == 'W':
                        lon = -lon
                    result['longitude'] = lon
                    logger.info(f"📍 Longitude: {lon}")
            
            if 'latitude' in result and 'longitude' in result:
                logger.info(f"✅ GPS coordinates extracted: lat={result['latitude']}, lon={result['longitude']}")
                return result
            else:
                logger.info("⚠️  Incomplete GPS data in EXIF")
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to extract GPS from EXIF: {e}", exc_info=True)
            return None
    
    def get_image_gps_from_s3(self, file_url: str) -> Optional[Dict[str, float]]:
        """
        S3에 저장된 이미지에서 GPS 좌표 추출
        
        Args:
            file_url: S3 파일의 전체 URL
        
        Returns:
            GPS 좌표 딕셔너리 또는 None
        """
        if not self.s3_client:
            logger.warning("S3 client not available")
            return None
        
        try:
            # URL에서 파일 키 추출
            file_key = file_url.replace(f"{self.base_url}/", "")
            
            # S3에서 파일 다운로드
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            
            image_bytes = response['Body'].read()
            
            # GPS 좌표 추출
            gps_data = self._extract_gps_from_exif(image_bytes)
            
            return gps_data
            
        except ClientError as e:
            logger.error(f"S3 get object error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting GPS from S3: {e}")
            return None
    
    def _validate_file(self, file: UploadFile, file_type: str) -> Tuple[bool, str]:
        """기본 파일 검증"""
        # 파일 확장자 추출
        file_extension = self._get_file_extension(file.filename) if file.filename else ''
        
        # 파일 크기 체크 (타입별로 다른 용량 허용)
        if file_type in ["video", "media"]:
            max_size = settings.MAX_VIDEO_SIZE  # 50MB
        else:
            max_size = settings.MAX_FILE_SIZE  # 10MB (image, audio 등)
            
        if hasattr(file, 'size') and file.size > max_size:
            return False, f"File size exceeds {max_size / (1024*1024)}MB limit"
        
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
        
        elif file_type == "video":
            # 허용된 비디오 확장자
            allowed_extensions = ['mp4', 'mov']
            
            if not file.content_type:
                logger.warning(f"⚠️  content_type is None, checking extension: {file_extension}")
                if file_extension not in allowed_extensions:
                    return False, f"Invalid video extension. Allowed: {allowed_extensions}"
            else:
                logger.info(f"🔍 Validating content_type: {file.content_type}")
                if file.content_type not in settings.ALLOWED_VIDEO_TYPES:
                    if file_extension in allowed_extensions:
                        logger.warning(f"⚠️  content_type mismatch but extension is valid: {file_extension}")
                    else:
                        return False, f"Invalid video type. content_type: {file.content_type}, Allowed: {settings.ALLOWED_VIDEO_TYPES}"
        
        elif file_type == "media":
            # 이미지 또는 비디오 (챌린지용)
            allowed_extensions = ['jpg', 'jpeg', 'png', 'webp', 'mp4', 'mov']
            
            if not file.content_type:
                logger.warning(f"⚠️  content_type is None, checking extension: {file_extension}")
                if file_extension not in allowed_extensions:
                    return False, f"Invalid media extension. Allowed: {allowed_extensions}"
            else:
                logger.info(f"🔍 Validating content_type: {file.content_type}")
                allowed_types = settings.ALLOWED_IMAGE_TYPES + settings.ALLOWED_VIDEO_TYPES
                if file.content_type not in allowed_types:
                    if file_extension in allowed_extensions:
                        logger.warning(f"⚠️  content_type mismatch but extension is valid: {file_extension}")
                    else:
                        return False, f"Invalid media type. content_type: {file.content_type}, Allowed: {allowed_types}"
        
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
        """야옹 소리 음성 파일 업로드 (Audio Guard 제거됨 - 별도 API 사용)"""
        if not self.s3_client:
            raise HTTPException(status_code=500, detail="S3 service not available")
        
        # 파일 검증
        is_valid, message = self._validate_file(file, "audio")
        if not is_valid:
            raise HTTPException(status_code=400, detail=message)
        
        try:
            # 파일 읽기
            file_content = await file.read()
            
            # 파일 확장자 추출
            file_extension = self._get_file_extension(file.filename)
            
            # 파일 키 생성
            file_key = self._generate_file_key(user_id, "meow_audio", file_extension)
            
            # S3 업로드
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=file_content,
                ContentType=file.content_type,
                Metadata={
                    'user_id': user_id,
                    'file_type': 'meow_audio',
                    'original_filename': file.filename
                }
            )
            
            # URL 생성
            file_url = f"{self.base_url}/{file_key}"
            logger.info(f"✅ [MEOW_AUDIO] Uploaded successfully: {file_url}")
            return file_url
            
        except HTTPException:
            raise
        except ClientError as e:
            logger.error(f"❌ [MEOW_AUDIO] S3 upload error: {e}")
            raise HTTPException(status_code=500, detail="Failed to upload audio to S3")
        except Exception as e:
            logger.error(f"❌ [MEOW_AUDIO] Unexpected error: {e}")
            raise HTTPException(status_code=500, detail="Audio upload failed")
    
    async def upload_train_voice(self, file: UploadFile, user_id: str, index: int) -> str:
        """암구호 학습용 음성 파일 업로드 (Audio Guard 제거됨 - 별도 API 사용)"""
        if not self.s3_client:
            raise HTTPException(status_code=500, detail="S3 service not available")

        # 파일 검증
        is_valid, message = self._validate_file(file, "audio")
        if not is_valid:
            raise HTTPException(status_code=400, detail=message)

        try:
            # 파일 읽기
            file_content = await file.read()

            # 파일 확장자 추출
            file_extension = self._get_file_extension(file.filename)

            # 파일 키 생성 (train_voice_1, train_voice_2, train_voice_3)
            file_key = self._generate_file_key(user_id, f"train_voice_{index}", file_extension)

            # S3 업로드
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=file_content,
                ContentType=file.content_type,
                Metadata={
                    'user_id': user_id,
                    'file_type': f'train_voice_{index}',
                    'original_filename': file.filename
                }
            )

            # URL 생성
            file_url = f"{self.base_url}/{file_key}"
            logger.info(f"✅ [TRAIN_VOICE_{index}] Uploaded successfully: {file_url}")
            return file_url

        except HTTPException:
            raise
        except ClientError as e:
            logger.error(f"❌ [TRAIN_VOICE_{index}] S3 upload error: {e}")
            raise HTTPException(status_code=500, detail="Failed to upload audio to S3")
        except Exception as e:
            logger.error(f"❌ [TRAIN_VOICE_{index}] Unexpected error: {e}")
            raise HTTPException(status_code=500, detail="Audio upload failed")
    
    async def upload_merged_train_voice(self, audio_bytes: bytes, user_id: str) -> str:
        """
        합쳐진 암구호 학습용 음성 파일 업로드
        
        새로운 경로: amz-bgm/meow/enroll/{user_id}/enroll.wav
        - 고정된 파일명으로 덮어쓰기
        - SageMaker 학습용 경로
        
        Args:
            audio_bytes: 합쳐진 오디오 바이트 데이터
            user_id: 사용자 ID
        
        Returns:
            업로드된 파일 URL
        """
        if not self.s3_client:
            raise HTTPException(status_code=500, detail="S3 service not available")
        
        try:
            # 고정된 파일 키 (덮어쓰기)
            file_key = f"meow/enroll/{user_id}/enroll.wav"
            
            # amz-bgm 버킷에 업로드
            bgm_bucket = "amz-bgm"
            
            self.s3_client.put_object(
                Bucket=bgm_bucket,
                Key=file_key,
                Body=audio_bytes,
                ContentType='audio/wav',
                Metadata={
                    'user_id': user_id,
                    'file_type': 'train_voice_merged',
                    'description': 'Merged from 3 train voice files for SageMaker training'
                }
            )
            
            # URL 생성
            file_url = f"https://{bgm_bucket}.s3.ap-northeast-2.amazonaws.com/{file_key}"
            logger.info(f"✅ [TRAIN_VOICE_MERGED] Uploaded to amz-bgm: {file_url}")
            return file_url
            
        except ClientError as e:
            logger.error(f"❌ [TRAIN_VOICE_MERGED] S3 upload error: {e}")
            raise HTTPException(status_code=500, detail="Failed to upload merged audio to S3")
        except Exception as e:
            logger.error(f"❌ [TRAIN_VOICE_MERGED] Unexpected error: {e}")
            raise HTTPException(status_code=500, detail="Merged audio upload failed")

    
    async def upload_challenge_image(self, file: UploadFile, user_id: str, challenge_date: str) -> Tuple[str, Optional[Dict[str, float]]]:
        """
        챌린지 미디어(이미지/비디오) 업로드 및 GPS 좌표 추출
        
        Returns:
            (file_url, gps_data) 튜플
            gps_data: {'latitude': float, 'longitude': float, 'altitude': float (optional)} 또는 None
        """
        if not self.s3_client:
            raise HTTPException(status_code=500, detail="S3 service not available")
        
        # 파일 정보 로깅
        logger.info(f"📸 Challenge media upload - user_id: {user_id}, date: {challenge_date}")
        logger.info(f"📸 File info - filename: {file.filename}, content_type: '{file.content_type}', size: {getattr(file, 'size', 'unknown')}")
        
        # 파일 검증 (이미지 또는 비디오)
        is_valid, message = self._validate_file(file, "media")
        if not is_valid:
            logger.error(f"❌ File validation failed: {message}")
            raise HTTPException(status_code=400, detail=message)
        
        try:
            # 파일 키 생성
            file_extension = self._get_file_extension(file.filename)
            file_key = self._generate_file_key(user_id, "challenge_image", file_extension, challenge_date)
            
            # 파일 읽기
            file_content = await file.read()
            
            # GPS 좌표 추출
            gps_data = self._extract_gps_from_exif(file_content)
            
            # S3 메타데이터 준비
            metadata = {
                'user_id': user_id,
                'challenge_date': challenge_date,
                'file_type': 'challenge_image',
                'original_filename': file.filename
            }
            
            # GPS 좌표가 있으면 메타데이터에 추가
            if gps_data:
                metadata['gps_latitude'] = str(gps_data['latitude'])
                metadata['gps_longitude'] = str(gps_data['longitude'])
                if 'altitude' in gps_data:
                    metadata['gps_altitude'] = str(gps_data['altitude'])
                logger.info(f"📍 GPS coordinates found: lat={gps_data['latitude']}, lon={gps_data['longitude']}")
            else:
                logger.info("📍 No GPS coordinates found in image")
            
            # S3 업로드
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=file_content,
                ContentType=file.content_type,
                Metadata=metadata
            )
            
            # URL 생성
            file_url = f"{self.base_url}/{file_key}"
            logger.info(f"Challenge image uploaded successfully: {file_url}")
            return file_url, gps_data
            
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
    
    async def upload_cat_character_image(self, image_bytes: bytes, user_id: str) -> str:
        """
        생성된 고양이 캐릭터 이미지를 S3에 업로드
        
        Args:
            image_bytes: 이미지 바이트 데이터
            user_id: 사용자 ID
        
        Returns:
            업로드된 이미지 URL
        """
        if not self.s3_client:
            raise HTTPException(status_code=500, detail="S3 service not available")
        
        try:
            # 파일 키 생성
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            file_key = f"cat-characters/{user_id}_{timestamp}_{unique_id}.png"
            
            # S3 업로드
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=image_bytes,
                ContentType='image/png',
                Metadata={
                    'user_id': user_id,
                    'file_type': 'cat_character',
                    'generated_by': 'gemini'
                }
            )
            
            # URL 생성
            file_url = f"{self.base_url}/{file_key}"
            logger.info(f"Cat character image uploaded successfully: {file_url}")
            return file_url
            
        except ClientError as e:
            logger.error(f"S3 upload error: {e}")
            raise HTTPException(status_code=500, detail="Failed to upload cat character to S3")
        except Exception as e:
            logger.error(f"Unexpected error during upload: {e}")
            raise HTTPException(status_code=500, detail="Cat character upload failed")
    
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


    def delete_user_files(self, user_id: str) -> bool:
        """사용자의 모든 S3 파일 삭제 (프로필, 야옹소리, train voice, 챌린지 이미지 등)"""
        if not self.s3_client:
            logger.warning("S3 client not initialized")
            return False

        try:
            # user_id가 포함된 모든 파일 찾기
            prefixes = [
                f"profiles/images/{user_id}",  # 프로필 이미지
                f"profiles/audio/meow/{user_id}",  # 야옹 소리
                f"profiles/audio/train/{user_id}",  # train voice
                f"profiles/audio/duress/{user_id}",  # duress 오디오
                f"challenges/{user_id}",  # 챌린지 이미지
                f"cat-characters/{user_id}",  # 고양이 캐릭터 이미지
            ]

            deleted_count = 0

            for prefix in prefixes:
                # 해당 prefix로 시작하는 모든 객체 조회
                paginator = self.s3_client.get_paginator('list_objects_v2')
                pages = paginator.paginate(Bucket=self.bucket_name, Prefix=prefix)

                for page in pages:
                    if 'Contents' not in page:
                        continue

                    # 객체 삭제
                    for obj in page['Contents']:
                        try:
                            self.s3_client.delete_object(
                                Bucket=self.bucket_name,
                                Key=obj['Key']
                            )
                            deleted_count += 1
                            logger.info(f"Deleted: {obj['Key']}")
                        except Exception as e:
                            logger.error(f"Failed to delete {obj['Key']}: {e}")

            logger.info(f"Total {deleted_count} files deleted for user {user_id}")
            return True

        except ClientError as e:
            logger.error(f"S3 delete user files error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during delete user files: {e}")
            return False



# 전역 S3 서비스 인스턴스
s3_service = S3Service()