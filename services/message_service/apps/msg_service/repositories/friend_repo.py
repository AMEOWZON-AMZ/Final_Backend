import os
from boto3.dynamodb.conditions import Attr, Key
from services.message_service.shared.ddb import ddb_table
from botocore.exceptions import ClientError

class FriendRepository:
    def __init__(self):
        self.table = ddb_table("DDB_FRIENDS_TABLE")

    def is_accepted(self, user_id, friend_id):
        resp = self.table.get_item(
            Key={"pk": f"USER#{user_id}", "sk": f"FRIEND#{friend_id}"}
        )
        item = resp.get("Item")
        return bool(item and item.get("status") == "ACCEPTED")

    def get_friend_nickname(self, user_id: str, friend_user_id: str) -> str | None:
        if not user_id or not friend_user_id:
            return None

        # Primary schema used by user_friends table: (user_id, friend_user_id)
        try:
            resp = self.table.get_item(Key={"user_id": user_id, "friend_user_id": friend_user_id})
            item = resp.get("Item")
            nickname = item.get("nickname") if item else None
            if isinstance(nickname, str) and nickname.strip():
                return nickname.strip()
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code")
            if code != "ValidationException":
                raise

        # Backward-compatible fallback schema: (pk, sk)
        try:
            resp = self.table.get_item(
                Key={"pk": f"USER#{user_id}", "sk": f"FRIEND#{friend_user_id}"}
            )
            item = resp.get("Item")
            nickname = item.get("nickname") if item else None
            if isinstance(nickname, str) and nickname.strip():
                return nickname.strip()
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code")
            if code != "ValidationException":
                raise

        return None

    def get_nickname_by_friend_user_id(self, friend_user_id: str) -> str | None:
        if not friend_user_id:
            return None

        index_name = os.getenv("DDB_USER_FRIENDS_GSI", "GSI1")
        try:
            resp = self.table.query(
                IndexName=index_name,
                KeyConditionExpression=Key("friend_user_id").eq(friend_user_id),
                Limit=1,
            )
            items = resp.get("Items", [])
            if items:
                nickname = items[0].get("nickname")
                if isinstance(nickname, str) and nickname.strip():
                    return nickname.strip()
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code")
            if code != "ValidationException":
                raise

        # Fallback when GSI is not configured in this environment.
        try:
            resp = self.table.scan(
                FilterExpression=Attr("friend_user_id").eq(friend_user_id),
                Limit=1,
            )
            items = resp.get("Items", [])
            if items:
                nickname = items[0].get("nickname")
                if isinstance(nickname, str) and nickname.strip():
                    return nickname.strip()
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code")
            if code != "ValidationException":
                raise

        return None
