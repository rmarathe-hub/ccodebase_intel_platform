#!/usr/bin/env bash
# Security / URL / cost-policy / discovery boundary tests.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT/apps/api"
# shellcheck disable=SC1091
source .venv/bin/activate
export PYTHONPATH=.
pytest -q \
  tests/test_github_url.py \
  tests/test_github_url_matrix.py \
  tests/test_github_url_security_extended.py \
  tests/test_security_boundaries.py \
  tests/test_doc_contracts_week04.py \
  tests/test_policy_docs.py \
  "$@"
