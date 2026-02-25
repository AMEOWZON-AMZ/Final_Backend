"""
Gemini AI 이미지 생성 서비스
사용자 사진을 기반으로 고양이 캐릭터 이미지 생성
"""
import google.generativeai as genai
import logging
from typing import Optional
from app.core.config import settings
from PIL import Image
import io
import httpx
import base64

logger = logging.getLogger(__name__)

# Gemini 프롬프트 (앞서 작성한 프롬프트)
CAT_CHARACTER_PROMPT = """Create a cute cartoon cat character avatar inspired by the reference image.

GOAL: Make a recognizable, cute cat character with SIMPLE, NATURAL fur patterns.

═══════════════════════════════════════════════════════════════

👁️ EYES - COPY THE SHAPE EXACTLY:

Look at the reference eyes carefully:
- What is the eye shape? (round, almond, narrow, wide, upturned, downturned)
- How big are they relative to the face?
- How far apart are they?
- What angle do they have?
- What expression do they show?

On the cat character:
- Use the EXACT SAME eye shape
- Keep the same size ratio
- Keep the same spacing
- Keep the same angle
- Keep the same expression
- Make them a bit larger for cartoon style, but keep the shape
- Add simple sparkle (1-2 small dots)
- Match the eye color

This is THE MOST IMPORTANT thing - get the eye shape right!

═══════════════════════════════════════════════════════════════

😊 FACE SHAPE - COPY EXACTLY:

Look at the reference face:
- Is it round, oval, square, heart-shaped, long, angular?
- Wide or narrow?
- Soft jawline or defined?
- Small chin or prominent?
- Full cheeks or slim?

On the cat character:
- Use the SAME face shape
- Keep the same proportions
- Add a small, subtle cat muzzle (don't change the base face shape)
- The face outline should match the person's face outline

═══════════════════════════════════════════════════════════════

😄 EXPRESSION - COPY EXACTLY:

Look at the reference expression:
- Smiling? How much? Wide or subtle?
- Serious? Playful? Calm?
- Head straight or tilted?

On the cat character:
- Same smile (or no smile)
- Same mood and energy
- Same head angle
- Should feel like the same person

═══════════════════════════════════════════════════════════════

💇 HAIRSTYLE - COPY EXACTLY:

Look at the reference hair:
- Length: very short, short, medium, long?
- Bangs: yes or no? What style?
- Part: center, side, or no part?
- Texture: straight, wavy, curly?
- Volume: flat, normal, fluffy?
- Style: neat, messy, slicked, natural?

On the cat character:
- Convert to fur with the EXACT SAME style
- Same length
- Same bangs (or no bangs)
- Same part
- Same texture
- Same volume
- Color matches the hair color

═══════════════════════════════════════════════════════════════

🎨 FUR COLOR & PATTERN - SIMPLE & NATURAL:

STEP 1: Choose base fur color (based on skin tone):

Light skin → Cream, light orange, or pale gray
Medium skin → Orange, light brown, or medium gray  
Tan skin → Golden brown or warm tan
Dark skin → Dark brown, charcoal gray, or black

STEP 2: Choose ONE simple pattern (or none):

OPTION 1 - SOLID COLOR (Simplest):
- Just one main color all over
- Lighter shade on belly, chest, muzzle (white or cream)
- That's it - clean and simple

OPTION 2 - LIGHT TABBY (Subtle stripes):
- Base color + slightly darker stripes
- Just a few simple stripes on the back and sides
- Small "M" shape on forehead (optional)
- Keep it minimal and natural

OPTION 3 - BICOLOR (Two colors):
- Main color on back, head, tail
- White or cream on chest, belly, paws
- Clean division, like a tuxedo cat
- Simple and classic

OPTION 4 - SIMPLE PATCHES (A few spots):
- Base color with 2-3 large patches of another color
- Like a calico but simpler
- Not too many patches

STEP 3: Add minimal natural details:

- Lighter fur on muzzle area (white/cream) - this is natural for cats
- Lighter fur on chest/belly (optional)
- Pink nose, pink paw pads, pink inner ears
- That's all - keep it simple!

COLOR PALETTE - Use only 2-3 colors total:
- Main fur color
- One lighter shade (for belly/muzzle)
- Pink (for nose, pads, ears)
- Optional: one darker shade if using stripes/patches

═══════════════════════════════════════════════════════════════

🎭 OTHER FEATURES:

Eyebrows:
- Simple darker fur markings matching the eyebrow shape
- Not too prominent, just visible

Nose:
- Small pink triangle
- Simple and cute

Mouth:
- Small cat mouth
- Matches the reference smile width
- Tiny fangs if smiling (optional)

Ears:
- Large fluffy cat ears
- Match the main fur color
- Pink inside

Body:
- Chibi style (big head, small body)
- Paw hands with pink pads
- Fluffy tail

═══════════════════════════════════════════════════════════════

🎨 ART STYLE:

- Clean cartoon style (like Zootopia, Puss in Boots)
- Chibi proportions
- Smooth, clean lines
- Simple shading (not too much)
- Bright, warm colors
- Cute and friendly
- Professional but not over-detailed

Keep it SIMPLE and CLEAN - no complex patterns, no heavy details.

═══════════════════════════════════════════════════════════════

🖼️ BACKGROUND:

- Transparent or pure white
- No background elements
- Clean edges

═══════════════════════════════════════════════════════════════

✅ CHECKLIST:

MUST MATCH:
✓ Eye shape exact
✓ Face shape exact
✓ Expression exact
✓ Hairstyle exact (length, bangs, part, texture)

KEEP SIMPLE:
✓ Natural cat fur color (not human skin tone)
✓ SIMPLE pattern (solid, light stripes, bicolor, or simple patches)
✓ Only 2-3 colors total
✓ Lighter muzzle area (natural for cats)
✓ Clean and not over-detailed

OVERALL:
✓ Recognizable as this person
✓ Cute and appealing
✓ Natural cat appearance
✓ NOT busy or over-patterned
✓ Clean and simple

═══════════════════════════════════════════════════════════════

⚠️ IMPORTANT - KEEP PATTERNS SIMPLE:

DO NOT:
❌ Add complex tribal-looking patterns
❌ Add too many stripes or spots
❌ Use too many colors
❌ Make busy, complicated designs
❌ Add face paint-like markings

DO:
✓ Keep it natural and simple
✓ Use patterns real cats have
✓ Less is more
✓ Clean and minimal
✓ Just enough to add interest, not overwhelm

Think of real cats - they have simple, natural patterns:
- Solid color cats (one color)
- Tabby cats (a few stripes)
- Tuxedo cats (two colors, clean division)
- Calico cats (a few large patches)

Keep it that simple!

═══════════════════════════════════════════════════════════════

FINAL INSTRUCTION:

Create a cute cat character that:

1. Has the person's EXACT eye shape (most important!)
2. Has the person's EXACT face shape
3. Has the person's EXACT expression
4. Has the person's EXACT hairstyle
5. Uses natural cat fur colors (not human skin)
6. Has SIMPLE, NATURAL fur patterns (like real cats)
7. Uses only 2-3 colors
8. Is CLEAN and NOT over-detailed

Think: "A cute cartoon cat that looks like this person, with simple natural cat coloring."

Keep it simple, keep it natural, keep it recognizable!"""


class GeminiService:
    def __init__(self):
        """Gemini API 클라이언트 초기화"""
        self.api_key = settings.GEMINI_API_KEY
        
        if not self.api_key:
            logger.warning("⚠️  GEMINI_API_KEY not configured")
        else:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            logger.info("✅ Gemini API configured")
    
    async def download_image_from_url(self, image_url: str) -> Optional[Image.Image]:
        """
        URL에서 이미지 다운로드
        
        Args:
            image_url: 이미지 URL (S3 등)
        
        Returns:
            PIL Image 객체 또는 None
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(image_url)
                response.raise_for_status()
                
                image = Image.open(io.BytesIO(response.content))
                return image
                
        except Exception as e:
            logger.error(f"❌ Failed to download image from {image_url}: {e}")
            return None
    
    async def generate_cat_character(
        self, 
        source_image_url: str,
        user_id: str
    ) -> Optional[str]:
        """
        사용자 사진을 기반으로 AI 고양이 캐릭터 이미지 생성
        
        Args:
            source_image_url: 원본 사진 URL (S3)
            user_id: 사용자 ID (로깅용)
        
        Returns:
            생성된 이미지의 base64 인코딩 문자열 또는 None (실패 시)
        """
        if not self.api_key:
            logger.error("❌ Gemini API key not configured")
            return None
        
        try:
            logger.info(f"🎨 Generating cat character for user {user_id}")
            logger.info(f"   Source: {source_image_url}")
            
            # 1. 원본 이미지 다운로드
            source_image = await self.download_image_from_url(source_image_url)
            if not source_image:
                logger.error("❌ Failed to download source image")
                return None
            
            logger.info(f"✅ Source image downloaded: {source_image.size}")
            
            # 2. Gemini API 호출
            logger.info("🤖 Calling Gemini API for image generation...")
            
            response = self.model.generate_content(
                [CAT_CHARACTER_PROMPT, source_image],
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    top_p=0.95,
                    top_k=40,
                    max_output_tokens=8192,
                )
            )
            
            # 3. 생성된 이미지 추출
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                
                # 이미지 파트 찾기
                for part in candidate.content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        # 이미지 데이터를 base64로 인코딩
                        image_data = part.inline_data.data
                        image_base64 = base64.b64encode(image_data).decode('utf-8')
                        
                        logger.info(f"✅ Cat character generated successfully")
                        return image_base64
                
                logger.error("❌ No image data in Gemini response")
                return None
            else:
                logger.error("❌ No candidates in Gemini response")
                return None
                    
        except Exception as e:
            logger.error(f"❌ Unexpected error generating cat character: {e}")
            logger.exception(e)
            return None


# 전역 Gemini 서비스 인스턴스
gemini_service = GeminiService()
