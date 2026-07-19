# Reproduction Guide — Week 0–4 Test Suite

## Prerequisites

```bash
cd /Users/rohitmarathe/codebase_intel_platform
make api-install
make web-install
docker compose up -d postgres
# wait until healthy, then:
make migrate
```

Postgres must be on host port **5434**:

`postgresql+psycopg://codeintel:codeintel@localhost:5434/codeintel`

## Fast paths

```bash
chmod +x scripts/testing/*.sh
./scripts/testing/run-fast-unit.sh
./scripts/testing/run-parser.sh
./scripts/testing/run-security.sh
./scripts/testing/run-integration.sh
./scripts/testing/run-worker-integration.sh
./scripts/testing/run-frontend-full.sh
./scripts/testing/run-coverage.sh
./scripts/testing/run-full.sh
./scripts/testing/run-slow.sh
```

## Manual equivalents

```bash
# API full serial, two seeds (flakiness check)
cd apps/api
.venv/bin/python -m pytest -q --randomly-seed=4242
.venv/bin/python -m pytest -q --randomly-seed=9001

# Coverage + HTML
.venv/bin/python -m pytest -q --cov=app --cov-branch \
  --cov-report=term-missing --cov-report=html:htmlcov

# Static
.venv/bin/ruff check .
.venv/bin/mypy app

# Frontend
cd ../web
npm run typecheck && npm run lint && npm test && npm run build
```

## CI parity

Push/PR to `main` runs `.github/workflows/ci.yml`:

1. API job with pgvector service on 5434 → alembic upgrade → ruff → mypy → pytest
2. Web typecheck/lint/test/build
3. Docker image builds for api/worker/web

## Git

You perform all `git add` / `commit` / `push` manually. Agents must not modify git history.
