from botocore.exceptions import ClientError

from services.inference_service.app.core.config import settings
from services.inference_service.app.shared.ddb import ddb_client, serialize_item


class CriticalEventTransactionRepository:
    # critical 처리에 필요한 테이블 이름과 DynamoDB client를 초기화한다.
    def __init__(self):
        self.client = ddb_client()
        self.user_status_table = settings.required("DDB_USER_STATUS_TABLE")
        self.critical_contacts_table = settings.required("DDB_CRITICAL_CONTACTS_TABLE")
        self.outbox_table = settings.required("DDB_OUTBOX_TABLE")

    # critical 상태 반영 + snapshot 저장 + outbox 적재를 트랜잭션으로 1회 처리한다.
    def apply_once(
        self,
        critical_user_id: str,
        source_event_id: str,
        critical_gps,
        friends: list[dict],
        created_at: str,
        ttl: int,
        outbox_event_id: str,
        outbox_dedupe_key: str,
        outbox_payload: dict,
    ) -> bool:
        critical_contacts_item = {
            "critical_user_id": critical_user_id,
            "event_id": source_event_id,
            "critical_gps": critical_gps,
            "friends": friends,
            "created_at": created_at,
            "ttl": ttl,
        }
        outbox_item = {
            "pk": f"EVENT#{outbox_event_id}",
            "sk": "EVENT",
            "event_id": outbox_event_id,
            "event_type": "CRITICAL_ALERT",
            "dedupe_key": outbox_dedupe_key,
            "status": "PENDING",
            "attempt_count": 0,
            "next_retry_at": created_at,
            "created_at": created_at,
            "payload": outbox_payload,
            "last_error": None,
        }

        try:
            self.client.transact_write_items(
                TransactItems=[
                    {
                        "Update": {
                            "TableName": self.user_status_table,
                            "Key": serialize_item({"user_id": critical_user_id}),
                            "UpdateExpression": (
                                "SET is_critical = :true, "
                                "critical_since = :critical_since, "
                                "updated_at = :updated_at, "
                                "current_daily_status = :critical_status"
                            ),
                            "ConditionExpression": "attribute_not_exists(is_critical) OR is_critical = :false",
                            "ExpressionAttributeValues": serialize_item(
                                {
                                    ":true": True,
                                    ":false": False,
                                    ":critical_since": created_at,
                                    ":updated_at": created_at,
                                    ":critical_status": "CRITICAL",
                                }
                            ),
                        }
                    },
                    {
                        "Put": {
                            "TableName": self.critical_contacts_table,
                            "Item": serialize_item(critical_contacts_item),
                            "ConditionExpression": "attribute_not_exists(critical_user_id) AND attribute_not_exists(event_id)",
                        }
                    },
                    {
                        "Put": {
                            "TableName": self.outbox_table,
                            "Item": serialize_item(outbox_item),
                            "ConditionExpression": "attribute_not_exists(pk) AND attribute_not_exists(sk)",
                        }
                    },
                ]
            )
            return True
        except ClientError as exc:
            if exc.response["Error"]["Code"] == "TransactionCanceledException":
                return False
            raise
