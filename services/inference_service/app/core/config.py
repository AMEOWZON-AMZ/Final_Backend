import os


class Settings:
    # 서비스 전역 설정값을 환경변수에서 로드한다.
    def __init__(self):
        self.aws_region = os.getenv("AWS_REGION", "ap-northeast-2")
        self.user_friends_gsi = os.getenv("DDB_USER_FRIENDS_GSI", "GSI1")
        self.critical_contacts_ttl_days = int(os.getenv("CRITICAL_CONTACTS_TTL_DAYS", "7"))

    @staticmethod
    # 필수 환경변수가 없으면 예외를 발생시켜 실행 시점에 빠르게 실패시킨다.
    def required(name: str) -> str:
        value = os.getenv(name)
        if not value:
            raise RuntimeError(f"Missing env var: {name}")
        return value


settings = Settings()
