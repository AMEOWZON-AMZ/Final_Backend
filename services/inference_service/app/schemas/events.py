from typing import Any, Literal

from pydantic import BaseModel, Field


DailyStatus = Literal["HAPPY", "SOSO", "SAD", "FAINT", "NO_DATA"]


class DailyStatusEventRequest(BaseModel):
    event_id: str | None = None
    user_id: str = Field(..., min_length=1)
    daily_status: DailyStatus
    inference_at: str | None = None


class FriendGpsPayload(BaseModel):
    friend_user_id: str = Field(..., min_length=1)
    friend_gps: dict[str, Any] | str | None = None


class CriticalEventRequest(BaseModel):
    event_id: str = Field(..., min_length=1)
    critical_user_id: str = Field(..., min_length=1)
    critical_gps: dict[str, Any] | str
    friends: list[FriendGpsPayload]
    occurred_at: str | None = None
