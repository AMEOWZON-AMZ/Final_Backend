from dataclasses import dataclass

@dataclass
class OutboxEvent:
    event_id: str
    event_type: str
    status: str
    attempt_count: int
    next_retry_at: str
    created_at: str
    payload: dict
    last_error: str | None = None

    def to_item(self):
        return {
            "pk": f"EVENT#{self.event_id}",
            "sk": "EVENT",
            "event_id": self.event_id,
            "event_type": self.event_type,
            "status": self.status,
            "attempt_count": self.attempt_count,
            "next_retry_at": self.next_retry_at,
            "created_at": self.created_at,
            "payload": self.payload,
            "last_error": self.last_error,
        }

    def to_job(self):
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "created_at": self.created_at,
            "payload": self.payload,
        }
