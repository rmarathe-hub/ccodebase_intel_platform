# Codebase Intelligence Platform

Local-first repository intelligence: import public GitHub repos, index them, search with hybrid retrieval, and answer with validated citations.

## Apps

- `apps/api` — FastAPI
- `apps/worker` — background worker (placeholder)
- `apps/web` — React + Vite UI

## Quick start (local)

```bash
make api-install
make web-install
cd apps/api && . .venv/bin/activate && uvicorn app.main:app --reload
# other terminal
cd apps/web && npm run dev
```

Docker Compose (`make dev`) wires postgres, api, worker, and web.

Postgres is published on host port **5434** (avoids clashing with a local Postgres on 5432).

## CI

GitHub Actions runs on every push/PR to `main`:

- Python: Ruff, MyPy, Pytest
- Frontend: TypeScript, ESLint, Vitest, production build
- Docker: builds api, worker, and web images

Locally: `make ci`
