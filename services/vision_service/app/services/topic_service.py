import re
from datetime import date

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings


def _is_safe_identifier(value: str) -> bool:
    return bool(
        re.fullmatch(
            r"[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)?",
            value,
        )
    )


class TopicService:
    def __init__(self):
        if not settings.database_url:
            raise RuntimeError("DATABASE_URL is required for topic validation")

        if not _is_safe_identifier(settings.topic_table):
            raise RuntimeError("TOPIC_TABLE is invalid")
        if not _is_safe_identifier(settings.topic_text_column):
            raise RuntimeError("TOPIC_TEXT_COLUMN is invalid")
        if not _is_safe_identifier(settings.topic_date_column):
            raise RuntimeError("TOPIC_DATE_COLUMN is invalid")

        self.engine: Engine = create_engine(settings.database_url, pool_pre_ping=True)

    def close(self) -> None:
        self.engine.dispose()

    def get_topic_by_date(self, target_date: date) -> str | None:
        query = text(
            f"""
            SELECT {settings.topic_text_column}
            FROM {settings.topic_table}
            WHERE {settings.topic_date_column} = :target_date
            ORDER BY {settings.topic_date_column} DESC
            LIMIT 1
            """
        )

        try:
            with self.engine.connect() as conn:
                row = conn.execute(
                    query,
                    {"target_date": target_date},
                ).first()
        except SQLAlchemyError as exc:
            raise RuntimeError("Failed to query topics from database") from exc

        if row is None or row[0] is None:
            return None
        topic = str(row[0]).strip()
        return topic or None
