-- challenge_submissions 테이블에 GPS 샘플 데이터 추가 (지도용 - 위도/경도만)
-- 2026-02-23

-- ID 1: 강남역 근처
UPDATE challenge_submissions 
SET latitude = 37.49794990, 
    longitude = 127.02762640, 
    has_gps = true 
WHERE id = 1;

-- ID 2: 홍대입구 근처
UPDATE challenge_submissions 
SET latitude = 37.55701140, 
    longitude = 126.92496420, 
    has_gps = true 
WHERE id = 2;

-- ID 4: 서울 시청 근처
UPDATE challenge_submissions 
SET latitude = 37.56653630, 
    longitude = 126.97796920, 
    has_gps = true 
WHERE id = 4;

-- ID 5: 잠실 근처
UPDATE challenge_submissions 
SET latitude = 37.51329420, 
    longitude = 127.10018340, 
    has_gps = true 
WHERE id = 5;

-- ID 6: 남산타워 근처
UPDATE challenge_submissions 
SET latitude = 37.55134480, 
    longitude = 126.98824240, 
    has_gps = true 
WHERE id = 6;

-- ID 7: 부산 해운대
UPDATE challenge_submissions 
SET latitude = 35.15854320, 
    longitude = 129.16034420, 
    has_gps = true 
WHERE id = 7;

-- ID 9: 제주 공항 근처
UPDATE challenge_submissions 
SET latitude = 33.50665890, 
    longitude = 126.49295420, 
    has_gps = true 
WHERE id = 9;

-- ID 10: 강남역 (다른 위치)
UPDATE challenge_submissions 
SET latitude = 37.49850000, 
    longitude = 127.02850000, 
    has_gps = true 
WHERE id = 10;

-- ID 11: 부산역 근처
UPDATE challenge_submissions 
SET latitude = 35.11495810, 
    longitude = 129.04156570, 
    has_gps = true 
WHERE id = 11;

-- ID 12: 여의도 근처
UPDATE challenge_submissions 
SET latitude = 37.52910000, 
    longitude = 126.92450000, 
    has_gps = true 
WHERE id = 12;

-- ID 14: 판교 근처
UPDATE challenge_submissions 
SET latitude = 37.39480000, 
    longitude = 127.11100000, 
    has_gps = true 
WHERE id = 14;

-- ID 16: 인천 송도
UPDATE challenge_submissions 
SET latitude = 37.38950000, 
    longitude = 126.64320000, 
    has_gps = true 
WHERE id = 16;

-- 확인
SELECT id, user_id, challenge_day_id, 
       latitude, longitude, has_gps,
       created_at
FROM challenge_submissions
ORDER BY id;
