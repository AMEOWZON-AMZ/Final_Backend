import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from fastapi import FastAPI

from services.inference_service.app.core.config import settings
from services.inference_service.app.routes.health import router as health_router
from services.inference_service.app.routes.inference import router as inference_router
from services.inference_service.app.services.inference_event_service import InferenceEventService

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

logger = logging.getLogger(__name__)


class DailyStatusSyncScheduler:
    def __init__(self):
        self._task: asyncio.Task | None = None
        self._stop = asyncio.Event()

    async def start(self) -> None:
        if not settings.daily_status_sync_enabled:
            logger.info("Daily status sync scheduler is disabled")
            return

        self._stop.clear()
        self._task = asyncio.create_task(self._run(), name="daily-status-sync")
        logger.info("Daily status sync scheduler started")

    async def stop(self) -> None:
        self._stop.set()
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        logger.info("Daily status sync scheduler stopped")

    async def _run(self) -> None:
        while not self._stop.is_set():
            delay = self._seconds_until_next_run()
            try:
                await asyncio.wait_for(self._stop.wait(), timeout=delay)
                return
            except TimeoutError:
                pass

            try:
                result = await asyncio.to_thread(InferenceEventService().sync_daily_status_from_s3)
                logger.info("Daily status sync completed: %s", result)
            except Exception:
                logger.exception("Daily status sync failed")

    @staticmethod
    def _seconds_until_next_run() -> float:
        tz = ZoneInfo(settings.daily_status_sync_timezone)
        now = datetime.now(tz)
        next_run = now.replace(
            hour=settings.daily_status_sync_hour,
            minute=0,
            second=0,
            microsecond=0,
        )
        if now >= next_run:
            next_run = next_run + timedelta(days=1)
        return max((next_run - now).total_seconds(), 1.0)


scheduler = DailyStatusSyncScheduler()


@asynccontextmanager
async def lifespan(_: FastAPI):
    await scheduler.start()
    try:
        yield
    finally:
        await scheduler.stop()


app = FastAPI(title="inference-status-service", version="1.0.0", lifespan=lifespan)

app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(inference_router, tags=["events"])
