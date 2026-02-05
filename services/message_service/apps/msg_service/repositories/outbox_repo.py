from boto3.dynamodb.conditions import Key
from services.message_service.shared.ddb import ddb_table

class OutboxRepository:
    def __init__(self):
        self.table = ddb_table("DDB_OUTBOX_TABLE")

    def put_event(self, event):
        self.table.put_item(Item=event.to_item())

    def query_pending(self, limit=10):
        resp = self.table.query(
            IndexName="status-index",
            KeyConditionExpression=Key("status").eq("PENDING"),
            Limit=limit,
        )
        return resp.get("Items", [])

    def update_status(self, pk, sk, status, retries, error=None):
        update = "SET #s = :s, retries = :r"
        values = {":s": status, ":r": retries}
        if error:
            update += ", last_error = :e"
            values[":e"] = error
        self.table.update_item(
            Key={"pk": pk, "sk": sk},
            UpdateExpression=update,
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues=values,
        )
