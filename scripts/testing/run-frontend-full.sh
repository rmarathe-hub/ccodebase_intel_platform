#!/usr/bin/env bash
# Frontend: typecheck + lint + vitest + production build.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT/apps/web"
npm run typecheck
npm run lint
npm test
npm run build
