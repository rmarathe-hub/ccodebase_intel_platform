"""Migration / schema contract for Alembic 0001–0006 (Week 2–4)."""

from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import create_engine, inspect, text

from app.core.config import settings
from tests.conftest import postgres_available, requires_postgres

ROOT = Path(__file__).resolve().parents[1]
VERSIONS = ROOT / "alembic" / "versions"

pytestmark = requires_postgres

EXPECTED_REVISIONS = (
    "0001_initial_schema.py",
    "0002_source_files.py",
    "0003_symbols.py",
    "0004_symbol_metadata.py",
    "0005_framework_imports.py",
    "0006_symbol_calls.py",
    "0007_symbol_relations.py",
    "0008_chunks.py",
)


def test_all_migration_files_present() -> None:
    names = {p.name for p in VERSIONS.glob("*.py") if not p.name.startswith("__")}
    for expected in EXPECTED_REVISIONS:
        assert expected in names


def test_migration_chain_revision_ids() -> None:
    """Each file declares revises pointing at the previous revision id."""
    texts = {
        name: (VERSIONS / name).read_text(encoding="utf-8") for name in EXPECTED_REVISIONS
    }
    assert 'revision: str = "0001_initial_schema"' in texts["0001_initial_schema.py"]
    assert 'down_revision: str | None = "0001_initial_schema"' in texts["0002_source_files.py"]
    assert 'down_revision: str | None = "0002_source_files"' in texts["0003_symbols.py"]
    assert 'down_revision: str | None = "0003_symbols"' in texts["0004_symbol_metadata.py"]
    assert 'down_revision: str | None = "0004_symbol_metadata"' in texts[
        "0005_framework_imports.py"
    ]
    assert 'down_revision: str | None = "0005_framework_imports"' in texts[
        "0006_symbol_calls.py"
    ]
    assert 'down_revision: str | None = "0006_symbol_calls"' in texts[
        "0007_symbol_relations.py"
    ]
    assert 'down_revision: str | None = "0007_symbol_relations"' in texts["0008_chunks.py"]


def test_live_schema_has_week3_and_week4_tables() -> None:
    if not postgres_available():
        pytest.skip("PostgreSQL required")
    engine = create_engine(settings.database_url, pool_pre_ping=True)
    insp = inspect(engine)
    tables = set(insp.get_table_names())
    for table in (
        "users",
        "repositories",
        "repository_snapshots",
        "indexing_jobs",
        "source_files",
        "symbols",
        "symbol_calls",
        "symbol_relations",
        "chunks",
        "llm_enrichment_cache",
    ):
        assert table in tables

    source_cols = {c["name"] for c in insp.get_columns("source_files")}
    for required in (
        "path",
        "language",
        "support_level",
        "parser_name",
        "parser_version",
        "skip_reason",
        "is_test_file",
        "is_generated",
        "is_vendor",
        "is_binary",
    ):
        assert required in source_cols

    symbol_cols = {c["name"] for c in insp.get_columns("symbols")}
    for required in (
        "kind",
        "name",
        "qualified_name",
        "start_line",
        "end_line",
        "docstring",
        "decorators_json",
        "parameters_json",
        "return_annotation",
        "is_async",
        "framework_role",
        "framework_detail",
        "resolved_module",
        "import_style",
        "is_local_import",
        "import_alias",
    ):
        assert required in symbol_cols

    call_cols = {c["name"] for c in insp.get_columns("symbol_calls")}
    for required in (
        "caller_symbol_id",
        "caller_qualified_name",
        "raw_callee",
        "qualified_expression",
        "line",
        "candidate_qualified_name",
        "confidence",
        "language",
    ):
        assert required in call_cols

    relation_cols = {c["name"] for c in insp.get_columns("symbol_relations")}
    for required in (
        "from_symbol_id",
        "from_qualified_name",
        "relation_kind",
        "raw_target",
        "line",
        "candidate_qualified_name",
        "to_symbol_id",
        "confidence",
        "language",
    ):
        assert required in relation_cols

    with engine.connect() as conn:
        head = conn.execute(text("SELECT version_num FROM alembic_version")).scalar()
    assert head == "0008_chunks"
    engine.dispose()


def test_alembic_heads_cli_matches_0008() -> None:
    from alembic.config import Config
    from alembic.script import ScriptDirectory

    cfg = Config(str(ROOT / "alembic.ini"))
    script = ScriptDirectory.from_config(cfg)
    heads = script.get_heads()
    assert heads == ["0008_chunks"]
