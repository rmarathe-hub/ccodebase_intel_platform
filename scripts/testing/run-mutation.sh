#!/usr/bin/env bash
# Focused mutation testing on pure URL + language contract modules.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT/apps/api"
# shellcheck disable=SC1091
source .venv/bin/activate
export PYTHONPATH=.
echo "Running mutmut (focused subset; may take several minutes)..."
# mutmut 3.x reads [tool.mutmut] from pyproject.toml
mutmut run || true
echo "--- mutmut results ---"
mutmut results || true
