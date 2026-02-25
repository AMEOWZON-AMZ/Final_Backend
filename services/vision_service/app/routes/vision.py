from datetime import datetime, timezone

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.core.config import settings
from app.core.container import get_clip_service, get_topic_service
from app.schemas.vision import ValidateTopicResponse

router = APIRouter(prefix="/vision")


def _parse_date(date_str: str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="date must be YYYY-MM-DD") from exc


@router.post("/validate", response_model=ValidateTopicResponse)
async def validate_against_daily_topics(file: UploadFile = File(...), date: str | None = Form(None)):
    if file.content_type and not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image file upload is allowed")

    raw = await file.read(settings.max_bytes + 1)
    if not raw:
        raise HTTPException(status_code=400, detail="Empty file is not allowed")
    if len(raw) > settings.max_bytes:
        raise HTTPException(status_code=413, detail="File size exceeded")

    if not date:
        date = datetime.now(timezone.utc).date().isoformat()
    target_date = _parse_date(date)

    try:
        topic = get_topic_service().get_topic_by_date(target_date)
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    if not topic:
        raise HTTPException(status_code=404, detail="No topic found for the target date")

    try:
        jpeg_bytes = get_clip_service().normalize_image(raw)
        score = get_clip_service().score_topic(jpeg_bytes, topic)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    matched = score >= settings.score_threshold
    return ValidateTopicResponse(
        matched=matched,
        date=date,
        topic=topic,
        score=round(score, 4),
        threshold=settings.score_threshold,
    )
