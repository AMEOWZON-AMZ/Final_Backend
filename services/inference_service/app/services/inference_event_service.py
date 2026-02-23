import csv
import io
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import boto3
from botocore.exceptions import ClientError

from services.inference_service.app.core.config import settings
from services.inference_service.app.repositories.critical_event_tx_repo import CriticalEventTransactionRepository
from services.inference_service.app.repositories.user_friends_repo import UserFriendsRepository
from services.inference_service.app.repositories.user_status_repo import UserStatusRepository
from services.inference_service.app.schemas.events import CriticalEventRequest, DailyStatusEventRequest
from services.inference_service.app.shared.sqs import send_critical_agent_event
from services.inference_service.app.shared.time import epoch_seconds_plus_days, now_utc_iso, to_utc_iso


class InferenceEventService:
    # Initialize repositories for status updates and critical event processing.
    def __init__(self):
        self.user_status_repo = UserStatusRepository()
        self.user_friends_repo = UserFriendsRepository()
        self.critical_tx_repo = CriticalEventTransactionRepository()

    def handle_daily_status(self, payload: DailyStatusEventRequest) -> dict:
        now_iso = now_utc_iso()
        inference_at = to_utc_iso(payload.inference_at, fallback=now_iso)

        current = self.user_status_repo.get(payload.user_id) or {}
        is_critical = bool(current.get("is_critical", False))
        current_daily_status = current.get("current_daily_status")

        # Ignore NO_DATA when user is currently in critical state.
        if is_critical and payload.daily_status == "NO_DATA":
            return {"action": "SKIPPED", "reason": "critical_no_data_ignored"}

        # Skip if status did not change.
        if current_daily_status == payload.daily_status:
            return {"action": "SKIPPED", "reason": "daily_status_unchanged"}

        self.user_status_repo.upsert_daily_status(
            user_id=payload.user_id,
            daily_status=payload.daily_status,
            updated_at=now_iso,
            last_inference_at=inference_at,
            clear_critical=is_critical,
        )

        fanout_updated = 0
        last_key = None
        while True:
            resp = self.user_friends_repo.query_by_friend_user_id(
                friend_user_id=payload.user_id,
                limit=100,
                last_key=last_key,
            )
            for item in resp.get("Items", []):
                self.user_friends_repo.update_daily_status(
                    user_id=item["user_id"],
                    friend_user_id=item["friend_user_id"],
                    daily_status=payload.daily_status,
                    updated_at=now_iso,
                )
                fanout_updated += 1

            last_key = resp.get("LastEvaluatedKey")
            if not last_key:
                break

        return {
            "action": "UPDATED",
            "daily_status": payload.daily_status,
            "fanout_updated": fanout_updated,
            "updated_at": now_iso,
        }

    def sync_daily_status_from_s3(self, target_date: str | None = None) -> dict:
        run_date = target_date or self._yesterday_in_sync_timezone().isoformat()
        try:
            datetime.strptime(run_date, "%Y-%m-%d")
        except ValueError as exc:
            raise ValueError("target_date must be YYYY-MM-DD") from exc

        key = f"{settings.daily_status_s3_prefix.strip('/')}/dt={run_date}/state_out.csv"

        s3 = boto3.client("s3", region_name=settings.aws_region)
        try:
            obj = s3.get_object(Bucket=settings.daily_status_s3_bucket, Key=key)
        except ClientError as exc:
            error_code = exc.response.get("Error", {}).get("Code", "")
            if error_code in {"NoSuchKey", "404", "NotFound"}:
                return {
                    "action": "SKIPPED",
                    "reason": "daily_status_file_not_found",
                    "target_date": run_date,
                    "s3_bucket": settings.daily_status_s3_bucket,
                    "s3_key": key,
                    "processed": 0,
                    "updated": 0,
                    "skipped": 0,
                    "errors": 0,
                }
            raise
        raw_csv = obj["Body"].read().decode("utf-8-sig")

        reader = csv.DictReader(io.StringIO(raw_csv))
        required_columns = {"uuid", "date", "cat_state"}
        columns = set(reader.fieldnames or [])
        missing = required_columns - columns
        if missing:
            raise ValueError(f"Missing required CSV columns: {sorted(missing)}")

        summary = {
            "target_date": run_date,
            "s3_bucket": settings.daily_status_s3_bucket,
            "s3_key": key,
            "processed": 0,
            "updated": 0,
            "skipped": 0,
            "errors": 0,
        }

        for row in reader:
            summary["processed"] += 1

            user_id = (row.get("uuid") or "").strip()
            daily_status = (row.get("cat_state") or "").strip().upper()
            inference_at = (row.get("date") or "").strip() or None

            if not user_id or not daily_status:
                summary["errors"] += 1
                continue

            try:
                result = self.handle_daily_status(
                    DailyStatusEventRequest(
                        user_id=user_id,
                        daily_status=daily_status,
                        inference_at=inference_at,
                    )
                )
                if result.get("action") == "UPDATED":
                    summary["updated"] += 1
                else:
                    summary["skipped"] += 1
            except ValueError:
                summary["errors"] += 1

        return summary

    def _yesterday_in_sync_timezone(self) -> date:
        tz = ZoneInfo(settings.daily_status_sync_timezone)
        local_today = datetime.now(tz).date()
        return local_today - timedelta(days=1)

    def handle_critical_event(self, payload: CriticalEventRequest) -> dict:
        now_iso = now_utc_iso()
        occurred_at = to_utc_iso(payload.occurred_at, fallback=now_iso)

        friends = [friend.model_dump() for friend in payload.friends]
        ttl = epoch_seconds_plus_days(settings.critical_contacts_ttl_days)

        changed = self.critical_tx_repo.apply_once(
            critical_user_id=payload.critical_user_id,
            source_event_id=payload.event_id,
            critical_gps=payload.critical_gps,
            friends=friends,
            created_at=now_iso,
            ttl=ttl,
        )
        if not changed:
            return {"action": "SKIPPED", "reason": "already_critical"}

        send_critical_agent_event(
            event_id=payload.event_id,
            user_id=payload.critical_user_id,
            occurred_at=occurred_at,
        )

        fanout_updated = 0
        last_key = None
        while True:
            resp = self.user_friends_repo.query_by_friend_user_id(
                friend_user_id=payload.critical_user_id,
                limit=100,
                last_key=last_key,
            )
            for item in resp.get("Items", []):
                self.user_friends_repo.update_daily_status(
                    user_id=item["user_id"],
                    friend_user_id=item["friend_user_id"],
                    daily_status="CRITICAL",
                    updated_at=now_iso,
                )
                fanout_updated += 1

            last_key = resp.get("LastEvaluatedKey")
            if not last_key:
                break

        return {
            "action": "UPDATED",
            "critical_user_id": payload.critical_user_id,
            "critical_agent_enqueued": True,
            "fanout_updated": fanout_updated,
            "occurred_at": occurred_at,
            "updated_at": now_iso,
        }
