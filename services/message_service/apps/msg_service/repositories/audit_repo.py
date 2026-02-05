from services.message_service.shared.ddb import ddb_table
from services.message_service.shared.time import epoch_seconds_plus_days
from services.message_service.shared.config import settings

class AuditRepository:
    def __init__(self):
        self.table = ddb_table("DDB_AUDIT_TABLE")

    def put_event(self, event_type, ref_id, from_user_id, to_user_id, created_at):
        self.table.put_item(
            Item={
                "pk": f"AUDIT#{to_user_id}",
                "sk": f"{created_at}#{ref_id}",
                "event_type": event_type,
                "ref_id": ref_id,
                "from_user_id": from_user_id,
                "to_user_id": to_user_id,
                "created_at": created_at,
                "expires_at": epoch_seconds_plus_days(settings.audit_ttl_days),
            }
        )
