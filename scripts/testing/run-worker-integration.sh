#!/usr/bin/env bash
# Worker pipeline + Week 3–4 API filter / persist integration (requires Postgres :5434).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT/apps/api"
# shellcheck disable=SC1091
source .venv/bin/activate
export PYTHONPATH=.
pytest -q \
  tests/test_worker_pipeline.py \
  tests/test_api_filters_week04.py \
  tests/test_symbols_api.py \
  tests/test_calls_api.py \
  tests/test_symbol_neighbors_api.py \
  tests/test_source_files_persist.py \
  tests/test_symbols_persist.py \
  tests/test_migrations_week04.py \
  "$@"
