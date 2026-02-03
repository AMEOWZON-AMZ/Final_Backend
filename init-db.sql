-- 초기 데이터베이스 설정
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 사용자 테이블은 SQLAlchemy에서 자동 생성되므로 여기서는 기본 설정만

-- 인덱스 생성 (성능 최적화)
-- 이 스크립트는 테이블이 생성된 후에 실행되어야 하므로 주석 처리
-- CREATE INDEX IF NOT EXISTS idx_users_cognito_user_id ON users(cognito_user_id);
-- CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
-- CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
-- CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);

-- 샘플 데이터 (선택적)
-- INSERT INTO users (cognito_user_id, email, username, full_name, is_active, is_verified) 
-- VALUES 
--     ('test-user-1', 'test1@example.com', 'testuser1', 'Test User 1', true, true),
--     ('test-user-2', 'test2@example.com', 'testuser2', 'Test User 2', true, true)
-- ON CONFLICT (cognito_user_id) DO NOTHING;