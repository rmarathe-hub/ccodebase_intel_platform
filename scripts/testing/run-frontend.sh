#!/usr/bin/env bash
# Frontend unit/component suite.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT/apps/web"
npm test "$@"
