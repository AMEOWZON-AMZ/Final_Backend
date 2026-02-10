import os
import json

try:
    import requests
except Exception:
    requests = None

try:
    from google.oauth2 import service_account
    from google.auth.transport.requests import Request as GoogleRequest
except Exception:
    service_account = None
    GoogleRequest = None


def _get_access_token():
    if service_account is None or GoogleRequest is None:
        return None, "google-auth not installed"

    sa_json = os.getenv("FCM_SERVICE_ACCOUNT_JSON", "")
    if not sa_json:
        return None, "missing FCM_SERVICE_ACCOUNT_JSON"

    try:
        info = json.loads(sa_json)
    except Exception:
        return None, "invalid FCM_SERVICE_ACCOUNT_JSON"

    scopes = ["https://www.googleapis.com/auth/firebase.messaging"]
    creds = service_account.Credentials.from_service_account_info(info, scopes=scopes)
    creds.refresh(GoogleRequest())
    return creds.token, None


def send_fcm(token: str, payload: dict):
    if requests is None:
        return False, "requests not installed"

    project_id = os.getenv("FCM_PROJECT_ID", "")
    if not project_id:
        return False, "missing FCM_PROJECT_ID"

    access_token, err = _get_access_token()
    if err:
        return False, err

    url = f"https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"
    notification = {
        "title": payload.get("title") or "New notification",
        "body": payload.get("body") or "You have a new message",
    }

    body = {
        "message": {
            "token": token,
            "notification": notification,
        }
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    resp = requests.post(url, headers=headers, data=json.dumps(body), timeout=5)
    if 200 <= resp.status_code < 300:
        return True, None
    return False, f"FCM error {resp.status_code}: {resp.text[:200]}"
