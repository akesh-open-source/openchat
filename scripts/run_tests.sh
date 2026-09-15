#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

python -m pytest \
  app/auth/tests/unit \
  app/auth/tests/integration \
  app/gateway/tests/unit \
  app/gateway/tests/integration \
  app/users/tests/unit \
  app/users/tests/integration \
  app/messaging/tests/unit \
  "$@"
