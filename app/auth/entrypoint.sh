#!/bin/sh
set -eu

echo "Starting auth entrypoint..."
echo "Database URL host check: $(echo "${AUTH_DATABASE_URL:-}" | sed -E 's|.*@([^/]+)/.*|\1|')"

if [ -z "${AUTH_DATABASE_URL:-}" ]; then
  echo "ERROR: AUTH_DATABASE_URL is not set" >&2
  exit 1
fi

echo "Running auth database migrations..."
python -m alembic -c /app/app/auth/alembic.ini upgrade head

echo "Starting auth service on ${AUTH_HOST:-0.0.0.0}:${AUTH_PORT:-8001}..."
exec python -m uvicorn app.auth.main:app \
  --host "${AUTH_HOST:-0.0.0.0}" \
  --port "${AUTH_PORT:-8001}"
