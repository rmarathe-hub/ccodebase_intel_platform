.PHONY: help dev stop test lint migrate reset-db api-install web-install ci docker-build worker worker-watch

help:
	@echo "Targets: dev stop test lint migrate reset-db api-install web-install ci docker-build worker worker-watch"

dev:
	docker compose up --build

stop:
	docker compose down

test:
	cd apps/api && .venv/bin/python -m pytest
	cd apps/web && npm test

lint:
	cd apps/api && .venv/bin/ruff check . && .venv/bin/mypy app
	cd apps/web && npm run lint && npm run typecheck

migrate:
	cd apps/api && .venv/bin/alembic upgrade head

reset-db:
	docker compose down -v
	docker compose up -d postgres
	@echo "Waiting for postgres..."
	@for i in 1 2 3 4 5 6 7 8 9 10; do \
		docker compose exec -T postgres pg_isready -U codeintel -d codeintel && break; \
		sleep 1; \
	done
	$(MAKE) migrate

api-install:
	cd apps/api && python3 -m venv .venv && . .venv/bin/activate && pip install -e ".[dev]"

web-install:
	cd apps/web && npm install

# Long-lived worker WITHOUT reload (production-like). Prefer worker-watch locally.
worker:
	PYTHONPATH=apps/api:apps/worker apps/api/.venv/bin/python -m worker

# Auto-restarts worker when apps/api or apps/worker Python changes.
worker-watch:
	chmod +x scripts/dev-worker.sh
	./scripts/dev-worker.sh

docker-build:
	docker build -f apps/api/Dockerfile -t codeintel-api:local .
	docker build -f apps/worker/Dockerfile -t codeintel-worker:local .
	docker build -f apps/web/Dockerfile -t codeintel-web:local .

ci: lint test docker-build
	@echo "CI checks passed."
