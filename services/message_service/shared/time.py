from datetime import datetime, timezone, timedelta


# 현재 UTC 시간을 ISO-8601(Z 포함) 문자열로 반환.
def now_utc_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# 현재 UTC 기준 N일 뒤의 epoch seconds 반환.
def epoch_seconds_plus_days(days: int) -> int:
    return int((datetime.now(timezone.utc) + timedelta(days=days)).timestamp())


# 현재 UTC 기준 N초 뒤 시간을 ISO-8601(Z 포함) 문자열로 반환.
def utc_iso_after_seconds(seconds: int) -> str:
    return (datetime.now(timezone.utc) + timedelta(seconds=seconds)).strftime("%Y-%m-%dT%H:%M:%SZ")
