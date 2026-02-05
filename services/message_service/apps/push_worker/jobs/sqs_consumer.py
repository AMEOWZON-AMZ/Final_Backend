import json
from services.message_service.shared.config import settings
from services.message_service.apps.push_worker.outbox.processor import handle_event

try:
    import boto3
except Exception:
    boto3 = None


def process_sqs():
    if not settings.sqs_queue_url:
        return False
    if boto3 is None:
        raise RuntimeError("boto3 is required for SQS")

    client = boto3.client("sqs", region_name=settings.aws_region)
    resp = client.receive_message(
        QueueUrl=settings.sqs_queue_url,
        MaxNumberOfMessages=10,
        WaitTimeSeconds=1,
    )
    messages = resp.get("Messages", [])
    if not messages:
        return False

    for msg in messages:
        body = json.loads(msg["Body"])
        handle_event(body)
        client.delete_message(QueueUrl=settings.sqs_queue_url, ReceiptHandle=msg["ReceiptHandle"])

    return True
