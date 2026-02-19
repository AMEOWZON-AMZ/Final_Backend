import os

class Settings:
    def __init__(self):
        self.aws_region = os.getenv("AWS_REGION", "ap-northeast-2")
        self.sqs_queue_url = os.getenv("SQS_QUEUE_URL", "")
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.audit_ttl_days = int(os.getenv("AUDIT_TTL_DAYS", "7"))

settings = Settings()
