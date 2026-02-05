import os
import json

try:
    import requests
except Exception:
    requests = None

FCM_URL = "https://fcm.googleapis.com/fcm/send"


def send_fcm(token: str, event: dict):
    if requests is None:
        return False, "requests not installed"

    server_key = os.getenv("FCM_SERVER_KEY", "")
    if not server_key:
        return False, "missing FCM_SERVER_KEY"

    # Minimal notification (no message content)
    payload = {
        "to": token,
        "notification": {
            "title": "New notification",
            "body": "You have a new message",
        },
        "data": {
            "event_type": event.get("event_type"),
            "ref_id": event.get("ref_id"),
        },
    }

    headers = {
        "Authorization": f"key={server_key}",
        "Content-Type": "application/json",
    }

    resp = requests.post(FCM_URL, headers=headers, data=json.dumps(payload), timeout=5)
    if resp.status_code >= 200 and resp.status_code < 300:
        return True, None
    return False, f"FCM error {resp.status_code}"
