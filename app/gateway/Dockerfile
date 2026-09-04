FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

COPY app/gateway/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY app/__init__.py /app/app/__init__.py
COPY app/gateway /app/app/gateway

EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.gateway.main:app --host ${GATEWAY_HOST:-0.0.0.0} --port ${GATEWAY_PORT:-8000}"]
