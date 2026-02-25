-- GPS 좌표 컬럼 추가
-- Migration: 003_add_gps_to_submissions
-- Date: 2026-02-20
-- Description: Add GPS coordinates to challenge_submissions table

-- GPS 좌표 컬럼 추가
ALTER TABLE challenge_submissions
ADD COLUMN latitude DECIMAL(10, 8),
ADD COLUMN longitude DECIMAL(11, 8),
ADD COLUMN altitude DECIMAL(8, 2),
ADD COLUMN has_gps BOOLEAN DEFAULT FALSE;

-- 지도 범위 검색용 인덱스 (PostgreSQL)
CREATE INDEX IF NOT EXISTS idx_submissions_gps 
ON challenge_submissions(latitude, longitude) 
WHERE latitude IS NOT NULL;

-- 날짜별 GPS 있는 제출 조회용 인덱스
CREATE INDEX IF NOT EXISTS idx_submissions_date_gps
ON challenge_submissions(challenge_day_id, has_gps)
WHERE has_gps = TRUE;

-- 확인
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'challenge_submissions' 
  AND column_name IN ('latitude', 'longitude', 'altitude', 'has_gps');
