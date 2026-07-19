#!/usr/bin/env bash
# Full local suite (API + web). Requires Postgres on DATABASE_URL / defaults.
# API tests run serially by default; FULL_PARALLEL=1 uses xdist --dist loadgroup.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT/apps/api"
# shellcheck disable=SC1091
source .venv/bin/activate
export PYTHONPATH=.
echo "== API pytest (random order) =="
if [[ "${FULL_PARALLEL:-0}" == "1" ]]; then
  pytest -q -n auto --dist loadgroup --randomly-seed=auto "$@"
else
  pytest -q --randomly-seed=auto "$@"
fi
echo "== Web vitest =="
cd "$ROOT/apps/web"
npm test
