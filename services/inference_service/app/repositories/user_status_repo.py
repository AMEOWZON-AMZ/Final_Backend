from services.inference_service.app.core.config import settings
from services.inference_service.app.shared.ddb import ddb_table


class UserStatusRepository:
    def __init__(self):
        self.table = ddb_table(settings.required("DDB_USER_STATUS_TABLE"))

    def get(self, user_id: str) -> dict | None:
        resp = self.table.get_item(Key={"user_id": user_id})
        return resp.get("Item")

    def upsert_daily_status(
        self,
        user_id: str,
        daily_status: str,
        updated_at: str,
        last_inference_at: str,
    ) -> None:
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
