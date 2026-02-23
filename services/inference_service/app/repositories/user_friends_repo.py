from boto3.dynamodb.conditions import Key

from services.inference_service.app.core.config import settings
from services.inference_service.app.shared.ddb import ddb_table


class UserFriendsRepository:
    # user_friends 테이블과 fanout 조회용 GSI 이름을 초기화한다.
    def __init__(self):
        self.table = ddb_table(settings.required("DDB_FRIENDS_TABLE"))
        self.index_name = settings.user_friends_gsi

    # GSI(friend_user_id)로 대상 사용자 상태를 봐야 하는 친구 행들을 페이지 단위 조회한다.
    def query_by_friend_user_id(self, friend_user_id: str, limit: int = 100, last_key: dict | None = None):
        params: dict = {
            "IndexName": self.index_name,
            "KeyConditionExpression": Key("friend_user_id").eq(friend_user_id),
            "Limit": limit,
        }
        if last_key:
            params["ExclusiveStartKey"] = last_key
        return self.table.query(**params)

    # 친구 캐시 행의 일일 상태와 갱신 시각을 업데이트한다.
    def update_daily_status(self, user_id: str, friend_user_id: str, daily_status: str, updated_at: str) -> None:
        self.table.update_item(
            Key={"user_id": user_id, "friend_user_id": friend_user_id},
            UpdateExpression="SET daily_status = :daily_status, updated_at = :updated_at",
            ExpressionAttributeValues={
                ":daily_status": daily_status,
                ":updated_at": updated_at,
            },
        )
