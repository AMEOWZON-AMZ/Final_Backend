"""
Gemini 2.5 Flash Image 서비스
사람 얼굴 사진을 고양이 캐릭터로 변환
"""
import logging
from typing import Optional
from app.core.config import settings
import base64
from google import genai
from google.genai import types
import asyncio
import time

logger = logging.getLogger(__name__)

# Gemini API 타임아웃 설정 (초)
GEMINI_API_TIMEOUT = 120  # 2분

# 고양이 캐릭터 변환 프롬프트 - 최적화 버전
CAT_CHARACTER_TRANSFORM_PROMPT = """CREATE 3D CAT CHARACTER (Pixar/Disney style) - NOT human face with cat ears!

== CORE STYLE (MUST BE CONSISTENT) ==
3D rendered character art with:
- Semi-realistic modeling (Pixar/Disney quality)
- Smooth surfaces, soft lighting, professional quality
- Studio lighting: main light + rim light + ambient
- Rich saturated colors, smooth gradients
- WHITE background
- SAME style for ALL images

== PRESERVE FROM ORIGINAL (CRITICAL - TOP 3 PRIORITIES) ==

PRIORITY 1: EYE SHAPE & EXPRESSION (MOST IMPORTANT)
   - Eye shape: round/almond/narrow/wide → keep EXACT same shape
   - Eye size: large/medium/small → maintain identical proportions
   - Eye angle: upturned/downturned/straight → preserve angle
   - Eye spacing: close/wide → keep same distance
   - Eye openness: wide open/half-closed/squinting → DO NOT CHANGE
   - Gaze direction: where they're looking → maintain exact same
   - Eye emotion: happy/sad/serious/playful → MUST preserve

PRIORITY 2: MOUTH SHAPE & EXPRESSION (CRITICAL)
   - Mouth shape: wide/small/full lips/thin lips → keep identical
   - Mouth position: smile/neutral/frown/smirk → DO NOT ALTER
   - Mouth openness: closed/slightly open/wide open → preserve exactly
   - Lip fullness: thick/thin/medium → maintain same
   - DO NOT make "cuter" or add smile if not present
   - DO NOT change serious face to happy face

PRIORITY 3: HAIRSTYLE TO FUR ON HEAD (CRITICAL)
   - Hair length: short/medium/long → determines cat fur length (short hair = short fur, long hair = long fluffy fur)
   - Hair volume: thick/thin/fluffy → fur volume matches exactly
   - Hair parting: center/side/no part → visible in fur on head
   - Hair texture: straight/wavy/curly → fur texture reflects this
   - Bangs/fringe: present or not → translate to fur falling over forehead
   - Hair direction: swept back/forward/side → fur flows same direction
   - Hair layers: layered/one-length → fur styling matches

4. GENDER (MUST BE CLEAR):
   - Male: broader face, angular features, masculine vibe
   - Female: softer features, delicate jaw, feminine vibe

5. COLORS (MATCH BRIGHTNESS):
   - Hair color → Head fur color (light to light, dark to dark, keep exact tone)
   - Skin warmth → Body fur warmth (warm to orange/cream, cool to gray/silver)
   - Clothing colors → Cat's outfit colors (keep exact same colors and style)
   - Clothing style → Translate to cat-sized clothing (casual/formal/sporty)

6. OTHER FEATURES:
   - Face shape and proportions
   - Head angle and pose
   - Eyebrows: same position and angle

== CAT TRANSFORMATION ==

FACE STRUCTURE:
- Rounded cat face with subtle muzzle (3D depth, not flat)
- Large expressive eyes with realistic shine
- Small pink triangular nose on muzzle
- Large fluffy ears on TOP of head
- Long white whiskers from muzzle

FUR PATTERNS (Choose based on person's coloring):
- Orange Tabby: warm tones, orange/red hair → bright orange + darker stripes + white chest
- Calico: diverse colors → white base + orange patches + black patches (asymmetric)
- Tuxedo: dark hair, elegant → black body + white chest/paws/chin
- Mackerel Tabby: medium tones → gray/brown + dark stripes + M on forehead
- Solid White: very light/blonde hair → pure white with subtle shadows (no patterns)
- Solid Orange: warm ginger/orange hair → solid orange/cream (no stripes)
- Solid Gray: cool gray/silver hair → solid gray/blue-gray (no patterns)
- Solid + White: light hair → cream/white with colored markings

FUR LENGTH (MUST match person's hair length):
- Short Hair Cat: person has short hair (above shoulders) → sleek, smooth, close to body
- Long Hair Cat: person has long hair (below shoulders) → fluffy, flowing, Persian/Maine Coon style with extra fluff around neck, chest, tail

CRITICAL FUR RULES:
- Match hair brightness (NOT all dark/black)
- Each person gets DIFFERENT pattern
- Multiple tones: base + pattern + highlights + shadows
- 100% fur coverage (NO human skin visible anywhere)
- Head fur MUST reflect hairstyle (length, volume, parting, texture, direction)
- Long-haired cats: extra fluffy everywhere, especially around face/neck
- Short-haired cats: sleek and smooth everywhere

BODY:
- 3D rendered fur texture matching hair length (short: sleek / long: fluffy and flowing)
- Head fur styled to match original hairstyle
- WEARING CLOTHES: Cat is dressed in outfit matching original person's clothing
  * Shirt/Top: Same color and style as original (t-shirt, hoodie, sweater, etc.)
  * Pants/Bottoms: If visible, match original style (jeans, skirt, shorts, etc.)
  * Accessories: Keep any visible accessories (hat, scarf, glasses, etc.)
  * Fit: Clothes fit naturally on cat body (not too tight, not too loose)
  * Style: Maintain casual/formal/sporty vibe from original
- Cute cat paws visible at sleeves/cuffs (pink pads)
- Long fluffy tail visible in frame (extra fluffy if long-haired)
- Bipedal stance (standing like a person, not on all fours)

== FINAL CHECKS ==
1. EYE SHAPE preserved exactly (shape/size/angle/spacing)?
2. EYE EXPRESSION unchanged (openness/gaze/emotion)?
3. MOUTH SHAPE preserved (shape/position/openness)?
4. MOUTH EXPRESSION unchanged (smile/neutral/frown)?
5. HAIRSTYLE reflected in head fur (length/volume/parting/texture/direction)?
6. Fur length matches hair length (short hair = short fur, long hair = long fur)?
7. 3D rendered style (consistent with all images)?
8. Subtle muzzle (not flat human face)?
9. Clear male/female identification?
10. Head fur color matches hair color exactly?
11. Body fur pattern different from other images?
12. Solid colors have depth (highlights/shadows)?
13. 100% fur coverage (no human skin)?
14. Large ears on TOP of head?
15. Professional 3D quality?
16. WHITE background?
17. WEARING CLOTHES that match original outfit (color and style)?
18. Cat paws visible at sleeves/cuffs?
19. Bipedal stance (standing like a person)?

BALANCE: 70% cute cat features + 30% preserved human identity

TOP 3 PRIORITIES: EYE SHAPE/EXPRESSION then MOUTH SHAPE/EXPRESSION then HAIRSTYLE TO HEAD FUR
If ANY of these 3 fail, you have completely failed!

HAIR LENGTH RULE: Short human hair = Short fur cat, Long human hair = Long fur cat"""


class GeminiImageService:
    def __init__(self):
        """Gemini 2.5 Flash Image API 클라이언트 초기화"""
        self.api_key = settings.GEMINI_API_KEY
        
        if not self.api_key:
            logger.warning("⚠️  GEMINI_API_KEY not configured")
            self.client = None
        else:
            # 디버깅: API 키 마지막 4자리만 로그
            masked_key = f"...{self.api_key[-4:]}" if self.api_key else "None"
            logger.info(f"✅ Gemini Image API configured with key ending: {masked_key}")
            self.client = genai.Client(api_key=self.api_key)
    
    async def transform_to_cat_character(
        self,
        image_bytes: bytes,
        image_mime_type: str = "image/jpeg"
    ) -> Optional[bytes]:
        """
        사람 얼굴 사진을 고양이 캐릭터로 변환
        
        Args:
            image_bytes: 원본 이미지 바이트 데이터
            image_mime_type: 이미지 MIME 타입
        
        Returns:
            생성된 고양이 캐릭터 이미지 바이트 데이터 또는 None
        """
        if not self.client:
            logger.error("❌ Gemini API key not configured")
            return None
        
        try:
            start_time = time.time()
            logger.info(f"🎨 Transforming image to cat character with Gemini 2.5 Flash Image")
            logger.info(f"   Image size: {len(image_bytes)} bytes, MIME: {image_mime_type}")
            logger.info(f"   Timeout: {GEMINI_API_TIMEOUT} seconds")
            
            # Gemini 2.5 Flash Image 모델 사용 (타임아웃 적용)
            try:
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        self.client.models.generate_content,
                        model='gemini-2.5-flash-image',
                        contents=[
                            types.Part.from_bytes(
                                data=image_bytes,
                                mime_type=image_mime_type
                            ),
                            CAT_CHARACTER_TRANSFORM_PROMPT
                        ]
                    ),
                    timeout=GEMINI_API_TIMEOUT
                )
            except asyncio.TimeoutError:
                elapsed = time.time() - start_time
                logger.error(f"⏱️  Gemini API timeout after {elapsed:.1f} seconds (limit: {GEMINI_API_TIMEOUT}s)")
                return None
            
            elapsed = time.time() - start_time
            logger.info(f"⏱️  Gemini API responded in {elapsed:.1f} seconds")
            
            # 응답에서 이미지 추출
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                
                # 이미지 파트 찾기
                for part in candidate.content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        generated_image = part.inline_data.data
                        logger.info(f"✅ Cat character generated: {len(generated_image)} bytes (took {elapsed:.1f}s)")
                        return generated_image
                
                # 텍스트 응답만 있는 경우 (에러 메시지 등)
                if hasattr(candidate.content.parts[0], 'text'):
                    error_text = candidate.content.parts[0].text
                    logger.error(f"❌ Gemini returned text instead of image: {error_text}")
                    return None
            
            logger.error("❌ No image in Gemini response")
            return None
                    
        except Exception as e:
            logger.error(f"❌ Error transforming to cat character: {e}")
            logger.exception(e)
            return None


# 전역 Gemini Image 서비스 인스턴스
gemini_image_service = GeminiImageService()
