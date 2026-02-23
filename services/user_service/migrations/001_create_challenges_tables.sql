-- 챌린지 테이블 생성 (권장 구조)
-- 실행: psql -h <RDS_HOST> -U user_admin -d postgres -f 001_create_challenges_tables.sql

-- 1. challenge_days 테이블 생성
CREATE TABLE IF NOT EXISTS challenge_days (
    id BIGSERIAL PRIMARY KEY,
    challenge_date DATE NOT NULL UNIQUE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_challenge_days_date ON challenge_days(challenge_date);

-- 2. challenge_submissions 테이블 생성
CREATE TABLE IF NOT EXISTS challenge_submissions (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    challenge_day_id BIGINT NOT NULL,
    image_url TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    -- Foreign Keys
    CONSTRAINT fk_challenge_day FOREIGN KEY (challenge_day_id) 
        REFERENCES challenge_days(id) ON DELETE CASCADE,
    CONSTRAINT fk_user FOREIGN KEY (user_id) 
        REFERENCES users(user_id) ON DELETE CASCADE,
    
    -- Unique Constraint: 한 사용자는 한 챌린지에 한 번만 제출 (race condition 방지)
    CONSTRAINT ux_user_challenge UNIQUE (user_id, challenge_day_id)
);

-- 인덱스 생성 (조회 성능 최적화)
CREATE INDEX IF NOT EXISTS idx_submission_day_user ON challenge_submissions(challenge_day_id, user_id);
CREATE INDEX IF NOT EXISTS idx_submission_user ON challenge_submissions(user_id);

-- 코멘트 추가
COMMENT ON TABLE challenge_days IS '일일 고양이 사진 챌린지';
COMMENT ON TABLE challenge_submissions IS '사용자 챌린지 제출 기록';
COMMENT ON COLUMN challenge_days.challenge_date IS '챌린지 날짜 (UNIQUE - 하루 1개 보장)';
COMMENT ON COLUMN challenge_submissions.image_url IS 'S3에 업로드된 이미지 URL';
COMMENT ON CONSTRAINT ux_user_challenge ON challenge_submissions IS '하루 1회 제출 강제 + race condition 방지';
