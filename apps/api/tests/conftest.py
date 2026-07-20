"""Shared pytest fixtures for API tests."""

from __future__ import annotations

from collections.abc import Generator

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.models import Base

_POSTGRES_NODE_HINTS = (
    "test_import_api",
    "test_api_contract_matrix",
    "test_job_queue",
    "test_concurrency_queue",
    "test_import_service",
    "test_db_constraints",
    "test_cors_and_errors",
    "test_models",
    "test_snapshots",
    "test_migrations_smoke",
    "test_job_queue_edges",
    "test_health",
    "test_coverage_edges",
    "test_source_files_persist",
    "test_files_api",
    "test_symbols_persist",
    "test_symbols_api",
    "test_calls_api",
    "test_symbol_neighbors_api",
    "test_api_filters_week04",
    "test_worker_pipeline",
    "test_migrations_week04",
    "test_embeddings_persist_week09",
    "test_java_symbols_persist",
  "test_mixed_frontend_backend",
)


def postgres_available() -> bool:
    engine = create_engine(settings.database_url, pool_pre_ping=True)
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
    finally:
        engine.dispose()


requires_postgres = pytest.mark.skipif(
    not postgres_available(),
    reason="PostgreSQL is required for this test",
)


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Serialize shared-Postgres modules under xdist (loadgroup)."""
    for item in items:
        if any(hint in item.nodeid for hint in _POSTGRES_NODE_HINTS):
            item.add_marker(pytest.mark.xdist_group("postgres"))


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    if not postgres_available():
        pytest.skip("PostgreSQL is required for this test")
    engine = create_engine(settings.database_url, pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        yield session
        session.rollback()
    finally:
        session.close()
        engine.dispose()
