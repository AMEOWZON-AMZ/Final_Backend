-- challenge_submissions 테이블에 GPS 컬럼 추가 (지도용 - 위도/경도만)
-- 2026-02-23

-- 1. latitude 컬럼 추가 (위도)
ALTER TABLE challenge_submissions 
ADD COLUMN IF NOT EXISTS latitude NUMERIC(10, 8);

-- 2. longitude 컬럼 추가 (경도)
ALTER TABLE challenge_submissions 
ADD COLUMN IF NOT EXISTS longitude NUMERIC(11, 8);

-- 3. has_gps 컬럼 추가 (GPS 정보 유무)
ALTER TABLE challenge_submissions 
ADD COLUMN IF NOT EXISTS has_gps BOOLEAN DEFAULT FALSE NOT NULL;

-- 4. GPS 관련 인덱스 추가
CREATE INDEX IF NOT EXISTS idx_submissions_gps 
ON challenge_submissions(latitude, longitude);

CREATE INDEX IF NOT EXISTS idx_submissions_date_gps 
ON challenge_submissions(challenge_day_id, has_gps);

-- 5. 기존 데이터 업데이트 (has_gps = false)
UPDATE challenge_submissions 
SET has_gps = FALSE 
WHERE has_gps IS NULL;

-- 확인
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'challenge_submissions' 
ORDER BY ordinal_position;
