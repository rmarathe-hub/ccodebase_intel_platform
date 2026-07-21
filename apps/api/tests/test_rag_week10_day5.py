"""Week 10 Day 5: grounded POST /ask + citation post-validation."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from pydantic_settings import SettingsConfigDict
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db.deps import get_db
from app.main import app
from app.models import Chunk, Repository, SnapshotStatus
from app.services.chunking import replace_chunks_for_snapshot
from app.services.discovery import discover_repository
from app.services.embeddings import replace_embeddings_for_snapshot
from app.services.files_query import latest_ready_snapshot
from app.services.rag.answer import mock_grounded_answer, run_ask
from app.services.rag.citations import (
    parse_citations,
    scrub_invalid_citations,
    validate_citations,
)
from app.services.rag.context_expand import ContextUnit, estimate_tokens
from app.services.snapshots import create_or_update_snapshot
from app.services.source_files import replace_source_files_for_snapshot
from tests.conftest import requires_postgres

pytestmark = requires_postgres

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "generic_polyglot"


class _AskSettings(Settings):
    model_config = SettingsConfigDict(env_file=None, extra="ignore")
    embedding_provider: str = "local"
    embedding_model: str = "local-hash-v1"
    embedding_version: str = "9.2"
    embedding_dimensions: int = 1536
    embeddings_enabled: bool = True
    ask_enabled: bool = True
    ask_use_mock: bool = True
    ask_cache_enabled: bool = True
    ask_prompt_version: str = "10.5-test"
    ask_rerank_use_mock: bool = True
    ask_query_rewrite_enabled: bool = True
    ask_query_max_rewrites: int = 4
    ask_context_token_budget: int = 6000
    llm_kill_switch: bool = False


@pytest.fixture()
def client(db_session: Session) -> TestClient:
    def _override() -> Session:
        return db_session

    app.dependency_overrides[get_db] = _override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _index(db_session: Session, cfg: Settings | None = None) -> Repository:
    conf = cfg or _AskSettings()
    repo = Repository(
        host="github.com",
        owner_name="week10",
        name=f"ask-{uuid4().hex[:8]}",
        default_branch="main",
        clone_url="https://github.com/week10/ask.git",
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
    replace_chunks_for_snapshot(db_session, snapshot_id=snapshot.id, repo_root=FIXTURE)
    db_session.flush()
    replace_embeddings_for_snapshot(db_session, snapshot_id=snapshot.id, cfg=conf)
    db_session.commit()
    return repo


# --- citation unit tests ---


def test_parse_citations_path_start_end() -> None:
    refs = parse_citations("See pkg/helpers.ts:12-18 and cmd/hello/main.go:3")
    assert len(refs) == 2
    assert refs[0].path == "pkg/helpers.ts"
    assert refs[0].start_line == 12
    assert refs[0].end_line == 18
    assert refs[1].start_line == 3
    assert refs[1].end_line == 3


def test_validate_citations_accepts_evidence_only(db_session: Session) -> None:
    cfg = _AskSettings()
    repo = _index(db_session, cfg)
    snap = latest_ready_snapshot(db_session, repo.id)
    assert snap is not None
    chunk = db_session.query(Chunk).filter(Chunk.snapshot_id == snap.id).first()
    assert chunk is not None

    good = citation_text = f"{chunk.path}:{chunk.start_line}-{chunk.end_line}"
    bad = f"{chunk.path}:{chunk.end_line + 50}-{chunk.end_line + 60}"
    invented = "totally/fake.py:1-2"
    text = f"Claim A ({good}). Claim B ({bad}). Claim C ({invented})."

    result = validate_citations(text, evidence=[chunk])
    assert len(result.valid_citations) == 1
    assert result.valid_citations[0].chunk_id == chunk.id
    assert len(result.dropped) == 2
    assert result.ok is False

    scrubbed = scrub_invalid_citations(text, result.dropped)
    assert citation_text in scrubbed
    assert "[citation removed]" in scrubbed
    assert invented not in scrubbed


def test_mock_grounded_answer_cites_units(db_session: Session) -> None:
    cfg = _AskSettings()
    repo = _index(db_session, cfg)
    snap = latest_ready_snapshot(db_session, repo.id)
    assert snap is not None
    chunk = db_session.query(Chunk).filter(Chunk.snapshot_id == snap.id).first()
    assert chunk is not None
    unit = ContextUnit(
        chunk=chunk,
        role="seed",
        depth=0,
        estimated_tokens=estimate_tokens(chunk.content),
        source_seed_id=chunk.id,
    )
    answer, cites = mock_grounded_answer("what is here?", units=[unit])
    assert chunk.path in answer
    assert cites
    assert all(c.valid for c in cites)


def test_run_ask_mock_ok(db_session: Session, monkeypatch: pytest.MonkeyPatch) -> None:
    cfg = _AskSettings()
    monkeypatch.setattr("app.services.rag.answer.settings", cfg)
    monkeypatch.setattr("app.services.rag.pipeline.settings", cfg)
    monkeypatch.setattr("app.services.rag.candidates.settings", cfg)
    monkeypatch.setattr("app.services.rag.rerank.settings", cfg)
    monkeypatch.setattr("app.services.rag.query_analysis.settings", cfg)
    monkeypatch.setattr("app.services.rag.context_expand.settings", cfg)

    repo = _index(db_session, cfg)
    snap = latest_ready_snapshot(db_session, repo.id)
    assert snap is not None

    result = run_ask(
        db_session,
        snapshot_id=snap.id,
        question="how does greeting work?",
        cfg=cfg,
    )
    assert result.status in {"ok", "partial"}
    assert result.answer
    assert result.validation.valid_citations
    assert all(c.valid for c in result.validation.valid_citations)
    assert result.model_provenance.get("provider") == "mock"


def test_run_ask_drops_invented_citations_from_llm_hook(
    db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    cfg = _AskSettings(ask_use_mock=False, ask_cache_enabled=False)
    monkeypatch.setattr("app.services.rag.answer.settings", cfg)

    repo = _index(db_session, cfg)
    snap = latest_ready_snapshot(db_session, repo.id)
    assert snap is not None

    def _llm(_question: str, evidence: list[dict]) -> dict:
        real = evidence[0]["citation"]
        return {
            "answer": f"Real {real}. Fake totally/missing.py:1-9.",
            "claims": [
                {"text": "real", "citation": real},
                {"text": "fake", "citation": "totally/missing.py:1-9"},
            ],
        }

    result = run_ask(
        db_session,
        snapshot_id=snap.id,
        question="greeting helper",
        cfg=cfg,
        llm_callable=_llm,
    )
    assert result.status == "partial"
    assert all(c.valid for c in result.validation.valid_citations)
    assert "totally/missing.py" not in result.answer
    assert "[citation removed]" in result.answer or result.validation.dropped


def test_ask_disabled(db_session: Session) -> None:
    cfg = _AskSettings(ask_enabled=False)
    repo = _index(db_session, cfg)
    snap = latest_ready_snapshot(db_session, repo.id)
    assert snap is not None
    result = run_ask(db_session, snapshot_id=snap.id, question="hello", cfg=cfg)
    assert result.status == "ask_disabled"


def test_ask_api_endpoint(client: TestClient, db_session: Session, monkeypatch: pytest.MonkeyPatch) -> None:
    cfg = _AskSettings()
    monkeypatch.setattr("app.services.rag.answer.settings", cfg)
    monkeypatch.setattr("app.services.rag.pipeline.settings", cfg)
    monkeypatch.setattr("app.services.rag.candidates.settings", cfg)
    monkeypatch.setattr("app.services.rag.rerank.settings", cfg)
    monkeypatch.setattr("app.services.rag.query_analysis.settings", cfg)
    monkeypatch.setattr("app.services.rag.context_expand.settings", cfg)
    monkeypatch.setattr("app.core.config.settings", cfg)

    repo = _index(db_session, cfg)
    resp = client.post(
        f"/api/v1/repositories/{repo.id}/ask",
        json={"question": "how does the greeting helper work?"},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["status"] in {"ok", "partial"}
    assert body["snapshot_id"]
    assert body["answer"]
    assert body["citations"]
    assert body["validation"]["valid_count"] >= 1
    assert body["analysis"]["kind"]
    for cite in body["citations"]:
        assert cite["valid"] is True
        assert cite["path"]
        assert cite["start_line"] >= 1
        assert cite["end_line"] >= cite["start_line"]


def test_ask_api_unknown_repo(client: TestClient) -> None:
    resp = client.post(
        f"/api/v1/repositories/{uuid4()}/ask",
        json={"question": "hello"},
    )
    assert resp.status_code == 404
