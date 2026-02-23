from services.inference_service.app.core.config import settings
from services.inference_service.app.shared.ddb import ddb_table


class OutboxRepository:
    def __init__(self):
        self.table = ddb_table(settings.required("DDB_OUTBOX_TABLE"))

    def put_event(self, item: dict) -> None:
        self.table.put_item(Item=item)
