"""Week 9 Days 3–4: semantic + hybrid chunk search."""

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
from app.models import Repository, SnapshotStatus
from app.services.chunking import replace_chunks_for_snapshot
from app.services.discovery import discover_repository
from app.services.embeddings import replace_embeddings_for_snapshot
from app.services.files_query import latest_ready_snapshot
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


def _index_and_embed(db_session: Session) -> Repository:
    repo = Repository(
        host="github.com",
        owner_name="rmarathe-hub",
        name=f"search-{uuid4().hex[:8]}",
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
    db_session.flush()
    replace_embeddings_for_snapshot(db_session, snapshot_id=snapshot.id)
    db_session.commit()
    return repo


def test_invalid_search_mode_rejected(client: TestClient, db_session: Session) -> None:
    repo = _index_and_embed(db_session)
    resp = client.get(
        f"/api/v1/repositories/{repo.id}/chunks/search",
        params={"q": "Hello", "search_mode": "maybe"},
    )
    assert resp.status_code == 422
    assert resp.json()["detail"]["code"] == "invalid_search_mode"


def test_exact_mode_unchanged_default(client: TestClient, db_session: Session) -> None:
    repo = _index_and_embed(db_session)
    resp = client.get(
        f"/api/v1/repositories/{repo.id}/chunks/search",
        params={"q": "Hello", "limit": 20},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["search_mode"] == "exact"
    assert body["total"] >= 1
    assert all(h["score"] == 1.0 for h in body["hits"])
    assert all(h["score_breakdown"]["exact"] == 1.0 for h in body["hits"])
    assert all("path" in h and h["start_line"] >= 1 for h in body["hits"])


def test_semantic_search_returns_scored_citations(
    client: TestClient, db_session: Session
) -> None:
    repo = _index_and_embed(db_session)
    resp = client.get(
        f"/api/v1/repositories/{repo.id}/chunks/search",
        params={"q": "Hello greeting main", "search_mode": "semantic", "limit": 10},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["search_mode"] == "semantic"
    assert body["total"] >= 1
    assert len(body["hits"]) >= 1
    for hit in body["hits"]:
        assert hit["path"]
        assert hit["start_line"] >= 1
        assert hit["end_line"] >= hit["start_line"]
        assert hit["score"] is not None
        assert 0.0 <= hit["score"] <= 1.0
        assert hit["score_breakdown"] is not None
        assert "semantic" in hit["score_breakdown"]
        assert "cosine_distance" in hit["score_breakdown"]


def test_semantic_respects_language_filter(
    client: TestClient, db_session: Session
) -> None:
    repo = _index_and_embed(db_session)
    resp = client.get(
        f"/api/v1/repositories/{repo.id}/chunks/search",
        params={"q": "package main", "search_mode": "semantic", "language": "go"},
    )
    assert resp.status_code == 200
    hits = resp.json()["hits"]
    assert hits
    assert all(h["language"] == "go" for h in hits)


def test_semantic_empty_without_embeddings(
    client: TestClient, db_session: Session
) -> None:
    repo = Repository(
        host="github.com",
        owner_name="rmarathe-hub",
        name=f"noemb-{uuid4().hex[:8]}",
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
    replace_chunks_for_snapshot(db_session, snapshot_id=snapshot.id, repo_root=FIXTURE)
    db_session.commit()

    resp = client.get(
        f"/api/v1/repositories/{repo.id}/chunks/search",
        params={"q": "Hello", "search_mode": "semantic"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["search_mode"] == "semantic"
    assert body["total"] == 0
    assert body["hits"] == []


def test_semantic_empty_when_embeddings_disabled(
    client: TestClient, db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    class Off(Settings):
        model_config = SettingsConfigDict(env_file=None, extra="ignore")
        embeddings_enabled: bool = False

    monkeypatch.setattr("app.services.chunks_query.settings", Off())
    repo = _index_and_embed(db_session)
    resp = client.get(
        f"/api/v1/repositories/{repo.id}/chunks/search",
        params={"q": "Hello", "search_mode": "semantic"},
    )
    assert resp.status_code == 200
    assert resp.json()["total"] == 0


def test_hybrid_includes_breakdown_and_stable_order(
    client: TestClient, db_session: Session
) -> None:
    repo = _index_and_embed(db_session)
    resp = client.get(
        f"/api/v1/repositories/{repo.id}/chunks/search",
        params={"q": "Hello", "search_mode": "hybrid", "limit": 15},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["search_mode"] == "hybrid"
    assert body["total"] >= 1
    hits = body["hits"]
    assert hits
    for hit in hits:
        assert hit["score"] is not None
        bd = hit["score_breakdown"]
        assert bd is not None
        assert "exact" in bd and "semantic" in bd and "fused" in bd
        assert "path" in hit and hit["start_line"] >= 1

    # Stable ordering: repeated call identical hit ids
    resp2 = client.get(
        f"/api/v1/repositories/{repo.id}/chunks/search",
        params={"q": "Hello", "search_mode": "hybrid", "limit": 15},
    )
    assert [h["id"] for h in resp2.json()["hits"]] == [h["id"] for h in hits]

    # Scores non-increasing
    scores = [h["score"] for h in hits]
    assert scores == sorted(scores, reverse=True)


def test_hybrid_differs_from_exact_only(
    client: TestClient, db_session: Session
) -> None:
    repo = _index_and_embed(db_session)
    exact = client.get(
        f"/api/v1/repositories/{repo.id}/chunks/search",
        params={"q": "Hello", "search_mode": "exact", "limit": 50},
    ).json()
    hybrid = client.get(
        f"/api/v1/repositories/{repo.id}/chunks/search",
        params={"q": "Hello", "search_mode": "hybrid", "limit": 50},
    ).json()
    assert exact["search_mode"] == "exact"
    assert hybrid["search_mode"] == "hybrid"
    # Hybrid candidate set is a superset (exact ∪ semantic neighbors).
    assert hybrid["total"] >= exact["total"]
    exact_ids = {h["id"] for h in exact["hits"]}
    hybrid_ids = {h["id"] for h in hybrid["hits"]}
    assert exact_ids.issubset(hybrid_ids) or hybrid["total"] > exact["total"]


def test_hybrid_preserves_support_level_labels(
    client: TestClient, db_session: Session
) -> None:
    repo = _index_and_embed(db_session)
    snap = latest_ready_snapshot(db_session, repo.id)
    assert snap is not None
    resp = client.get(
        f"/api/v1/repositories/{repo.id}/chunks/search",
        params={"q": "main", "search_mode": "hybrid", "limit": 30},
    )
    assert resp.status_code == 200
    for hit in resp.json()["hits"]:
        assert hit["support_level"] in {"deep", "generic", "skip"}
        # Generic hits must not be claimed verified-deep via search.
        if hit["support_level"] == "generic":
            assert hit["verified_deep"] is False
