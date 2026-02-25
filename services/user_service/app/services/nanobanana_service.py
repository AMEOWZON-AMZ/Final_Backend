"""
Nanobanana AI 이미지 생성 서비스
사용자 사진을 AI로 변환하여 고양이 이미지 생성
"""
import httpx
import logging
from typing import Optional, Dict
from app.core.config import settings

logger = logging.getLogger(__name__)


class NanobananaService:
    def __init__(self):
        """Nanobanana API 클라이언트 초기화"""
        self.api_url = settings.NANOBANANA_API_URL
        self.api_key = settings.NANOBANANA_API_KEY
        self.timeout = 60.0  # 60초 타임아웃
        
        if not self.api_key:
            logger.warning("⚠️  NANOBANANA_API_KEY not configured")
    
    async def generate_cat_image(
        self, 
        source_image_url: str,
        cat_pattern: str,
        cat_color: str,
        user_id: str
    ) -> Optional[str]:
        """
        사용자 사진을 기반으로 AI 고양이 이미지 생성
        
        Args:
            source_image_url: 원본 사진 URL (S3)
            cat_pattern: 고양이 패턴 (예: "tabby", "solid", "calico")
            cat_color: 고양이 색상 (예: "orange", "black", "white")
            user_id: 사용자 ID (로깅용)
        
        Returns:
            생성된 이미지 URL 또는 None (실패 시)
        """
        if not self.api_key:
            logger.error("❌ Nanobanana API key not configured")
            return None
        
        try:
            logger.info(f"🎨 Generating cat image for user {user_id}")
            logger.info(f"   Pattern: {cat_pattern}, Color: {cat_color}")
            logger.info(f"   Source: {source_image_url}")
            
            # Nanobanana API 요청 페이로드
            payload = {
                "source_image_url": source_image_url,
                "prompt": f"A cute {cat_color} {cat_pattern} cat, high quality, detailed",
                "style": "realistic",
                "user_id": user_id
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # API 호출
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.api_url}/generate",
                    json=payload,
                    headers=headers
                )
                
                response.raise_for_status()
                result = response.json()
                
                generated_url = result.get("image_url")
                
                if generated_url:
                    logger.info(f"✅ Cat image generated: {generated_url}")
                    return generated_url
                else:
                    logger.error(f"❌ No image URL in response: {result}")
                    return None
                    
        except httpx.TimeoutException:
            logger.error(f"❌ Nanobanana API timeout for user {user_id}")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ Nanobanana API error: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error generating cat image: {e}")
            return None
    
    async def check_generation_status(self, job_id: str) -> Dict:
        """
        이미지 생성 작업 상태 확인 (비동기 생성 시)
        
        Args:
            job_id: 생성 작업 ID
        
        Returns:
            작업 상태 정보
        """
        if not self.api_key:
            return {"status": "error", "message": "API key not configured"}
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.api_url}/status/{job_id}",
                    headers=headers
                )
                
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"❌ Failed to check generation status: {e}")
            return {"status": "error", "message": str(e)}


# 전역 Nanobanana 서비스 인스턴스
nanobanana_service = NanobananaService()
