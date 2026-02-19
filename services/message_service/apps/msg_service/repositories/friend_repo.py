from services.message_service.shared.ddb import ddb_table

class FriendRepository:
    def __init__(self):
        self.table = ddb_table("DDB_FRIENDS_TABLE")

    def is_accepted(self, user_id, friend_id):
        resp = self.table.get_item(
            Key={"pk": f"USER#{user_id}", "sk": f"FRIEND#{friend_id}"}
        )
        item = resp.get("Item")
        return bool(item and item.get("status") == "ACCEPTED")
