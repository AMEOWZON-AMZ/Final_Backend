"""
손상된 profile_image_url 수정
"""
import requests

BASE_URL = "http://k8s-userserv-userserv-faeaf14223-576848475.ap-northeast-2.elb.amazonaws.com"
USER_ID = "c478cd4c-5071-7060-2991-cc9b3bb59dff"

# 올바른 URL
CORRECT_URL = "https://ameowzon-test-files.s3.amazonaws.com/cat-characters/c478cd4c-5071-7060-2991-cc9b3bb59dff_20260226_121004_031757c7.png"

print("🔧 Profile Image URL 수정...")
print(f"📍 User ID: {USER_ID}")
print(f"✅ 올바른 URL: {CORRECT_URL}\n")

# 프로필 업데이트 API 호출
url = f"{BASE_URL}/api/v1/users/profile/{USER_ID}"

# multipart로 전송
files = {}
data = {
    'profile_image_url': CORRECT_URL
}

response = requests.post(url, data=data, files=files)

print(f"📊 응답 상태: {response.status_code}")

if response.status_code == 200:
    print("✅ 수정 완료!")
    
    # 다시 조회해서 확인
    response = requests.get(url)
    if response.status_code == 200:
        result = response.json()
        new_url = result['data']['profile_image_url']
        
        # presigned 파라미터 제거
        if '?' in new_url:
            new_url = new_url.split('?')[0]
        
        print(f"\n📸 수정된 URL (presigned 제거):")
        print(new_url)
        
        if new_url == CORRECT_URL:
            print("\n🎉 URL이 올바르게 수정되었습니다!")
        else:
            print("\n⚠️  URL이 여전히 다릅니다.")
else:
    print(f"❌ 실패: {response.text}")
