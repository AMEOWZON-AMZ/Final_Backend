import os
import boto3
from boto3.dynamodb.types import TypeSerializer
from services.message_service.shared.config import settings

_serializer = TypeSerializer()


# env에서 DynamoDB 테이블명을 읽고 없으면 예외 발생.
def ddb_table_name(env_name: str) -> str:
    table_name = os.getenv(env_name)
    if not table_name:
        raise RuntimeError(f"Missing env var: {env_name}")
    return table_name


# 설정된 리전으로 DynamoDB Table 리소스 반환.
def ddb_table(env_name: str):
    table_name = ddb_table_name(env_name)
    resource = boto3.resource("dynamodb", region_name=settings.aws_region)
    return resource.Table(table_name)


# TransactWriteItems 등에 쓰는 low-level DynamoDB client 반환.
def ddb_client():
    return boto3.client("dynamodb", region_name=settings.aws_region)


# Python dict를 DynamoDB attribute 값으로 직렬화.
def serialize_item(item: dict) -> dict:
    return {k: _serializer.serialize(v) for k, v in item.items()}
