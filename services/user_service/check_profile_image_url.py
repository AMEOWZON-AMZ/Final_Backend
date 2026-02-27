"""
RDS에서 profile_image_url 확인
"""
import requests

BASE_URL = "http://k8s-userserv-userserv-faeaf14223-576848475.ap-northeast-2.elb.amazonaws.com"
USER_ID = "c478cd4c-5071-7060-2991-cc9b3bb59dff"

# API로 조회
url = f"{BASE_URL}/api/v1/users/profile/{USER_ID}"
response = requests.get(url)

if response.status_code == 200:
    result = response.json()
    profile_image_url = result['data']['profile_image_url']
    
    print("📸 Profile Image URL (from API with presigned):")
    print("=" * 100)
    print(profile_image_url)
    print("\n")
    
    # presigned 파라미터 제거
    if '?' in profile_image_url:
        original_url = profile_image_url.split('?')[0]
        print("🔗 Original S3 URL (presigned 파라미터 제거):")
        print("=" * 100)
        print(original_url)
        print("\n")
        
        # URL 디코딩 확인
        from urllib.parse import unquote
        decoded_url = unquote(original_url)
        print("🔓 URL Decoded:")
        print("=" * 100)
        print(decoded_url)
        print("\n")
        
        # 여러 번 디코딩
        for i in range(5):
            decoded_url = unquote(decoded_url)
            if decoded_url == unquote(decoded_url):
                break
        
        print(f"🔓 Final Decoded URL (after {i+1} iterations):")
        print("=" * 100)
        print(decoded_url)
