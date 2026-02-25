"""
Replicate AI 이미지 변환 서비스
얼굴 특징을 보존하는 고양이 캐릭터 변환
"""
import replicate
import logging
from typing import Optional
from app.core.config import settings
import httpx
import base64

logger = logging.getLogger(__name__)

# 고양이 캐릭터 변환 프롬프트
CAT_CHARACTER_TRANSFORM_PROMPT = """cute cartoon cat character, chibi style, fluffy cat ears, cat nose, cat mouth with whiskers, soft fur texture, natural cat patterns, paw hands, fluffy tail, adorable expression, pastel colors, clean illustration, white background, high quality, professional character design"""

NEGATIVE_PROMPT = """human ears, realistic photo, ugly, deformed, blurry, low quality, dark background, complex background"""


class ReplicateImageService:
    def __init__(self):
        """Replicate API 클라이언트 초기화"""
        self.token = settings.REPLICATE_TOKEN if hasattr(settings, 'REPLICATE_TOKEN') else None
        
        if not self.token:
            logger.warning("⚠️  REPLICATE_TOKEN not configured")
        else:
            # Replicate 라이브러리는 환경 변수를 사용하므로 설정
            import os
            os.environ['REPLICATE_API_TOKEN'] = self.token
            logger.info("✅ Replicate Image API configured")
    
    async def transform_to_cat_character(
        self,
        image_bytes: bytes,
        image_mime_type: str = "image/jpeg"
    ) -> Optional[bytes]:
        """
        사람 얼굴을 고양이 캐릭터로 변환
        SDXL img2img 사용
        
        Args:
            image_bytes: 원본 이미지 바이트 데이터
            image_mime_type: 이미지 MIME 타입
        
        Returns:
            생성된 고양이 캐릭터 이미지 바이트 데이터 또는 None
        """
        if not self.token:
            logger.error("❌ Replicate token not configured")
            return None
        
        try:
            logger.info(f"🎨 Transforming to cat character with Replicate SDXL")
            logger.info(f"   Image size: {len(image_bytes)} bytes")
            
            # 이미지를 base64로 인코딩
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            image_data_uri = f"data:{image_mime_type};base64,{image_base64}"
            
            logger.info(f"🤖 Calling Replicate API (SDXL img2img)...")
            
            # SDXL img2img 모델 사용
            output = replicate.run(
                "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
                input={
                    "image": image_data_uri,
                    "prompt": CAT_CHARACTER_TRANSFORM_PROMPT,
                    "negative_prompt": NEGATIVE_PROMPT,
                    "num_inference_steps": 40,
                    "guidance_scale": 7.5,
                    "prompt_strength": 0.65,  # 0.0-1.0, 낮을수록 원본 보존 (0.65 = 65% 변환)
                    "refine": "expert_ensemble_refiner",
                    "scheduler": "KarrasDPM",
                    "num_outputs": 1
                }
            )
            
            # 결과 처리
            if output:
                image_url = output[0] if isinstance(output, list) else output
                logger.info(f"✅ Image generated: {image_url}")
                
                # URL에서 이미지 다운로드
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(image_url)
                    if response.status_code == 200:
                        result_bytes = response.content
                        logger.info(f"✅ Downloaded: {len(result_bytes)} bytes")
                        return result_bytes
                    else:
                        logger.error(f"❌ Download failed: {response.status_code}")
                        return None
            else:
                logger.error("❌ No output from Replicate")
                return None
                    
        except Exception as e:
            logger.error(f"❌ Error transforming: {e}")
            logger.exception(e)
            return None


# 전역 Replicate Image 서비스 인스턴스
replicate_image_service = ReplicateImageService()
