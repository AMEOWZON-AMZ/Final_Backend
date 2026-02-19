from boto3.dynamodb.conditions import Key
from services.message_service.shared.ddb import ddb_table

class HeartRepository:
    def __init__(self):
        self.table = ddb_table("DDB_HEARTS_TABLE")

    def put_heart(self, heart_id, from_user_id, to_user_id, created_at):
        self.table.put_item(
            Item={
                "pk": f"RECEIVER#{to_user_id}",
                "sk": f"{created_at}#{heart_id}",
                "heart_id": heart_id,
                "from_user_id": from_user_id,
                "to_user_id": to_user_id,
                "created_at": created_at,
            }
        )

    def query_received(self, to_user_id, limit=20):
        resp = self.table.query(
            KeyConditionExpression=Key("pk").eq(f"RECEIVER#{to_user_id}"),
            ScanIndexForward=False,
            Limit=limit,
        )
        return resp.get("Items", [])
