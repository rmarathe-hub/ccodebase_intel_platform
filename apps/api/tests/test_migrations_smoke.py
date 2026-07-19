"""Alembic migration smoke tests against isolated Postgres schema checks."""

from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import create_engine, inspect, text

from app.core.config import settings
from tests.conftest import postgres_available, requires_postgres

ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "alembic" / "versions" / "0001_initial_schema.py"

pytestmark = requires_postgres


def test_migration_file_exists_and_mentions_core_tables() -> None:
    text_body = MIGRATION.read_text(encoding="utf-8")
    for table in ("users", "repositories", "repository_snapshots", "indexing_jobs"):
        assert table in text_body
    assert "CREATE EXTENSION IF NOT EXISTS vector" in text_body


def test_live_schema_has_expected_tables_and_columns() -> None:
    if not postgres_available():
        pytest.skip("PostgreSQL required")
    engine = create_engine(settings.database_url, pool_pre_ping=True)
    insp = inspect(engine)
    tables = set(insp.get_table_names())
    for table in ("users", "repositories", "repository_snapshots", "indexing_jobs"):
        assert table in tables

    job_cols = {col["name"] for col in insp.get_columns("indexing_jobs")}
    for required in (
        "status",
        "stage",
        "progress_percentage",
        "attempt_count",
        "max_attempts",
        "locked_by",
        "locked_until",
        "heartbeat_at",
        "error_code",
        "error_message",
        "started_at",
        "completed_at",
        "snapshot_id",
        "repository_id",
    ):
        assert required in job_cols

    snap_cols = {col["name"] for col in insp.get_columns("repository_snapshots")}
    for required in ("repository_id", "branch", "commit_sha", "file_count", "status", "created_at"):
        assert required in snap_cols

    with engine.connect() as conn:
        ext = conn.execute(text("SELECT extname FROM pg_extension WHERE extname='vector'")).scalar()
        assert ext == "vector"
    engine.dispose()
