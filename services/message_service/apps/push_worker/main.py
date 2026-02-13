import time
from dotenv import load_dotenv
from pathlib import Path
from services.message_service.apps.push_worker.outbox.processor import process_outbox
from services.message_service.apps.push_worker.jobs.sqs_consumer import process_sqs

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

import os
print("AWS_REGION =", os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION"))
print("DDB_OUTBOX_TABLE =", os.getenv("DDB_OUTBOX_TABLE"))
print("DDB_ENDPOINT_URL =", os.getenv("DDB_ENDPOINT_URL"))

def run_loop():
    while True:
        # Prefer SQS if configured, otherwise poll Outbox
        did_work = process_sqs()
        if not did_work:
            process_outbox()
        time.sleep(1)


if __name__ == "__main__":
    run_loop()
