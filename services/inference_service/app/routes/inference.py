from fastapi import APIRouter, HTTPException

from services.inference_service.app.schemas.events import CriticalEventRequest, DailyStatusEventRequest
from services.inference_service.app.services.inference_event_service import InferenceEventService

router = APIRouter()


# SageMaker 일일 상태 이벤트를 받아 상태 저장/전파 로직을 실행한다.
@router.post("/events/daily-status")
async def post_daily_status(payload: DailyStatusEventRequest):
    service = InferenceEventService()
    try:
        result = service.handle_daily_status(payload)
        return {"ok": True, "result": result}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


# 36시간 비활동 critical 이벤트를 받아 트랜잭션 처리 및 outbox 적재를 수행한다.
@router.post("/events/critical")
async def post_critical_event(payload: CriticalEventRequest):
    service = InferenceEventService()
    try:
        result = service.handle_critical_event(payload)
        return {"ok": True, "result": result}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
