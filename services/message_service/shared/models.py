from dataclasses import dataclass

@dataclass
class OutboxEvent:
    event_type: str
    from_user_id: str
    to_user_id: str
    ref_id: str
    created_at: str
    status: str
    retries: int
    last_error: str | None = None

    def to_item(self):
        return {
            "pk": f"OUTBOX#{self.to_user_id}",
            "sk": f"{self.created_at}#{self.ref_id}",
            "event_type": self.event_type,
            "from_user_id": self.from_user_id,
            "to_user_id": self.to_user_id,
            "ref_id": self.ref_id,
            "created_at": self.created_at,
            "status": self.status,
            "retries": self.retries,
            "last_error": self.last_error,
        }

    def to_job(self):
        return {
            "event_type": self.event_type,
            "from_user_id": self.from_user_id,
            "to_user_id": self.to_user_id,
            "ref_id": self.ref_id,
            "created_at": self.created_at,
        }
