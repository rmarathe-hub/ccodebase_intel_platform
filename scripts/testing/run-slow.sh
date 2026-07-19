#!/usr/bin/env bash
# Slow / performance smoke suite.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT/apps/api"
# shellcheck disable=SC1091
source .venv/bin/activate
export PYTHONPATH=.
pytest -q -m slow tests/test_performance_smoke.py "$@"
