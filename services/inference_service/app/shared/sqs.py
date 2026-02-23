import json
import os

import boto3

from services.inference_service.app.core.config import settings


def send_critical_agent_event(event_id: str, user_id: str, occurred_at: str):
    client = boto3.client("sqs", region_name=settings.aws_region)
    queue_url = _resolve_critical_agent_queue_url(client)

    body = json.dumps(
        {
            "event_id": event_id,
            "user_id": user_id,
            "occurred_at": occurred_at,
        }
    )
    client.send_message(QueueUrl=queue_url, MessageBody=body)


def _resolve_critical_agent_queue_url(client) -> str:
    direct_url = os.getenv("CRITICAL_AGENT_QUEUE_URL", "").strip()
    if direct_url:
        return direct_url

    queue_name = os.getenv("CRITICAL_AGENT_QUEUE_NAME", "critical-agent-queue").strip()
    if not queue_name:
        queue_name = "critical-agent-queue"

    resp = client.get_queue_url(QueueName=queue_name)
    return resp["QueueUrl"]
