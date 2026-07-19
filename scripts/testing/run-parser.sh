#!/usr/bin/env bash
# Parser / Week-4 Python deep unit tests (no Postgres required for most).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT/apps/api"
# shellcheck disable=SC1091
source .venv/bin/activate
export PYTHONPATH=.
pytest -q \
  tests/test_python_ast_parser.py \
  tests/test_python_ast_matrix.py \
  tests/test_python_framework_imports.py \
  tests/test_python_framework_matrix.py \
  tests/test_python_calls.py \
  tests/test_python_calls_matrix.py \
  tests/test_python_deep_fixtures.py \
  tests/test_js_ts_parser.py \
  tests/test_js_ts_module_framework.py \
  tests/test_js_ts_calls.py \
  tests/test_js_ts_deep_fixtures.py \
  tests/test_java_parser.py \
  tests/test_java_framework_inheritance.py \
  tests/test_java_architecture_calls.py \
  "$@"
