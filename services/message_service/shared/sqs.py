import json
from services.message_service.shared.config import settings

try:
    import boto3
except Exception:
    boto3 = None


def send_sqs_job(event):
    if not settings.sqs_queue_url:
        return
    if boto3 is None:
        raise RuntimeError("boto3 is required for SQS")
    client = boto3.client("sqs", region_name=settings.aws_region)
    body = json.dumps(event.to_job())
    client.send_message(QueueUrl=settings.sqs_queue_url, MessageBody=body)
