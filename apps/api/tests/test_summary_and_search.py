"""Week 7 Days 5–6: repository summary + exact chunk search."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db.deps import get_db
from app.main import app
from app.models import Repository, SnapshotStatus
from app.services.chunking import replace_chunks_for_snapshot
from app.services.discovery import discover_repository
from app.services.repository_summary import (
    build_deterministic_summary,
    build_repository_summary,
    mock_repository_summary,
)
from app.services.snapshots import create_or_update_snapshot
from app.services.source_files import replace_source_files_for_snapshot
from tests.conftest import requires_postgres

pytestmark = requires_postgres

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "generic_polyglot"


@pytest.fixture()
def client(db_session: Session) -> TestClient:
    def _override() -> Session:
        return db_session

    app.dependency_overrides[get_db] = _override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _index_polyglot(db_session: Session) -> Repository:
    repo = Repository(
        host="github.com",
        owner_name="rmarathe-hub",
        name=f"sum-{uuid4().hex[:8]}",
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
    replace_chunks_for_snapshot(db_session, snapshot_id=snapshot.id, repo_root=FIXTURE)
    db_session.commit()
    return repo


def test_deterministic_summary_shape(db_session: Session) -> None:
    repo = _index_polyglot(db_session)
    from app.services.files_query import latest_ready_snapshot

    snap = latest_ready_snapshot(db_session, repo.id)
    assert snap is not None
    summary = build_deterministic_summary(db_session, snapshot_id=snap.id)
    assert summary["file_count"] >= 5
    assert "go" in summary["language_mix"] or "configuration" in summary["language_mix"]
    assert summary["chunk_counts"]["total"] >= 1
    assert isinstance(summary["entry_point_candidates"], list)
    assert "cmd/hello/main.go" in summary["entry_point_candidates"] or any(
        "main.go" in p for p in summary["entry_point_candidates"]
    )


def test_summary_api_disabled_llm(client: TestClient, db_session: Session) -> None:
    repo = _index_polyglot(db_session)
    resp = client.get(f"/api/v1/repositories/{repo.id}/summary")
    assert resp.status_code == 200
    body = resp.json()
    assert body["deterministic_summary"] is not None
    assert body["deterministic_summary"]["file_count"] >= 1
    assert body["llm_summary"] is None
    assert body["llm_summary_status"] in {"disabled", "skipped", "provider_unavailable"}


def test_summary_api_with_mock_llm(
    client: TestClient, db_session: Session, monkeypatch: pytest.MonkeyPatch
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
    monkeypatch.setattr(
        "app.services.repository_summary.settings",
        Settings(
            llm_enrichment_enabled=True,
            llm_provider="azure_openai",
            azure_openai_endpoint="https://example.openai.azure.com/",
            azure_openai_api_key="test",
            azure_openai_deployment="gpt-test",
        ),
    )

    repo = _index_polyglot(db_session)
    # build_repository_summary uses settings from module — patch cfg via monkeypatch on build call path
    from app.services.files_query import latest_ready_snapshot

    snap = latest_ready_snapshot(db_session, repo.id)
    assert snap is not None
    built = build_repository_summary(
        db_session,
        snapshot_id=snap.id,
        cfg=Settings(
            llm_enrichment_enabled=True,
            llm_provider="azure_openai",
            azure_openai_endpoint="https://example.openai.azure.com/",
            azure_openai_api_key="test",
            azure_openai_deployment="gpt-test",
        ),
    )
    assert built["llm_summary_status"] == "ok"
    assert built["llm_summary"] is not None
    assert built["deterministic_summary"] is not None
    assert built["llm_summary"]["claims_verified_deep"] is False


def test_exact_chunk_search_api(client: TestClient, db_session: Session) -> None:
    repo = _index_polyglot(db_session)
    resp = client.get(
        f"/api/v1/repositories/{repo.id}/chunks/search",
        params={"q": "Hello", "limit": 50},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["search_mode"] == "exact"
    assert body["total"] >= 1
    assert all("start_line" in h and "end_line" in h and "path" in h for h in body["hits"])
    assert all("Hello" in h["content"] or "hello" in h["content"].lower() for h in body["hits"])

    filtered = client.get(
        f"/api/v1/repositories/{repo.id}/chunks/search",
        params={"q": "Hello", "language": "go", "llm_enriched": False},
    )
    assert filtered.status_code == 200
    assert filtered.json()["search_mode"] == "exact"
    assert all(h["language"] == "go" for h in filtered.json()["hits"])
    assert all(h["llm_enriched"] is False for h in filtered.json()["hits"])


def test_exact_search_works_without_llm(client: TestClient, db_session: Session) -> None:
    repo = _index_polyglot(db_session)
    resp = client.get(
        f"/api/v1/repositories/{repo.id}/chunks/search",
        params={"q": "serde", "chunk_type": "configuration_section"},
    )
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1
