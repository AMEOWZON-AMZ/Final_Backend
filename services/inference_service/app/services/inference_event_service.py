from services.inference_service.app.core.config import settings
from services.inference_service.app.repositories.critical_event_tx_repo import CriticalEventTransactionRepository
from services.inference_service.app.repositories.user_friends_repo import UserFriendsRepository
from services.inference_service.app.repositories.user_status_repo import UserStatusRepository
from services.inference_service.app.schemas.events import CriticalEventRequest, DailyStatusEventRequest
from services.inference_service.app.shared.time import epoch_seconds_plus_days, now_utc_iso, to_utc_iso


class InferenceEventService:
    def __init__(self):
        self.user_status_repo = UserStatusRepository()
        self.user_friends_repo = UserFriendsRepository()
        self.critical_tx_repo = CriticalEventTransactionRepository()

    #하루 상태 업데이트
    def handle_daily_status(self, payload: DailyStatusEventRequest) -> dict:
        now_iso = now_utc_iso()
        inference_at = to_utc_iso(payload.inference_at, fallback=now_iso)

        current = self.user_status_repo.get(payload.user_id) or {}
        is_critical = bool(current.get("is_critical", False))
        current_daily_status = current.get("current_daily_status")

        #크리티컬인 상태에서 NO_DATA 들어오면 무시
        if is_critical and payload.daily_status == "NO_DATA":
            return {"action": "SKIPPED", "reason": "critical_no_data_ignored"}
        #상태가 변한 게 없으면 저장/전파 안 함
        if current_daily_status == payload.daily_status:
            return {"action": "SKIPPED", "reason": "daily_status_unchanged"}
        #사용자 테이블 업데이트
        self.user_status_repo.upsert_daily_status(
            user_id=payload.user_id,
            daily_status=payload.daily_status,
            updated_at=now_iso,
            last_inference_at=inference_at,
        )

        #팬아웃 코드
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

        #몇 명 친구에게 전파했는지까지 리턴
        return {
            "action": "UPDATED",
            "daily_status": payload.daily_status,
            "fanout_updated": fanout_updated,
            "updated_at": now_iso,
        }
    #위급 이벤트 처리
    def handle_critical_event(self, payload: CriticalEventRequest) -> dict:
        now_iso = now_utc_iso()
        occurred_at = to_utc_iso(payload.occurred_at, fallback=now_iso)

        friends = [friend.model_dump() for friend in payload.friends]
        ttl = epoch_seconds_plus_days(settings.critical_contacts_ttl_days)
        dedupe_key = f"CRITICAL#{payload.critical_user_id}"
        to_user_ids = [friend.friend_user_id for friend in payload.friends]
        outbox_payload = {
            "to_user_ids": to_user_ids,
            "title": "Critical status detected",
            "body": f"User {payload.critical_user_id} may be in danger. Please check now.",
            "critical_user_id": payload.critical_user_id,
            "critical_gps": payload.critical_gps,
            "friends": friends,
            "occurred_at": occurred_at,
        }

        changed = self.critical_tx_repo.apply_once(
            critical_user_id=payload.critical_user_id,
            source_event_id=payload.event_id,
            critical_gps=payload.critical_gps,
            friends=friends,
            created_at=now_iso,
            ttl=ttl,
            outbox_event_id=dedupe_key,
            outbox_payload=outbox_payload,
        )
        if not changed:
            return {"action": "SKIPPED", "reason": "already_critical"}

        return {
            "action": "UPDATED",
            "critical_user_id": payload.critical_user_id,
            "outbox_event_id": dedupe_key,
            "friends_count": len(to_user_ids),
            "updated_at": now_iso,
        }
