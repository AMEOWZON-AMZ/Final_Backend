import boto3
from boto3.dynamodb.types import TypeSerializer
from decimal import Decimal

from services.inference_service.app.core.config import settings

_serializer = TypeSerializer()


def ddb_table(table_name: str):
    resource = boto3.resource("dynamodb", region_name=settings.aws_region)
    return resource.Table(table_name)


def ddb_client():
    return boto3.client("dynamodb", region_name=settings.aws_region)


def _to_ddb_compatible(value):
    if isinstance(value, float):
        return Decimal(str(value))
    if isinstance(value, dict):
        return {k: _to_ddb_compatible(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_to_ddb_compatible(v) for v in value]
    return value


def serialize_item(item: dict) -> dict:
    normalized = _to_ddb_compatible(item)
    return {k: _serializer.serialize(v) for k, v in normalized.items()}
