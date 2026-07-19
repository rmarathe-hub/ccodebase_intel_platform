#!/usr/bin/env bash
# Coverage suite with branch coverage for apps/api.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT/apps/api"
# shellcheck disable=SC1091
source .venv/bin/activate
export PYTHONPATH=.
pytest -q --cov=app --cov-branch --cov-report=term-missing --cov-report=xml:coverage.xml "$@"
