from fastapi import APIRouter, HTTPException, Query

from services.inference_service.app.schemas.events import CriticalEventRequest
from services.inference_service.app.services.inference_event_service import InferenceEventService

router = APIRouter()


# Legacy daily-status endpoint is intentionally disabled.
# We now read daily status from S3 CSV on a schedule.
#
# @router.post("/events/daily-status")
# async def post_daily_status(payload: DailyStatusEventRequest):
#     service = InferenceEventService()
#     try:
#         result = service.handle_daily_status(payload)
#         return {"ok": True, "result": result}
#     except ValueError as exc:
#         raise HTTPException(status_code=400, detail=str(exc))


@router.post("/jobs/daily-status-sync")
async def run_daily_status_sync(target_date: str | None = Query(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$")):
    service = InferenceEventService()
    try:
        result = service.sync_daily_status_from_s3(target_date=target_date)
        return {"ok": True, "result": result}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"daily-status sync failed: {exc}")


@router.post("/events/critical")
async def post_critical_event(payload: CriticalEventRequest):
    service = InferenceEventService()
    try:
        result = service.handle_critical_event(payload)
        return {"ok": True, "result": result}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
