import os
import boto3
from boto3.dynamodb.types import TypeSerializer
from services.message_service.shared.config import settings

_serializer = TypeSerializer()


def ddb_table_name(env_name: str) -> str:
    table_name = os.getenv(env_name)
    if not table_name:
        raise RuntimeError(f"Missing env var: {env_name}")
    return table_name


def ddb_table(env_name: str):
    table_name = ddb_table_name(env_name)
    resource = boto3.resource("dynamodb", region_name=settings.aws_region)
    return resource.Table(table_name)


def ddb_client():
    return boto3.client("dynamodb", region_name=settings.aws_region)


def serialize_item(item: dict) -> dict:
    return {k: _serializer.serialize(v) for k, v in item.items()}
