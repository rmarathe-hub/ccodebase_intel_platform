#!/usr/bin/env bash
# Integration suite: Postgres-backed API/job/import/migration tests.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT/apps/api"
# shellcheck disable=SC1091
source .venv/bin/activate
export PYTHONPATH=.
pytest -q \
  tests/test_import_api.py \
  tests/test_api_contract_matrix.py \
  tests/test_job_queue.py \
  tests/test_job_queue_edges.py \
  tests/test_concurrency_queue.py \
  tests/test_db_constraints.py \
  tests/test_import_service.py \
  tests/test_migrations_smoke.py \
  tests/test_models.py \
  tests/test_cors_and_errors.py \
  "$@"
