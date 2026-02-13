from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from services.message_service.shared.ddb import ddb_table
from services.message_service.shared.time import now_utc_iso


class OutboxRepository:
    def __init__(self):
        self.table = ddb_table("DDB_OUTBOX_TABLE")

    def put_event(self, event):
        self.table.put_item(Item=event.to_item())

    def get_event(self, event_id: str):
        resp = self.table.get_item(Key={"pk": f"EVENT#{event_id}", "sk": "EVENT"})
        return resp.get("Item")

    def query_ready(self, limit=10, now_iso=None):
        now_iso = now_iso or now_utc_iso()
        items = []
        items.extend(self._query_status("PENDING", limit, now_iso))
        if len(items) < limit:
            items.extend(self._query_status("RETRY", limit - len(items), now_iso))
        return items

    def _query_status(self, status, limit, now_iso):
        resp = self.table.query(
            IndexName="status-index",
            KeyConditionExpression=Key("status").eq(status),
            FilterExpression=Attr("next_retry_at").not_exists() | Attr("next_retry_at").lte(now_iso),
            Limit=limit,
        )
        return resp.get("Items", [])

    def try_mark_processing(self, event_id: str, now_iso: str) -> bool:
        try:
            self.table.update_item(
                Key={"pk": f"EVENT#{event_id}", "sk": "EVENT"},
                UpdateExpression="SET #s = :processing, processing_at = :now",
                ConditionExpression="(#s = :pending OR #s = :retry) AND (attribute_not_exists(next_retry_at) OR next_retry_at <= :now)",
                ExpressionAttributeNames={"#s": "status"},
                ExpressionAttributeValues={
                    ":processing": "PROCESSING",
                    ":pending": "PENDING",
                    ":retry": "RETRY",
                    ":now": now_iso,
                },
            )
            return True
        except ClientError as exc:
            if exc.response["Error"]["Code"] == "ConditionalCheckFailedException":
                return False
            raise

    def mark_sent(self, event_id: str, now_iso: str) -> bool:
        try:
            self.table.update_item(
                Key={"pk": f"EVENT#{event_id}", "sk": "EVENT"},
                UpdateExpression="SET #s = :sent, sent_at = :now",
                ConditionExpression="#s = :processing",
                ExpressionAttributeNames={"#s": "status"},
                ExpressionAttributeValues={
                    ":sent": "SENT",
                    ":processing": "PROCESSING",
                    ":now": now_iso,
                },
            )
            return True
        except ClientError as exc:
            if exc.response["Error"]["Code"] == "ConditionalCheckFailedException":
                return False
            raise

    def mark_retry(self, event_id: str, attempt_count: int, next_retry_at: str, last_error: str | None):
        now_iso = now_utc_iso()
        update = "SET #s = :retry, attempt_count = :a, next_retry_at = :n, updated_at = :u"
        values = {
            ":retry": "RETRY",
            ":a": attempt_count,
            ":n": next_retry_at,
            ":u": now_iso,
            ":processing": "PROCESSING",
        }
        if last_error:
            update += ", last_error = :e"
            values[":e"] = last_error

        try:
            self.table.update_item(
                Key={"pk": f"EVENT#{event_id}", "sk": "EVENT"},
                UpdateExpression=update,
                ConditionExpression="#s = :processing",
                ExpressionAttributeNames={"#s": "status"},
                ExpressionAttributeValues=values,
            )
            return True
        except ClientError as exc:
            if exc.response["Error"]["Code"] == "ConditionalCheckFailedException":
                return False
            raise

    def mark_failed(self, event_id: str, attempt_count: int, last_error: str | None):
        now_iso = now_utc_iso()
        update = "SET #s = :failed, attempt_count = :a, updated_at = :u"
        values = {
            ":failed": "FAILED",
            ":a": attempt_count,
            ":u": now_iso,
            ":processing": "PROCESSING",
        }
        if last_error:
            update += ", last_error = :e"
            values[":e"] = last_error

        try:
            self.table.update_item(
                Key={"pk": f"EVENT#{event_id}", "sk": "EVENT"},
                UpdateExpression=update,
                ConditionExpression="#s = :processing",
                ExpressionAttributeNames={"#s": "status"},
                ExpressionAttributeValues=values,
            )
            return True
        except ClientError as exc:
            if exc.response["Error"]["Code"] == "ConditionalCheckFailedException":
                return False
            raise
