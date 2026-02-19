import os


class Settings:
    def __init__(self):
        self.aws_region = os.getenv("AWS_REGION", "ap-northeast-2")
        self.user_friends_gsi = os.getenv("DDB_USER_FRIENDS_GSI", "GSI1")
        self.critical_contacts_ttl_days = int(os.getenv("CRITICAL_CONTACTS_TTL_DAYS", "7"))

    @staticmethod
    def required(name: str) -> str:
        value = os.getenv(name)
        if not value:
            raise RuntimeError(f"Missing env var: {name}")
        return value


settings = Settings()
