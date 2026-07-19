.PHONY: help dev stop test lint migrate reset-db api-install web-install

help:
	@echo "Targets: dev stop test lint migrate reset-db api-install web-install"

dev:
	docker compose up --build

stop:
	docker compose down

test:
	cd apps/api && python -m pytest
	cd apps/web && npm test --if-present

lint:
	cd apps/api && ruff check . && mypy app
	cd apps/web && npm run lint

migrate:
	cd apps/api && alembic upgrade head

reset-db:
	docker compose down -v
	docker compose up -d postgres
	@echo "Waiting for postgres..."
	@sleep 3
	$(MAKE) migrate

api-install:
	cd apps/api && python -m venv .venv && . .venv/bin/activate && pip install -e ".[dev]"

web-install:
	cd apps/web && npm install
