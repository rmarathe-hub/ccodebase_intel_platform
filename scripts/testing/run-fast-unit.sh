#!/usr/bin/env bash
# Fast unit suite: no Postgres-dependent tests, no slow markers.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT/apps/api"
# shellcheck disable=SC1091
source .venv/bin/activate
export PYTHONPATH=.
pytest -q -m "not slow" \
  --ignore=tests/test_import_api.py \
  --ignore=tests/test_job_queue.py \
  --ignore=tests/test_job_queue_edges.py \
  --ignore=tests/test_concurrency_queue.py \
  --ignore=tests/test_db_constraints.py \
  --ignore=tests/test_import_service.py \
  --ignore=tests/test_api_contract_matrix.py \
  --ignore=tests/test_migrations_smoke.py \
  tests/test_github_url.py \
  tests/test_github_url_matrix.py \
  tests/test_git_clone.py \
  tests/test_snapshots.py \
  tests/test_settings.py \
  tests/test_job_model.py \
  tests/test_job_stages_matrix.py \
  tests/test_language_contract.py \
  tests/test_classification_matrix.py \
  tests/test_policy_docs.py \
  tests/test_config_matrix.py \
  tests/test_security_boundaries.py \
  tests/test_health.py \
  "$@"
