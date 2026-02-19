import os
from pathlib import Path

import boto3
from dotenv import load_dotenv


def required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing env var: {name}")
    return value


def main():
    base_dir = Path(__file__).resolve().parents[1]
    load_dotenv(base_dir / ".env")

    region = os.getenv("AWS_REGION", "ap-northeast-2")
    table_names = {
        "DDB_USER_STATUS_TABLE": required("DDB_USER_STATUS_TABLE"),
        "DDB_FRIENDS_TABLE": required("DDB_FRIENDS_TABLE"),
        "DDB_CRITICAL_CONTACTS_TABLE": required("DDB_CRITICAL_CONTACTS_TABLE"),
        "DDB_OUTBOX_TABLE": required("DDB_OUTBOX_TABLE"),
    }

    ddb = boto3.client("dynamodb", region_name=region)
    print(f"AWS_REGION={region}")
    for env_name, table_name in table_names.items():
        resp = ddb.describe_table(TableName=table_name)
        status = resp["Table"]["TableStatus"]
        print(f"{env_name}={table_name} (status={status})")

    print("DynamoDB connectivity check passed.")


if __name__ == "__main__":
    main()
