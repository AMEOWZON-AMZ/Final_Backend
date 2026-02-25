"""
Replicate AI 이미지 생성 서비스
Stable Diffusion을 사용한 고양이 캐릭터 생성
"""
import replicate
import logging
from typing import Optional
from app.core.config import settings
import httpx

logger = logging.getLogger(__name__)

# 고양이 캐릭터 생성 프롬프트 (간결 버전)
CAT_CHARACTER_PROMPT_TEMPLATE = """A cute cartoon cat character avatar, chibi style, anthropomorphic cat.

Character features:
- Large expressive eyes
- {face_shape} face shape
- Fluffy cat ears on top of head
- Small pink nose
- Cute cat mouth with tiny fangs
- Soft fur texture
- {fur_color} fur color
- {fur_pattern} pattern
- Paw hands with pink pads
- Fluffy tail

Art style:
- Chibi proportions (big head, small body)
- Clean cartoon illustration
- Soft pastel colors
- Simple and cute
- White background
- Professional character design

High quality, detailed, adorable, friendly expression."""


class ReplicateService:
    def __init__(self):
        """Replicate API 클라이언트 초기화"""
        self.token = settings.REPLICATE_TOKEN if hasattr(settings, 'REPLICATE_TOKEN') else None
        
        if not self.token:
            logger.warning("⚠️  REPLICATE_TOKEN not configured")
        else:
            # Replicate 라이브러리는 환경 변수를 사용하므로 설정
            import os
            os.environ['REPLICATE_API_TOKEN'] = self.token
            logger.info("✅ Replicate API configured")
    
    async def generate_cat_character(
        self,
        face_shape: str = "round",
        fur_color: str = "orange",
        fur_pattern: str = "tabby stripes"
    ) -> Optional[bytes]:
        """
        AI 고양이 캐릭터 이미지 생성
        
        Args:
            face_shape: 얼굴 형태 (round, oval, square 등)
            fur_color: 털 색상 (orange, brown, gray, black 등)
            fur_pattern: 털 무늬 (solid, tabby stripes, patches 등)
        
        Returns:
            생성된 이미지 바이트 데이터 또는 None (실패 시)
        """
        if not self.token:
            logger.error("❌ Replicate token not configured")
            return None
        
        try:
            logger.info(f"🎨 Generating cat character with Replicate")
            logger.info(f"   Face: {face_shape}, Color: {fur_color}, Pattern: {fur_pattern}")
            
            # 프롬프트 생성
            prompt = CAT_CHARACTER_PROMPT_TEMPLATE.format(
                face_shape=face_shape,
                fur_color=fur_color,
                fur_pattern=fur_pattern
            )
            
            logger.info(f"📝 Prompt: {prompt[:200]}...")
            logger.info(f"🤖 Calling Replicate API...")
            
            # Replicate API 호출
            output = replicate.run(
                "stability-ai/stable-diffusion:db21e45d3f7023abc2a46ee38a23973f6dce16bb082a930b0c49861f96d1e5bf",
                input={
                    "prompt": prompt,
                    "negative_prompt": "ugly, deformed, noisy, blurry, distorted, out of focus, bad anatomy, extra limbs, poorly drawn face, poorly drawn hands, missing fingers, scary, creepy, realistic, photo",
                    "width": 512,
                    "height": 512,
                    "num_outputs": 1,
                    "num_inference_steps": 50,
                    "guidance_scale": 7.5
                }
            )
            
            # 결과는 URL 리스트로 반환됨
            if output and len(output) > 0:
                image_url = output[0]
                logger.info(f"✅ Image generated: {image_url}")
                
                # URL에서 이미지 다운로드
                async with httpx.AsyncClient() as client:
                    response = await client.get(image_url)
                    if response.status_code == 200:
                        image_bytes = response.content
                        logger.info(f"✅ Downloaded image: {len(image_bytes)} bytes")
                        return image_bytes
                    else:
                        logger.error(f"❌ Failed to download image: {response.status_code}")
                        return None
            else:
                logger.error("❌ No output from Replicate")
                return None
                    
        except Exception as e:
            logger.error(f"❌ Error generating cat character: {e}")
            logger.exception(e)
            return None
    
    async def generate_cat_from_description(
        self,
        description: str
    ) -> Optional[bytes]:
        """
        설명을 기반으로 고양이 캐릭터 생성
        
        Args:
            description: 고양이 캐릭터 설명
        
        Returns:
            생성된 이미지 바이트 데이터 또는 None
        """
        if not self.token:
            logger.error("❌ Replicate token not configured")
            return None
        
        try:
            logger.info(f"🎨 Generating cat from description")
            
            # 기본 스타일 추가
            full_prompt = f"{description}, cute cartoon cat character, chibi style, anthropomorphic, clean illustration, white background, high quality, professional character design"
            
            logger.info(f"🤖 Calling Replicate API...")
            
            output = replicate.run(
                "stability-ai/stable-diffusion:db21e45d3f7023abc2a46ee38a23973f6dce16bb082a930b0c49861f96d1e5bf",
                input={
                    "prompt": full_prompt,
                    "negative_prompt": "ugly, deformed, noisy, blurry, distorted, bad anatomy, scary, creepy, realistic, photo",
                    "width": 512,
                    "height": 512,
                    "num_outputs": 1
                }
            )
            
            if output and len(output) > 0:
                image_url = output[0]
                
                # URL에서 이미지 다운로드
                async with httpx.AsyncClient() as client:
                    response = await client.get(image_url)
                    if response.status_code == 200:
                        return response.content
                    else:
                        return None
            else:
                return None
                    
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return None


# 전역 Replicate 서비스 인스턴스
replicate_service = ReplicateService()
