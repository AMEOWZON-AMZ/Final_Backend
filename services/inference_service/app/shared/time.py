from datetime import datetime, timezone, timedelta


# 현재 UTC 시간을 ISO-8601(Z) 문자열로 반환한다.
def now_utc_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# 입력된 시간을 UTC ISO-8601(Z) 형식으로 정규화하고, 없으면 fallback을 사용한다.
def to_utc_iso(value: str | None, fallback: str) -> str:
    if not value:
        return fallback

    raw = value.strip()
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"

    try:
        dt = datetime.fromisoformat(raw)
    except ValueError as exc:
        raise ValueError(f"Invalid ISO-8601 timestamp: {value}") from exc

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


# 현재 UTC 기준 N일 뒤 epoch seconds를 반환한다.
def epoch_seconds_plus_days(days: int) -> int:
    return int((datetime.now(timezone.utc) + timedelta(days=days)).timestamp())
