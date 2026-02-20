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
    # 서비스 계정 JSON으로 FCM v1 액세스 토큰 발급.
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


def _build_critical_push_data(payload: dict) -> dict[str, str] | None:
    raw = payload.get("data")
    parsed = _parse_data_payload(raw)
    if not parsed or parsed.get("event_type") != "CRITICAL_PUSH":
        return None

    inner = parsed.get("payload")
    if isinstance(inner, str):
        try:
            inner = json.loads(inner)
        except Exception:
            return None

    if not isinstance(inner, dict):
        inner = parsed

    phone_number = inner.get("phone_number")
    if not isinstance(phone_number, str) or not phone_number.strip():
        return None

    fcm_data = {
        "event_type": "CRITICAL_PUSH",
        "phone_number": phone_number.strip(),
    }

    from_user_id = inner.get("from_user_id")
    if isinstance(from_user_id, str) and from_user_id.strip():
        fcm_data["from_user_id"] = from_user_id.strip()

    to_user_id = inner.get("to_user_id")
    if isinstance(to_user_id, str) and to_user_id.strip():
        fcm_data["to_user_id"] = to_user_id.strip()

    return fcm_data


def _parse_data_payload(raw) -> dict | None:
    if isinstance(raw, dict):
        return raw

    if isinstance(raw, str) and raw.strip():
        try:
            parsed = json.loads(raw)
        except Exception:
            return None
        return parsed if isinstance(parsed, dict) else None

    return None


def send_fcm(token: str, payload: dict):
    # FCM notification payload 전송.
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
    critical_data = _build_critical_push_data(payload)
    if critical_data:
        body["message"]["data"] = critical_data

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    resp = requests.post(url, headers=headers, data=json.dumps(body), timeout=5)
    if 200 <= resp.status_code < 300:
        return True, None
    return False, f"FCM error {resp.status_code}: {resp.text[:200]}"
