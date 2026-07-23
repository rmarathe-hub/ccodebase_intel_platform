"""Week 7 Days 1–2: chunk extraction, persist, mocked LLM enrichment."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.models import Chunk, Repository, SnapshotStatus
from app.services.chunking import replace_chunks_for_snapshot
from app.services.chunking.sql_chunks import chunk_sql_source
from app.services.chunking.treesitter_generic import chunk_generic_source
from app.services.discovery import discover_repository
from app.services.java_symbols import replace_java_symbols_for_snapshot
from app.services.js_ts_symbols import replace_js_ts_symbols_for_snapshot
from app.services.llm.azure_openai import mock_enrichment_for_items
from app.services.snapshots import create_or_update_snapshot
from app.services.source_files import replace_source_files_for_snapshot
from app.services.symbols import replace_python_symbols_for_snapshot
from tests.conftest import requires_postgres

pytestmark = requires_postgres

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "generic_polyglot"


def test_go_treesitter_chunks_offline() -> None:
    source = (FIXTURE / "cmd/hello/main.go").read_text(encoding="utf-8")
    chunks = chunk_generic_source(source=source, path="cmd/hello/main.go", language="go")
    assert chunks
    assert all(c.verified_deep is False for c in chunks)
    assert all(c.support_level == "generic" for c in chunks)
    assert any(c.extraction_method == "treesitter_node" for c in chunks)
    assert any("Hello" in c.content or "func" in c.content for c in chunks)


@pytest.mark.parametrize(
    ("rel", "language"),
    [
        ("src/lib.rs", "rust"),
        ("c/add.c", "c"),
        ("cpp/greeter.cpp", "c++"),
        ("csharp/Program.cs", "c#"),
        ("ruby/greeter.rb", "ruby"),
        ("scripts/hello.sh", "shell"),
    ],
)
def test_generic_language_chunks_offline(rel: str, language: str) -> None:
    source = (FIXTURE / rel).read_text(encoding="utf-8")
    chunks = chunk_generic_source(source=source, path=rel, language=language)
    assert chunks, f"expected chunks for {language}"
    assert all(c.chunk_type == "generic_structure" for c in chunks)
    assert all(c.parser_name.endswith("treesitter") for c in chunks)


def test_sql_sqlglot_chunks_offline() -> None:
    source = (FIXTURE / "db/schema.sql").read_text(encoding="utf-8")
    chunks = chunk_sql_source(source=source, path="db/schema.sql")
    assert len(chunks) >= 2
    assert all(c.extraction_method == "sqlglot_tokenizer" for c in chunks)
    assert all(c.verified_deep is False for c in chunks)


def test_strings_do_not_create_fake_go_funcs() -> None:
    source = 'package main\n\nconst s = "func Fake() {}"\n\nfunc Real() {}\n'
    chunks = chunk_generic_source(source=source, path="x.go", language="go")
    func_chunks = [
        c
        for c in chunks
        if c.metadata_json and "function_declaration" in c.metadata_json
    ]
    assert any("func Real()" in c.content for c in func_chunks)
    assert all("Fake" not in c.content for c in func_chunks)


def test_replace_chunks_polyglot_and_stable_hash(db_session: Session) -> None:
    repo = Repository(
        host="github.com",
        owner_name="rmarathe-hub",
        name=f"poly-{uuid4().hex[:8]}",
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

    n1, e1 = replace_chunks_for_snapshot(
        db_session, snapshot_id=snapshot.id, repo_root=FIXTURE
    )
    db_session.commit()
    assert n1 >= 5
    assert e1 == 0  # enrichment disabled by default
    rows = list(
        db_session.scalars(select(Chunk).where(Chunk.snapshot_id == snapshot.id)).all()
    )
    assert all(r.verified_deep is False for r in rows)
    assert any(r.language == "go" for r in rows)
    assert any(r.language == "sql" for r in rows)
    hashes = sorted(r.content_hash for r in rows)

    n2, _ = replace_chunks_for_snapshot(
        db_session, snapshot_id=snapshot.id, repo_root=FIXTURE
    )
    db_session.commit()
    assert n2 == n1
    rows2 = list(
        db_session.scalars(select(Chunk).where(Chunk.snapshot_id == snapshot.id)).all()
    )
    assert sorted(r.content_hash for r in rows2) == hashes


def test_deep_symbol_chunks_from_python_java(
    db_session: Session, tmp_path: Path
) -> None:
    # Merge a tiny python+java tree.
    root = tmp_path / "mixed"
    (root / "pkg").mkdir(parents=True)
    (root / "pkg" / "svc.py").write_text(
        (
            "def helper(x):\n"
            "    return x\n\n"
            "class Box:\n"
            "    def run(self):\n"
            "        return helper(1)\n"
        ),
        encoding="utf-8",
    )
    (root / "Main.java").write_text(
        "package demo;\npublic class Main {\n  public int add(int a, int b) { return a + b; }\n}\n",
        encoding="utf-8",
    )

    repo = Repository(
        host="github.com",
        owner_name="rmarathe-hub",
        name=f"deep-chunk-{uuid4().hex[:8]}",
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
    discovery = discover_repository(root)
    replace_source_files_for_snapshot(
        db_session, snapshot_id=snapshot.id, discovery=discovery
    )
    db_session.flush()
    replace_python_symbols_for_snapshot(
        db_session, snapshot_id=snapshot.id, repo_root=root
    )
    replace_java_symbols_for_snapshot(
        db_session, snapshot_id=snapshot.id, repo_root=root
    )
    replace_js_ts_symbols_for_snapshot(
        db_session, snapshot_id=snapshot.id, repo_root=root
    )
    n, _ = replace_chunks_for_snapshot(
        db_session, snapshot_id=snapshot.id, repo_root=root
    )
    db_session.commit()
    assert n >= 2
    deep = list(
        db_session.scalars(
            select(Chunk).where(
                Chunk.snapshot_id == snapshot.id, Chunk.verified_deep.is_(True)
            )
        ).all()
    )
    assert deep
    assert all(c.extraction_method == "deep_symbol" for c in deep)
    assert all(c.chunk_type == "symbol" for c in deep)


def test_enrichment_batch_with_mock_provider(
    db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    class MockProvider:
        provider_name = "azure_openai"

        def enrich_batch(self, *, items, prompt_version):  # type: ignore[no-untyped-def]
            return mock_enrichment_for_items(items, prompt_version=prompt_version)

        def summarize_repository(self, **kwargs):  # type: ignore[no-untyped-def]
            raise NotImplementedError

    monkeypatch.setattr(
        "app.services.chunking.get_llm_provider", lambda cfg=None: MockProvider()
    )
    cfg = Settings(
        llm_enrichment_enabled=True,
        llm_provider="azure_openai",
        azure_openai_endpoint="https://example.openai.azure.com/",
        azure_openai_api_key="test",
        azure_openai_deployment="gpt-test",
        llm_max_chunks_per_request=4,
        llm_max_requests_per_job=5,
    )

    repo = Repository(
        host="github.com",
        owner_name="rmarathe-hub",
        name=f"enrich-{uuid4().hex[:8]}",
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
        db_session, snapshot_id=snapshot.id, repo_root=FIXTURE, cfg=cfg
    )
    db_session.commit()
    assert n >= 5
    assert enriched >= 1
    rows = list(
        db_session.scalars(select(Chunk).where(Chunk.snapshot_id == snapshot.id)).all()
    )
    assert any(r.llm_enriched for r in rows)
    assert all(not r.verified_deep for r in rows)
    assert any(r.validation_status == "accepted" for r in rows)
