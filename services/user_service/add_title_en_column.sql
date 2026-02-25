-- challenge_days 테이블에 영문 제목 컬럼 추가
-- 2026-02-23

-- 1. title_en 컬럼 추가
ALTER TABLE challenge_days 
ADD COLUMN IF NOT EXISTS title_en VARCHAR(255);

-- 2. 기존 데이터에 영문 제목 추가 (예시)
UPDATE challenge_days SET title_en = 'Sleeping Cat' WHERE title = '잠자는 고양이';
UPDATE challenge_days SET title_en = 'Playing Cat' WHERE title = '노는 고양이';
UPDATE challenge_days SET title_en = 'Eating Cat' WHERE title = '밥먹는 고양이';

-- 3. 확인
SELECT id, challenge_date, title, title_en, description 
FROM challenge_days 
ORDER BY challenge_date 
LIMIT 10;
