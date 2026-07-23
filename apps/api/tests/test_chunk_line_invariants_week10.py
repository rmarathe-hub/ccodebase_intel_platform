"""Line-range and whole-file fallback invariants for config/source chunking."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Chunk, Repository, SnapshotStatus
from app.services.chunking import replace_chunks_for_snapshot
from app.services.chunking.config_chunking import (
    chunk_configuration_file,
    chunk_json_source,
    chunk_yaml_source,
    physical_line_count,
)
from app.services.discovery import discover_repository
from app.services.js_ts_symbols import replace_js_ts_symbols_for_snapshot
from app.services.snapshots import create_or_update_snapshot
from app.services.source_files import replace_source_files_for_snapshot
from tests.conftest import requires_postgres

pytestmark = requires_postgres


def test_json_opening_brace_is_line_one() -> None:
    source = '{\n  "name": "demo",\n  "private": true\n}\n'
    chunks = chunk_json_source(source=source, path="package.json")
    assert chunks
    assert min(c.start_line for c in chunks) == 1
    assert max(c.end_line for c in chunks) == physical_line_count(source)
    joined = "\n".join(
        c.content
        for c in sorted(chunks, key=lambda x: (x.start_line, x.end_line))
    )
    assert "{" in joined.splitlines()[0] or joined.lstrip().startswith("{")
    first = next(c for c in chunks if c.start_line == 1)
    assert first.content.splitlines()[0].strip() == "{"


def test_yaml_name_key_starts_at_line_one() -> None:
    source = "name: Deploy\non:\n  push:\n    branches: [main]\n"
    chunks = chunk_yaml_source(source=source, path=".github/workflows/x.yml")
    assert chunks
    assert min(c.start_line for c in chunks) == 1
    assert any(c.content.lstrip().startswith("name:") for c in chunks)


def test_typescript_config_import_line_preserved() -> None:
    source = (
        'import { defineConfig } from "vite";\n'
        "\n"
        "export default defineConfig({\n"
        '  base: "/",\n'
        "});\n"
    )
    # Unknown config suffix falls through to whole-file fallback.
    chunks = chunk_configuration_file(source=source, path="vite.config.ts")
    assert len(chunks) == 1
    assert chunks[0].start_line == 1
    assert chunks[0].content.startswith("import")
    assert "defineConfig" in chunks[0].content


def test_blank_first_line_json_still_covers_line_one() -> None:
    source = '\n{\n  "name": "x"\n}\n'
    chunks = chunk_json_source(source=source, path="package.json")
    assert min(c.start_line for c in chunks) == 1
    first = next(c for c in chunks if c.start_line == 1)
    assert first.content.splitlines()[0] == ""


def test_one_line_json() -> None:
    source = '{"a":1}'
    chunks = chunk_json_source(source=source, path="package.json")
    assert len(chunks) == 1
    assert chunks[0].start_line == 1
    assert chunks[0].end_line == 1
    assert chunks[0].content == '{"a":1}'


def test_no_trailing_newline_json() -> None:
    source = '{\n  "a": 1\n}'
    chunks = chunk_json_source(source=source, path="package.json")
    assert min(c.start_line for c in chunks) == 1
    assert max(c.end_line for c in chunks) == 3
    assert physical_line_count(source) == 3


def test_config_whole_file_fallback_when_parser_empty() -> None:
    source = "not: valid: yaml: [[[\n"
    chunks = chunk_configuration_file(source=source, path="broken.yaml")
    assert len(chunks) == 1
    assert chunks[0].start_line == 1
    assert chunks[0].parent_context == "__file__"


def test_deep_vite_config_gets_whole_file_chunk(db_session: Session, tmp_path: Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    vite = (
        'import { defineConfig } from "vite";\n'
        "\n"
        "export default defineConfig({\n"
        '  base: "/",\n'
        "  server: {\n"
        "    port: 5173,\n"
        "  },\n"
        "});\n"
    )
    (root / "vite.config.ts").write_text(vite, encoding="utf-8")
    (root / "package.json").write_text('{"name":"t"}\n', encoding="utf-8")

    repo = Repository(
        host="github.com",
        owner_name="t",
        name=f"vite-fallback-{uuid4().hex[:8]}",
        default_branch="main",
        clone_url="https://github.com/t/vite-fallback.git",
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
    discovery = discover_repository(root)
    replace_source_files_for_snapshot(
        db_session, snapshot_id=snapshot.id, discovery=discovery
    )
    db_session.flush()
    replace_js_ts_symbols_for_snapshot(
        db_session, snapshot_id=snapshot.id, repo_root=root
    )
    db_session.flush()
    n, _ = replace_chunks_for_snapshot(
        db_session, snapshot_id=snapshot.id, repo_root=root
    )
    db_session.commit()
    assert n >= 1
    rows = list(
        db_session.scalars(
            select(Chunk).where(
                Chunk.snapshot_id == snapshot.id,
                Chunk.path == "vite.config.ts",
            )
        ).all()
    )
    assert rows
    assert min(r.start_line for r in rows) == 1
    assert max(r.end_line for r in rows) == 8
    assert any(
        r.extraction_method in {"deep_file_fallback", "whole_file_fallback"}
        or r.chunk_type == "file"
        for r in rows
    )
    assert "defineConfig" in "\n".join(r.content for r in rows)
