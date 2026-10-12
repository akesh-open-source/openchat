FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

COPY app/messaging/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY app/__init__.py /app/app/__init__.py
COPY app/messaging /app/app/messaging
COPY app/messaging/entrypoint.sh /entrypoint.sh

EXPOSE 8003

# Invoke via /bin/sh so a missing +x / shebang quirk cannot exit 255.
ENTRYPOINT ["/bin/sh", "/entrypoint.sh"]
