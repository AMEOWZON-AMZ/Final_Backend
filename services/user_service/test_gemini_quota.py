"""
Gemini API 할당량 테스트
동일한 키로 로컬에서 테스트
"""
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# .env 파일 로드
load_dotenv()

def test_gemini_api():
    """Gemini API 테스트"""
    api_key = os.getenv("GEMINI_API_KEY")
    
    print(f"🔑 API Key: {api_key[:20]}...")
    print(f"📍 Testing Gemini API with gemini-2.5-flash-image...")
    
    try:
        # Client 생성
        client = genai.Client(api_key=api_key)
        
        # 이미지 모델 테스트 (이전에 사용했던 모델)
        print("\n🎨 Testing image model (gemini-2.5-flash-image)...")
        
        # 간단한 텍스트 요청
        response = client.models.generate_content(
            model='gemini-2.5-flash-image',
            contents='Say "Hello from Gemini!" in one sentence.'
        )
        print(f"✅ Image model works!")
        print(f"Response: {response.text}")
        
        print("\n✅ Test passed! API key is working with gemini-2.5-flash-image.")
        
    except Exception as e:
        error_str = str(e)
        print(f"\n❌ Error: {e}")
        
        if "429" in error_str and "RESOURCE_EXHAUSTED" in error_str:
            print("\n⚠️ Quota exceeded! This API key has reached its limit for gemini-2.5-flash-image.")
            print("\nError details:")
            if "free_tier" in error_str:
                print("  - Free tier quota exhausted")
            if "limit: 0" in error_str:
                print("  - Current limit is 0 (quota fully used)")
            
            print("\nSolutions:")
            print("1. Wait for quota reset (usually resets daily)")
            print("2. Create a new Google Cloud project and get a new API key")
            print("3. Upgrade to paid tier at https://console.cloud.google.com/")
            print("4. Use a different model (e.g., gemini-1.5-flash)")
            
        elif "403" in error_str:
            print("\n⚠️ API key is invalid or doesn't have permission.")
        elif "404" in error_str:
            print("\n⚠️ Model not found. The model name might be incorrect.")
        else:
            print(f"\n⚠️ Unknown error occurred.")

if __name__ == "__main__":
    test_gemini_api()
