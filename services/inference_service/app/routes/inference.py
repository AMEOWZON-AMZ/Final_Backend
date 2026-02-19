from fastapi import APIRouter, HTTPException

from services.inference_service.app.schemas.events import CriticalEventRequest, DailyStatusEventRequest
from services.inference_service.app.services.inference_event_service import InferenceEventService

router = APIRouter()


@router.post("/events/daily-status")
async def post_daily_status(payload: DailyStatusEventRequest):
    service = InferenceEventService()
    try:
        result = service.handle_daily_status(payload)
        return {"ok": True, "result": result}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/events/critical")
async def post_critical_event(payload: CriticalEventRequest):
    service = InferenceEventService()
    try:
        result = service.handle_critical_event(payload)
        return {"ok": True, "result": result}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
