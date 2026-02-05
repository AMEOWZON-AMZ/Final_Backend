from services.message_service.apps.msg_service.repositories.outbox_repo import OutboxRepository
from services.message_service.apps.msg_service.repositories.device_token_repo import DeviceTokenRepository
from services.message_service.apps.push_worker.fcm.client import send_fcm

MAX_RETRIES = 5


def process_outbox():
    repo = OutboxRepository()
    items = repo.query_pending(limit=10)
    for item in items:
        handle_event(item)


def handle_event(event):
    # event can be job dict or outbox item dict
    to_user_id = event.get("to_user_id")
    if not to_user_id:
        return

    token_repo = DeviceTokenRepository()
    token_item = token_repo.get_token(to_user_id)

    # If no token, mark SENT (or NO_TOKEN)
    if not token_item:
        _mark_outbox(event, status="SENT")
        return

    ok, error = send_fcm(token_item["token"], event)
    if ok:
        _mark_outbox(event, status="SENT")
    else:
        retries = int(event.get("retries", 0)) + 1
        status = "FAILED" if retries >= MAX_RETRIES else "PENDING"
        _mark_outbox(event, status=status, retries=retries, error=error)


def _mark_outbox(event, status, retries=None, error=None):
    # Reconstruct keys if missing (e.g., SQS job)
    if "pk" not in event or "sk" not in event:
        if "to_user_id" in event and "created_at" in event and "ref_id" in event:
            event = dict(event)
            event["pk"] = f"OUTBOX#{event['to_user_id']}"
            event["sk"] = f"{event['created_at']}#{event['ref_id']}"
        else:
            return
    repo = OutboxRepository()
    repo.update_status(
        pk=event["pk"],
        sk=event["sk"],
        status=status,
        retries=retries if retries is not None else int(event.get("retries", 0)),
        error=error,
    )
