FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# 서비스 코드 복사
COPY services/message_service /app/services/message_service

# 파이썬 모듈 경로
ENV PYTHONPATH=/app

# 의존성 설치 (message_service 기준 requirements.txt 위치에 맞춰)
RUN pip install --no-cache-dir -r /app/services/message_service/requirements.txt

# msg_service 실행 (경로는 너가 기존에 쓰던 uvicorn 경로로 조정)
CMD ["uvicorn", "services.message_service.apps.msg_service.main:app", "--host", "0.0.0.0", "--port", "8080"]
