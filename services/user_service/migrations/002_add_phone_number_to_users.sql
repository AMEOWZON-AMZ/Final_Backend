-- 사용자 테이블에 전화번호 컬럼 추가
-- 실행: psql -h <RDS_HOST> -U user_admin -d postgres -f 002_add_phone_number_to_users.sql

-- phone_number 컬럼 추가
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS phone_number VARCHAR(20);

-- 코멘트 추가
COMMENT ON COLUMN users.phone_number IS '사용자 전화번호 (선택)';
