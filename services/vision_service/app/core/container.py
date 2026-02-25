from app.services.clip_service import ClipService
from app.services.topic_service import TopicService

clip_service: ClipService | None = None
topic_service: TopicService | None = None


def init_resources() -> None:
    global clip_service, topic_service
    clip_service = ClipService()
    topic_service = TopicService()


def close_resources() -> None:
    global topic_service
    if topic_service is not None:
        topic_service.close()


def get_clip_service() -> ClipService:
    if clip_service is None:
        raise RuntimeError("ClipService is not initialized")
    return clip_service


def get_topic_service() -> TopicService:
    if topic_service is None:
        raise RuntimeError("TopicService is not initialized")
    return topic_service
