FROM python:3.11-slim

WORKDIR /app

COPY services/inference_service/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

EXPOSE 8080

CMD ["uvicorn", "services.inference_service.app.main:app", "--host", "0.0.0.0", "--port", "8080"]
