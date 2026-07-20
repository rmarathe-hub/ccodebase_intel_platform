"""Week 7 Day 7 — full polyglot matrix: discover → chunk → summary → search → worker."""

from __future__ import annotations

import ast
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db.deps import get_db
from app.main import app
from app.models import Chunk, LlmEnrichmentCache, Repository, SnapshotStatus, SourceFile, Symbol
from app.services.chunking import replace_chunks_for_snapshot
from app.services.discovery import discover_repository
from app.services.llm.azure_openai import mock_enrichment_for_items
from app.services.repository_summary import build_repository_summary, mock_repository_summary
from app.services.snapshots import create_or_update_snapshot
from app.services.source_files import replace_source_files_for_snapshot
from tests.conftest import requires_postgres

pytestmark = requires_postgres

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "generic_polyglot"
CHUNKING_ROOT = Path(__file__).resolve().parents[1] / "app" / "services" / "chunking"

EXPECTED_LANG_FILES = {
    "go": "cmd/hello/main.go",
    "rust": "src/lib.rs",
    "c": "c/add.c",
    "c++": "cpp/greeter.cpp",
    "c#": "csharp/Program.cs",
    "ruby": "ruby/greeter.rb",
    "shell": "scripts/hello.sh",
    "sql": "db/schema.sql",
    "configuration": "package.json",
    "documentation": "docs/ARCHITECTURE.md",
}


@pytest.fixture()
def client(db_session: Session) -> TestClient:
    def _override() -> Session:
        return db_session

    app.dependency_overrides[get_db] = _override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _index(db_session: Session, *, cfg: Settings | None = None) -> tuple[Repository, object]:
    repo = Repository(
        host="github.com",
        owner_name="rmarathe-hub",
        name=f"w7d7-{uuid4().hex[:8]}",
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
    replace_chunks_for_snapshot(
        db_session, snapshot_id=snapshot.id, repo_root=FIXTURE, cfg=cfg
    )
    db_session.commit()
    return repo, snapshot


def test_chunking_package_has_no_regex_imports() -> None:
    """Structural chunkers must not import the re module."""
    offenders: list[str] = []
    for path in CHUNKING_ROOT.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "re" or alias.name.startswith("re."):
                        offenders.append(str(path))
            elif isinstance(node, ast.ImportFrom) and node.module == "re":
                offenders.append(str(path))
    assert offenders == []


def test_polyglot_discovery_classifies_expected_languages() -> None:
    discovery = discover_repository(FIXTURE)
    by_path = {f.path: f for f in discovery.files}
    for language, path in EXPECTED_LANG_FILES.items():
        assert path in by_path, path
        assert by_path[path].support_level.value == "generic"
        assert by_path[path].language == language
    # Dockerfile special filename
    assert "Dockerfile" in by_path
    assert by_path["Dockerfile"].language == "configuration"


def test_full_pipeline_matrix_api(
    client: TestClient, db_session: Session
) -> None:
    repo, snapshot = _index(db_session)

    files = list(
        db_session.scalars(
            select(SourceFile).where(SourceFile.snapshot_id == snapshot.id)
        ).all()
    )
    assert len(files) >= len(EXPECTED_LANG_FILES)

    chunks = list(
        db_session.scalars(select(Chunk).where(Chunk.snapshot_id == snapshot.id)).all()
    )
    assert len(chunks) >= 15
    assert all(c.verified_deep is False for c in chunks)
    langs = {c.language for c in chunks}
    for needed in ("go", "rust", "sql", "configuration", "documentation"):
        assert needed in langs

    # No verified Symbol rows for generic languages
    symbols = list(
        db_session.scalars(select(Symbol).where(Symbol.snapshot_id == snapshot.id)).all()
    )
    assert all(s.language in {"python", "java", "javascript", "typescript"} for s in symbols)

    # No deep parser stamp pollution on generic files
    generic_files = [f for f in files if f.support_level == "generic"]
    assert generic_files
    assert all(
        f.parser_name is None
        or not f.parser_name.endswith("-ast")  # deep python stamp
        for f in generic_files
    )

    summary = client.get(f"/api/v1/repositories/{repo.id}/summary")
    assert summary.status_code == 200
    body = summary.json()
    assert body["deterministic_summary"] is not None
    assert body["deterministic_summary"]["chunk_counts"]["total"] >= 15
    assert body["llm_summary"] is None
    assert body["llm_summary_status"] in {"disabled", "skipped", "provider_unavailable"}

    search = client.get(
        f"/api/v1/repositories/{repo.id}/chunks/search",
        params={"q": "Hello", "limit": 100},
    )
    assert search.status_code == 200
    assert search.json()["search_mode"] == "exact"
    assert search.json()["total"] >= 1

    cfg_search = client.get(
        f"/api/v1/repositories/{repo.id}/chunks/search",
        params={"q": "serde", "chunk_type": "configuration_section"},
    )
    assert cfg_search.status_code == 200
    assert cfg_search.json()["total"] >= 1


def test_llm_failure_preserves_deterministic_chunks(
    db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    boom_calls = {"n": 0}

    class BoomProvider:
        provider_name = "azure_openai"

        def enrich_batch(self, **kwargs):  # type: ignore[no-untyped-def]
            boom_calls["n"] += 1
            raise RuntimeError("provider outage")

        def summarize_repository(self, **kwargs):  # type: ignore[no-untyped-def]
            raise RuntimeError("provider outage")

    monkeypatch.setattr(
        "app.services.chunking.get_llm_provider", lambda cfg=None: BoomProvider()
    )
    # Unique prompt_version avoids shared-DB cache hits from earlier enrichment tests.
    cfg = Settings(
        llm_enrichment_enabled=True,
        llm_provider="azure_openai",
        azure_openai_endpoint="https://example.openai.azure.com/",
        azure_openai_api_key="test",
        azure_openai_deployment="gpt-test",
        llm_prompt_version=f"w7d7-boom-{uuid4().hex[:8]}",
    )
    _repo, snapshot = _index(db_session, cfg=cfg)
    chunks = list(
        db_session.scalars(select(Chunk).where(Chunk.snapshot_id == snapshot.id)).all()
    )
    assert len(chunks) >= 15
    assert boom_calls["n"] >= 1
    assert all(c.llm_enriched is False for c in chunks)
    assert all(c.verified_deep is False for c in chunks)


def test_enrichment_batches_not_one_call_per_chunk(
    db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[int] = []

    class CountingProvider:
        provider_name = "azure_openai"

        def enrich_batch(self, *, items, prompt_version):  # type: ignore[no-untyped-def]
            calls.append(len(items))
            return mock_enrichment_for_items(items, prompt_version=prompt_version)

        def summarize_repository(self, **kwargs):  # type: ignore[no-untyped-def]
            raise NotImplementedError

    monkeypatch.setattr(
        "app.services.chunking.get_llm_provider", lambda cfg=None: CountingProvider()
    )
    cfg = Settings(
        llm_enrichment_enabled=True,
        llm_provider="azure_openai",
        azure_openai_endpoint="https://example.openai.azure.com/",
        azure_openai_api_key="test",
        azure_openai_deployment="gpt-test",
        llm_max_chunks_per_request=4,
        llm_max_requests_per_job=20,
        llm_prompt_version=f"w7d7-batch-{uuid4().hex[:8]}",
    )
    _repo, snapshot = _index(db_session, cfg=cfg)
    chunks = list(
        db_session.scalars(select(Chunk).where(Chunk.snapshot_id == snapshot.id)).all()
    )
    enriched = [c for c in chunks if c.llm_enriched]
    assert enriched
    assert calls, "expected at least one enrich_batch call"
    assert sum(calls) >= len(enriched)
    # One call per batch, not per chunk: request count must be < enriched chunk count
    # when there are more than max_chunks_per_request enriched items.
    if len(enriched) > cfg.llm_max_chunks_per_request:
        assert len(calls) < len(enriched)


def test_cache_avoids_repeat_enrichment_calls(
    db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls = {"n": 0}

    class CountingProvider:
        provider_name = "azure_openai"

        def enrich_batch(self, *, items, prompt_version):  # type: ignore[no-untyped-def]
            calls["n"] += 1
            return mock_enrichment_for_items(items, prompt_version=prompt_version)

        def summarize_repository(self, **kwargs):  # type: ignore[no-untyped-def]
            raise NotImplementedError

    monkeypatch.setattr(
        "app.services.chunking.get_llm_provider", lambda cfg=None: CountingProvider()
    )
    cfg = Settings(
        llm_enrichment_enabled=True,
        llm_provider="azure_openai",
        azure_openai_endpoint="https://example.openai.azure.com/",
        azure_openai_api_key="test",
        azure_openai_deployment="gpt-test",
        llm_max_chunks_per_request=8,
        llm_max_requests_per_job=50,
        llm_prompt_version=f"w7d7-cache-{uuid4().hex[:8]}",
    )
    repo = Repository(
        host="github.com",
        owner_name="rmarathe-hub",
        name=f"cache-{uuid4().hex[:8]}",
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
    replace_chunks_for_snapshot(
        db_session, snapshot_id=snapshot.id, repo_root=FIXTURE, cfg=cfg
    )
    db_session.commit()
    first_calls = calls["n"]
    assert first_calls >= 1
    cache_rows = list(db_session.scalars(select(LlmEnrichmentCache)).all())
    assert cache_rows

    calls["n"] = 0
    replace_chunks_for_snapshot(
        db_session, snapshot_id=snapshot.id, repo_root=FIXTURE, cfg=cfg
    )
    db_session.commit()
    # Second pass should be mostly/entirely cache hits → zero or fewer live calls.
    assert calls["n"] == 0


def test_llm_summary_mock_separate_from_deterministic(
    db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    class MockProvider:
        provider_name = "azure_openai"

        def enrich_batch(self, **kwargs):  # type: ignore[no-untyped-def]
            raise NotImplementedError

        def summarize_repository(self, **kwargs):  # type: ignore[no-untyped-def]
            return mock_repository_summary(**kwargs)

    monkeypatch.setattr(
        "app.services.repository_summary.get_llm_provider",
        lambda cfg=None: MockProvider(),
    )
    _repo, snapshot = _index(db_session)
    built = build_repository_summary(
        db_session,
        snapshot_id=snapshot.id,
        cfg=Settings(
            llm_enrichment_enabled=True,
            llm_provider="azure_openai",
            azure_openai_endpoint="https://example.openai.azure.com/",
            azure_openai_api_key="test",
            azure_openai_deployment="gpt-test",
        ),
    )
    assert built["deterministic_summary"] is not None
    assert built["llm_summary_status"] == "ok"
    assert built["llm_summary"] is not None
    assert built["llm_summary"]["claims_verified_deep"] is False
    # Deterministic fields must remain even when LLM is present
    assert "language_mix" in built["deterministic_summary"]  # type: ignore[operator]
