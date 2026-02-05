from services.message_service.shared.ddb import ddb_table

class DeviceTokenRepository:
    def __init__(self):
        self.table = ddb_table("DDB_DEVICE_TOKENS_TABLE")

    def put_token(self, user_id, token, platform, updated_at):
        self.table.put_item(
            Item={
                "pk": f"USER#{user_id}",
                "sk": "TOKEN",
                "user_id": user_id,
                "token": token,
                "platform": platform,
                "updated_at": updated_at,
            }
        )

    def get_token(self, user_id):
        resp = self.table.get_item(Key={"pk": f"USER#{user_id}", "sk": "TOKEN"})
        return resp.get("Item")
