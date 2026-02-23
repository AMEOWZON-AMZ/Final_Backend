import os
import json
from services.message_service.apps.msg_service.repositories.friend_repo import FriendRepository

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


def _build_critical_push_data(
    payload: dict,
    event_type: str | None,
    target_user_id: str | None = None,
) -> dict[str, str] | None:
    if event_type != "CRITICAL_ALERT":
        return None

    raw = payload.get("data")
    parsed = _parse_data_payload(raw)
    if not parsed:
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

    to_user_id = target_user_id if isinstance(target_user_id, str) and target_user_id.strip() else inner.get("to_user_id")
    if isinstance(to_user_id, str) and to_user_id.strip():
        fcm_data["to_user_id"] = to_user_id.strip()

    from_id = fcm_data.get("from_user_id")
    to_id = fcm_data.get("to_user_id")
    if from_id and to_id:
        try:
            nickname = FriendRepository().get_friend_nickname(user_id=to_id, friend_user_id=from_id)
            if nickname:
                fcm_data["nickname"] = nickname
        except Exception as exc:
            print(
                "[FCM] nickname lookup failed",
                f"from_user_id={from_id}",
                f"to_user_id={to_id}",
                f"error={exc}",
            )

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


def send_fcm(
    token: str,
    payload: dict,
    event_type: str | None = None,
    target_user_id: str | None = None,
):
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
    critical_data = _build_critical_push_data(
        payload,
        event_type=event_type,
        target_user_id=target_user_id,
    )
    message = {
        "token": token,
    }
    if critical_data:
        # CRITICAL_PUSH는 앱 커스텀 동작(전화/딥링크)을 위해 data-only로 전송.
        message["data"] = critical_data
        print(
            "[FCM] mode=data-only",
            f"db_event_type={event_type}",
            f"event_type={critical_data.get('event_type')}",
            f"to_user_id={critical_data.get('to_user_id')}",
        )
    else:
        notification = {
            "title": payload.get("title") or "New notification",
            "body": payload.get("body") or "You have a new message",
        }
        message["notification"] = notification
        raw_data = payload.get("data")
        raw_event_type = raw_data.get("event_type") if isinstance(raw_data, dict) else None
        print(
            "[FCM] mode=notification",
            f"db_event_type={event_type}",
            f"data_present={raw_data is not None}",
            f"data_event_type={raw_event_type}",
        )

    body = {"message": message}

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    resp = requests.post(url, headers=headers, data=json.dumps(body), timeout=5)
    if 200 <= resp.status_code < 300:
        return True, None
    return False, f"FCM error {resp.status_code}: {resp.text[:200]}"
