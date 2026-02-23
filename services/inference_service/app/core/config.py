import os


class Settings:
    # Load service-wide settings from environment variables.
    def __init__(self):
        self.aws_region = os.getenv("AWS_REGION", "ap-northeast-2")
        self.user_friends_gsi = os.getenv("DDB_USER_FRIENDS_GSI", "GSI1")
        self.critical_contacts_ttl_days = int(os.getenv("CRITICAL_CONTACTS_TTL_DAYS", "7"))

        self.daily_status_sync_enabled = os.getenv("DAILY_STATUS_SYNC_ENABLED", "true").lower() == "true"
        self.daily_status_s3_bucket = os.getenv("DAILY_STATUS_S3_BUCKET", "nyang-ml-apne2-dev")
        self.daily_status_s3_prefix = os.getenv("DAILY_STATUS_S3_PREFIX", "ml/outputs")
        self.daily_status_sync_timezone = os.getenv("DAILY_STATUS_SYNC_TIMEZONE", "Asia/Seoul")
        self.daily_status_sync_hour = int(os.getenv("DAILY_STATUS_SYNC_HOUR", "6"))

    @staticmethod
    def required(name: str) -> str:
        value = os.getenv(name)
        if not value:
            raise RuntimeError(f"Missing env var: {name}")
        return value


settings = Settings()
