from boto3.dynamodb.conditions import Key
from services.message_service.shared.ddb import ddb_table

class MessageRepository:
    def __init__(self):
        self.table = ddb_table("DDB_MESSAGES_TABLE")

    def put_message(self, message_id, from_user_id, to_user_id, body, created_at):
        self.table.put_item(
            Item={
                "pk": f"RECEIVER#{to_user_id}",
                "sk": f"{created_at}#{message_id}",
                "message_id": message_id,
                "from_user_id": from_user_id,
                "to_user_id": to_user_id,
                "body": body,
                "created_at": created_at,
            }
        )

    def query_inbox(self, to_user_id, limit=20):
        resp = self.table.query(
            KeyConditionExpression=Key("pk").eq(f"RECEIVER#{to_user_id}"),
            ScanIndexForward=False,
            Limit=limit,
        )
        return resp.get("Items", [])
