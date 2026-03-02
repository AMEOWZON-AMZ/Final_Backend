from pydantic import BaseModel, Field


class ValidateTopicResponse(BaseModel):
    ok: bool = True
    matched: bool
    date: str
    topic: str
    score: float = Field(...)
    threshold: float
    score_type: str = "siglip_cosine_similarity"
