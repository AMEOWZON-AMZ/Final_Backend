"""
Simple Transcribe Service (Non-Streaming)
Streaming API 대신 일반 StartTranscriptionJob 사용
"""
import boto3
import time
import logging
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

LANGUAGE_CODE = "ko-KR"
REGION = settings.AWS_REGION


class SimpleTranscribeService:
    """일반 Transcribe API 사용 (Streaming 아님)"""
    
    def __init__(self):
        self.client = boto3.client('transcribe', region_name=REGION)
        self.s3_client = boto3.client('s3', region_name=REGION)
        self.bucket = settings.S3_BUCKET_NAME
    
    def transcribe_pcm(self, pcm_bytes: bytes, sample_rate: int = 16000) -> Optional[str]:
        """
        PCM 오디오를 텍스트로 변환
        
        Args:
            pcm_bytes: PCM 오디오 데이터
            sample_rate: 샘플레이트 (기본 16000)
        
        Returns:
            변환된 텍스트 또는 None
        """
        job_name = f"meow-transcribe-{int(time.time() * 1000)}"
        s3_key = f"temp/transcribe/{job_name}.wav"
        
        try:
            # 1. WAV 헤더 추가
            wav_bytes = self._add_wav_header(pcm_bytes, sample_rate)
            
            # 2. S3에 임시 업로드
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=s3_key,
                Body=wav_bytes,
                ContentType='audio/wav'
            )
            
            media_uri = f"s3://{self.bucket}/{s3_key}"
            
            # 3. Transcribe Job 시작
            self.client.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={'MediaFileUri': media_uri},
                MediaFormat='wav',
                LanguageCode=LANGUAGE_CODE
            )
            
            # 4. Job 완료 대기 (최대 10초)
            max_wait = 10
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                status = self.client.get_transcription_job(
                    TranscriptionJobName=job_name
                )
                
                job_status = status['TranscriptionJob']['TranscriptionJobStatus']
                
                if job_status == 'COMPLETED':
                    # 결과 가져오기
                    transcript_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
                    import requests
                    response = requests.get(transcript_uri)
                    result = response.json()
                    
                    text = result['results']['transcripts'][0]['transcript']
                    logger.info(f"Transcribe 성공: '{text}'")
                    
                    # 정리
                    self._cleanup(job_name, s3_key)
                    return text
                
                elif job_status == 'FAILED':
                    logger.error(f"Transcribe 실패: {status['TranscriptionJob'].get('FailureReason')}")
                    self._cleanup(job_name, s3_key)
                    return None
                
                time.sleep(0.5)
            
            # 타임아웃
            logger.warning(f"Transcribe 타임아웃 ({max_wait}초)")
            self._cleanup(job_name, s3_key)
            return None
            
        except Exception as e:
            logger.error(f"Transcribe 에러: {e}")
            try:
                self._cleanup(job_name, s3_key)
            except:
                pass
            return None
    
    def _add_wav_header(self, pcm_bytes: bytes, sample_rate: int) -> bytes:
        """PCM 데이터에 WAV 헤더 추가"""
        import struct
        
        num_channels = 1
        sample_width = 2  # 16-bit
        num_frames = len(pcm_bytes) // sample_width
        
        # WAV 헤더 생성
        header = struct.pack(
            '<4sI4s4sIHHIIHH4sI',
            b'RIFF',
            36 + len(pcm_bytes),
            b'WAVE',
            b'fmt ',
            16,  # fmt chunk size
            1,   # PCM
            num_channels,
            sample_rate,
            sample_rate * num_channels * sample_width,
            num_channels * sample_width,
            sample_width * 8,
            b'data',
            len(pcm_bytes)
        )
        
        return header + pcm_bytes
    
    def _cleanup(self, job_name: str, s3_key: str):
        """임시 파일 및 Job 정리"""
        try:
            # S3 파일 삭제
            self.s3_client.delete_object(Bucket=self.bucket, Key=s3_key)
        except:
            pass
        
        try:
            # Transcribe Job 삭제
            self.client.delete_transcription_job(TranscriptionJobName=job_name)
        except:
            pass


# 전역 인스턴스
simple_transcribe_service = SimpleTranscribeService()
