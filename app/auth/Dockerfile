FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

COPY app/auth/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY app/__init__.py /app/app/__init__.py
COPY app/auth /app/app/auth
COPY app/auth/entrypoint.sh /entrypoint.sh

EXPOSE 8001

# Invoke via /bin/sh so a missing +x / shebang quirk cannot exit 255.
ENTRYPOINT ["/bin/sh", "/entrypoint.sh"]
