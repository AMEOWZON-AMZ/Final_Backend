import logging
import sys

from services.inference_service.app.services.inference_event_service import InferenceEventService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> int:
    try:
        result = InferenceEventService().sync_daily_status_from_s3()
        logger.info("daily status sync succeeded: %s", result)
        return 0
    except Exception:
        logger.exception("daily status sync failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
