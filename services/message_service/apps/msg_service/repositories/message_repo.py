from boto3.dynamodb.conditions import Key
from services.message_service.shared.ddb import ddb_table, ddb_client, ddb_table_name, serialize_item

class MessageRepository:
    def __init__(self):
        self.table = ddb_table("DDB_MESSAGES_TABLE")

    # def put_message(self, message_id, from_user_id, to_user_id, body, created_at):
    #     self.table.put_item(
    #         Item={
    #             "pk": f"RECEIVER#{to_user_id}",
    #             "sk": f"{created_at}#{message_id}",
    #             "message_id": message_id,
    #             "from_user_id": from_user_id,
    #             "to_user_id": to_user_id,
    #             "body": body,
    #             "created_at": created_at,
    #         }
    #     )

    def build_message_item(self, message_id, from_user_id, to_user_id, body, created_at):
        return {
            "pk": f"RECEIVER#{to_user_id}",
            "sk": f"{created_at}#{message_id}",
            "message_id": message_id,
            "from_user_id": from_user_id,
            "to_user_id": to_user_id,
            "body": body,
            "created_at": created_at,
        }

    def put_message_with_outbox(self, message_item: dict, outbox_item: dict):
        client = ddb_client()
        client.transact_write_items(
            TransactItems=[
                {
                    "Put": {
                        "TableName": ddb_table_name("DDB_MESSAGES_TABLE"),
                        "Item": serialize_item(message_item),
                        "ConditionExpression": "attribute_not_exists(pk) AND attribute_not_exists(sk)",
                    }
                },
                {
                    "Put": {
                        "TableName": ddb_table_name("DDB_OUTBOX_TABLE"),
                        "Item": serialize_item(outbox_item),
                        "ConditionExpression": "attribute_not_exists(pk) AND attribute_not_exists(sk)",
                    }
                },
            ]
        )

    def query_inbox(self, to_user_id, limit=20):
        resp = self.table.query(
            KeyConditionExpression=Key("pk").eq(f"RECEIVER#{to_user_id}"),
            ScanIndexForward=False,
            Limit=limit,
        )
        return resp.get("Items", [])
