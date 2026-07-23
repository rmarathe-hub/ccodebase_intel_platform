#!/usr/bin/env bash
# Run the indexing worker with auto-restart on Python changes.
# Prevents the common footgun: API --reload picks up chunking changes while
# a long-lived `python -m worker` keeps serving stale code.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="${ROOT}/apps/api:${ROOT}/apps/worker${PYTHONPATH:+:$PYTHONPATH}"
PY="${ROOT}/apps/api/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  PY="python3"
fi

if "$PY" -c "import watchfiles" 2>/dev/null; then
  exec "$PY" -m watchfiles \
    --filter python \
    "$PY -m worker" \
    apps/api/app \
    apps/worker/worker
fi

echo "watchfiles not installed — running worker without auto-restart." >&2
echo "Install with: apps/api/.venv/bin/pip install 'watchfiles>=0.24'" >&2
echo "Or: make worker-watch (after api-install with [dev])." >&2
exec "$PY" -m worker
