FROM python:3.11-slim

WORKDIR /workspace/app

COPY requirements.txt /workspace/requirements.txt
RUN pip install --no-cache-dir -r /workspace/requirements.txt

COPY app /workspace/app

CMD ["python", "src/runtime/batch_runner.py", "--s3-silver-uri", "s3://silver-dummy/silver_events/", "--s3-daily-feature-uri", "s3://nyang-ml-apne2-dev/ml/daily-feature/", "--s3-baseline-uri", "s3://nyang-ml-apne2-dev/ml/baseline/", "--model-uri", "s3://nyang-ml-apne2-dev/ml/artifacts/models/isolation_forest.pkl", "--s3-output-uri", "s3://nyang-ml-apne2-dev/ml/outputs/"]
