import time
from services.message_service.apps.push_worker.outbox.processor import process_outbox
from services.message_service.apps.push_worker.jobs.sqs_consumer import process_sqs


def run_loop():
    while True:
        # Prefer SQS if configured, otherwise poll Outbox
        did_work = process_sqs()
        if not did_work:
            process_outbox()
        time.sleep(1)


if __name__ == "__main__":
    run_loop()
