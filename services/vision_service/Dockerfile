FROM python:3.11-slim

ENV PORT=8080
WORKDIR /app

COPY services/vision_service/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY services/vision_service /app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
