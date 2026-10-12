#!/bin/sh
set -eu

echo "Starting users entrypoint..."
echo "Database URL host check: $(echo "${USERS_DATABASE_URL:-}" | sed -E 's|.*@([^/]+)/.*|\1|')"

if [ -z "${USERS_DATABASE_URL:-}" ]; then
  echo "ERROR: USERS_DATABASE_URL is not set" >&2
  exit 1
fi

echo "Running users database migrations..."
python -m alembic -c /app/app/users/alembic.ini upgrade head

echo "Starting users service on ${USERS_HOST:-0.0.0.0}:${USERS_PORT:-8002}..."
exec python -m uvicorn app.users.main:app \
  --host "${USERS_HOST:-0.0.0.0}" \
  --port "${USERS_PORT:-8002}"
