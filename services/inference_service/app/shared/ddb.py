import boto3
from boto3.dynamodb.types import TypeSerializer

from services.inference_service.app.core.config import settings

_serializer = TypeSerializer()


def ddb_table(table_name: str):
    resource = boto3.resource("dynamodb", region_name=settings.aws_region)
    return resource.Table(table_name)


def ddb_client():
    return boto3.client("dynamodb", region_name=settings.aws_region)


def serialize_item(item: dict) -> dict:
    return {k: _serializer.serialize(v) for k, v in item.items()}
