from services.inference_service.app.core.config import settings
from services.inference_service.app.shared.ddb import ddb_table


class UserStatusRepository:
    # user_status 테이블 핸들을 초기화한다.
    def __init__(self):
        self.table = ddb_table(settings.required("DDB_USER_STATUS_TABLE"))

    # 사용자 현재 상태 레코드를 단건 조회한다.
    def get(self, user_id: str) -> dict | None:
        resp = self.table.get_item(Key={"user_id": user_id})
        return resp.get("Item")

    # 일일 상태/추론 시각을 upsert하고 is_critical 기본값을 보장한다.
    def upsert_daily_status(
        self,
        user_id: str,
        daily_status: str,
        updated_at: str,
        last_inference_at: str,
        clear_critical: bool = False,
    ) -> None:
        if clear_critical:
            self.table.update_item(
                Key={"user_id": user_id},
                UpdateExpression=(
                    "SET current_daily_status = :daily_status, "
                    "updated_at = :updated_at, "
                    "last_inference_at = :last_inference_at, "
                    "is_critical = :is_critical_false "
                    "REMOVE critical_since"
                ),
                ExpressionAttributeValues={
                    ":daily_status": daily_status,
                    ":updated_at": updated_at,
                    ":last_inference_at": last_inference_at,
                    ":is_critical_false": False,
                },
            )
            return

        self.table.update_item(
            Key={"user_id": user_id},
            UpdateExpression=(
                "SET current_daily_status = :daily_status, "
                "updated_at = :updated_at, "
                "last_inference_at = :last_inference_at, "
                "is_critical = if_not_exists(is_critical, :is_critical_default)"
            ),
            ExpressionAttributeValues={
                ":daily_status": daily_status,
                ":updated_at": updated_at,
                ":last_inference_at": last_inference_at,
                ":is_critical_default": False,
            },
        )
