FROM python:3.11-slim

WORKDIR /app



RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*


ENV PYTHONPATH=/app

# Install dependencies if you have a requirements file for this service
COPY services/message_service/requirements.txt /app/services/message_service/requirements.txt
RUN pip install -r /app/services/message_service/requirements.txt

COPY services/message_service /app/services/message_service



CMD ["uvicorn", "services.message_service.apps.msg_service.main:app", "--host", "0.0.0.0", "--port", "8080"]
