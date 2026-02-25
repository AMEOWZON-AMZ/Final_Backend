-- duress_audio_url 컬럼을 train_voice_urls (JSON 배열)로 마이그레이션
-- Step 1: 새 컬럼 추가
ALTER TABLE users ADD COLUMN train_voice_urls TEXT;

-- Step 2: 기존 duress_audio_url 데이터를 train_voice_urls로 복사 (JSON 배열 형식)
UPDATE users 
SET train_voice_urls = CONCAT('["', duress_audio_url, '"]')
WHERE duress_audio_url IS NOT NULL AND duress_audio_url != '';

-- Step 3: 빈 배열로 초기화 (NULL인 경우)
UPDATE users 
SET train_voice_urls = '[]'
WHERE train_voice_urls IS NULL;

-- Step 4: 기존 duress_audio_url 컬럼 삭제 (선택사항 - 백업 후 실행)
-- ALTER TABLE users DROP COLUMN duress_audio_url;

-- Step 5: duress_code 컬럼도 삭제 (더 이상 사용하지 않음)
-- ALTER TABLE users DROP COLUMN duress_code;
