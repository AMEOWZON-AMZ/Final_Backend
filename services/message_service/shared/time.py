from datetime import datetime, timezone, timedelta


def now_utc_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def epoch_seconds_plus_days(days: int) -> int:
    return int((datetime.now(timezone.utc) + timedelta(days=days)).timestamp())
