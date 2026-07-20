"""Week 7 Days 3–4: configuration + Markdown AST chunking."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Chunk, Repository, SnapshotStatus
from app.services.chunking import replace_chunks_for_snapshot
from app.services.chunking.config_chunking import (
    chunk_configuration_file,
    chunk_dockerfile_source,
    chunk_json_source,
    chunk_toml_source,
    chunk_xml_source,
    chunk_yaml_source,
)
from app.services.chunking.markdown_chunks import chunk_markdown_source
from app.services.discovery import discover_repository
from app.services.snapshots import create_or_update_snapshot
from app.services.source_files import replace_source_files_for_snapshot
from tests.conftest import requires_postgres

pytestmark = requires_postgres

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "generic_polyglot"


def test_json_top_level_keys_offline() -> None:
    source = (FIXTURE / "package.json").read_text(encoding="utf-8")
    chunks = chunk_json_source(source=source, path="package.json")
    keys = {c.parent_context for c in chunks}
    assert "name" in keys
    assert "scripts" in keys
    assert "dependencies" in keys
    assert all(c.chunk_type == "configuration_section" for c in chunks)
    assert all(c.verified_deep is False for c in chunks)


def test_yaml_compose_services_offline() -> None:
    source = (FIXTURE / "docker-compose.yml").read_text(encoding="utf-8")
    chunks = chunk_yaml_source(source=source, path="docker-compose.yml")
    contexts = {c.parent_context for c in chunks}
    assert "services" in contexts
    assert "services.api" in contexts
    assert "services.db" in contexts
    assert "volumes" in contexts


def test_toml_cargo_sections_offline() -> None:
    source = (FIXTURE / "Cargo.toml").read_text(encoding="utf-8")
    chunks = chunk_toml_source(source=source, path="Cargo.toml")
    tables = {c.parent_context for c in chunks}
    assert "dependencies" in tables
    assert "dev-dependencies" in tables


def test_xml_maven_top_level_offline() -> None:
    source = (FIXTURE / "pom.xml").read_text(encoding="utf-8")
    chunks = chunk_xml_source(source=source, path="pom.xml")
    assert chunks
    names = {c.parent_context for c in chunks}
    assert "modelVersion" in names or "groupId" in names or "dependencies" in names
    assert all(c.parser_name == "defusedxml-sax" for c in chunks)


def test_dockerfile_stages_offline() -> None:
    source = (FIXTURE / "Dockerfile").read_text(encoding="utf-8")
    chunks = chunk_dockerfile_source(source=source, path="Dockerfile")
    assert len(chunks) >= 2
    names = {c.parent_context for c in chunks}
    assert "base" in names
    assert "runtime" in names


def test_markdown_ast_headings_ignore_fenced_fake() -> None:
    source = (FIXTURE / "docs/ARCHITECTURE.md").read_text(encoding="utf-8")
    chunks = chunk_markdown_source(source=source, path="docs/ARCHITECTURE.md")
    headings = [c.metadata_json or "" for c in chunks]
    assert any("Installation" in h for h in headings)
    assert any("Architecture" in h for h in headings)
    assert all("Not A Real Heading" not in (c.parent_context or "") for c in chunks)
    assert all(c.extraction_method == "markdown_ast" for c in chunks)
    assert all(c.chunk_type == "documentation_section" for c in chunks)


def test_config_router_by_filename() -> None:
    df = (FIXTURE / "Dockerfile").read_text(encoding="utf-8")
    assert chunk_configuration_file(source=df, path="Dockerfile")
    pkg = (FIXTURE / "package.json").read_text(encoding="utf-8")
    assert chunk_configuration_file(source=pkg, path="package.json")


def test_persist_config_and_docs_chunks(db_session: Session) -> None:
    repo = Repository(
        host="github.com",
        owner_name="rmarathe-hub",
        name=f"cfg-{uuid4().hex[:8]}",
        default_branch="main",
        clone_url="https://github.com/rmarathe-hub/retail-retention-revenue-intel.git",
    )
    db_session.add(repo)
    db_session.flush()
    snapshot = create_or_update_snapshot(
        db_session,
        repository_id=repo.id,
        branch="main",
        commit_sha=uuid4().hex[:12],
        file_count=0,
        status=SnapshotStatus.READY,
    )
    discovery = discover_repository(FIXTURE)
    replace_source_files_for_snapshot(
        db_session, snapshot_id=snapshot.id, discovery=discovery
    )
    db_session.flush()
    n, enriched = replace_chunks_for_snapshot(
        db_session, snapshot_id=snapshot.id, repo_root=FIXTURE
    )
    db_session.commit()
    assert n >= 10
    assert enriched == 0
    rows = list(
        db_session.scalars(select(Chunk).where(Chunk.snapshot_id == snapshot.id)).all()
    )
    assert any(r.chunk_type == "configuration_section" for r in rows)
    assert any(r.chunk_type == "documentation_section" for r in rows)
    assert any(r.path == "package.json" for r in rows)
    assert any(r.path.endswith("ARCHITECTURE.md") for r in rows)
    assert all(r.verified_deep is False for r in rows if r.language in {"configuration", "documentation"})
