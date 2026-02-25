import os


class Settings:
    def __init__(self):
        self.model_name = os.getenv("MODEL_NAME", "ViT-B-16-SigLIP").strip()
        self.pretrained = os.getenv("PRETRAINED", "webli").strip()
        self.max_bytes = int(os.getenv("MAX_BYTES", str(10 * 1024 * 1024)))
        self.score_threshold = float(os.getenv("SCORE_THRESHOLD", "0.22"))

        self.database_url = os.getenv("DATABASE_URL", "").strip()
        self.topic_table = os.getenv("TOPIC_TABLE", "challenge_days").strip()
        self.topic_text_column = os.getenv("TOPIC_TEXT_COLUMN", "title_en").strip()
        self.topic_date_column = os.getenv("TOPIC_DATE_COLUMN", "challenge_date").strip()

    @staticmethod
    def required(name: str) -> str:
        value = os.getenv(name, "").strip()
        if not value:
            raise RuntimeError(f"Missing env var: {name}")
        return value


settings = Settings()
