#!/bin/sh
set -eu

echo "Starting messaging entrypoint..."
echo "Database URL host check: $(echo "${MESSAGING_DATABASE_URL:-}" | sed -E 's|.*@([^/]+)/.*|\1|')"

if [ -z "${MESSAGING_DATABASE_URL:-}" ]; then
  echo "ERROR: MESSAGING_DATABASE_URL is not set" >&2
  exit 1
fi

echo "Running messaging database migrations..."
python -m alembic -c /app/app/messaging/alembic.ini upgrade head

echo "Starting messaging service on ${MESSAGING_HOST:-0.0.0.0}:${MESSAGING_PORT:-8003}..."
exec python -m uvicorn app.messaging.main:app \
  --host "${MESSAGING_HOST:-0.0.0.0}" \
  --port "${MESSAGING_PORT:-8003}"
