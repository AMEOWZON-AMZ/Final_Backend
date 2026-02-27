"""
RDS에서 train_voice_urls 확인
최근 업데이트된 사용자의 train_voice_urls 개수 확인
"""
import psycopg2
import json
import os
from dotenv import load_dotenv

load_dotenv()

# RDS 연결
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT", 5432),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

cursor = conn.cursor()

# 최근 업데이트된 사용자 10명의 train_voice_urls 확인
query = """
SELECT 
    user_id, 
    nickname, 
    train_voice_urls,
    updated_at_timestamp
FROM users 
WHERE train_voice_urls IS NOT NULL 
  AND train_voice_urls != '[]'
ORDER BY updated_at_timestamp DESC 
LIMIT 10
"""

cursor.execute(query)
results = cursor.fetchall()

print("📊 최근 train_voice_urls가 있는 사용자 10명:")
print("=" * 100)

for row in results:
    user_id, nickname, train_voice_urls, updated_at = row
    
    try:
        urls = json.loads(train_voice_urls) if train_voice_urls else []
        url_count = len(urls)
        
        print(f"\n👤 {nickname} ({user_id[:20]}...)")
        print(f"   📅 업데이트: {updated_at}")
        print(f"   🎤 Train voice URLs: {url_count}개")
        
        if url_count == 4:
            print("   ✅ 정상 (3개 + 1개 병합)")
        elif url_count == 3:
            print("   ⚠️  병합 파일 없음 (3개만)")
        else:
            print(f"   ❓ 예상과 다름")
        
        for i, url in enumerate(urls, 1):
            filename = url.split('/')[-1]
            print(f"      {i}. {filename}")
            
    except Exception as e:
        print(f"   ❌ JSON 파싱 오류: {e}")

cursor.close()
conn.close()

print("\n" + "=" * 100)
