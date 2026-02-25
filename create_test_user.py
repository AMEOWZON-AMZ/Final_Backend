"""간단한 테스트 사용자 생성"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# 테스트 사용자 생성
signup_data = {
    "email": "testuser@example.com",
    "nickname": "테스트유저",
    "cat_pattern": "SOLID",
    "cat_color": "orange"
}

print("🔧 Creating test user...")
print(f"Email: {signup_data['email']}")

response = requests.post(
    f"{BASE_URL}/users/signup",
    json=signup_data
)

print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

if response.status_code == 201:
    print("\n✅ Test user created successfully!")
else:
    print("\n❌ Failed to create test user")
