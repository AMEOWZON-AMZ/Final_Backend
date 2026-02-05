import os
import boto3
from services.message_service.shared.config import settings


def ddb_table(env_name: str):
    table_name = os.getenv(env_name)
    if not table_name:
        raise RuntimeError(f"Missing env var: {env_name}")
    resource = boto3.resource("dynamodb", region_name=settings.aws_region)
    return resource.Table(table_name)
