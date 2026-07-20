"""Week 8 Day 4 — generic directory graph API."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.main import app
from app.models import Repository, SnapshotStatus
from app.services.chunking import replace_chunks_for_snapshot
from app.services.discovery import discover_repository
from app.services.snapshots import create_or_update_snapshot
from app.services.source_files import replace_source_files_for_snapshot
from tests.conftest import requires_postgres

pytestmark = requires_postgres

POLYGLOT = Path(__file__).resolve().parent / "fixtures" / "generic_polyglot"


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
        name=f"w8d4-{uuid4().hex[:8]}",
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
    discovery = discover_repository(POLYGLOT)
    replace_source_files_for_snapshot(
        db_session, snapshot_id=snapshot.id, discovery=discovery
    )
    db_session.flush()
    replace_chunks_for_snapshot(
        db_session, snapshot_id=snapshot.id, repo_root=POLYGLOT
    )
    db_session.commit()
    return repo


def test_directory_graph_hierarchy(client: TestClient, db_session: Session) -> None:
    repo = _index_polyglot(db_session)
    resp = client.get(f"/api/v1/repositories/{repo.id}/graph/directories")
    assert resp.status_code == 200
    body = resp.json()
    assert body["graph_type"] == "directories"
    assert body["node_count"] >= 5
    dir_nodes = [n for n in body["nodes"] if n["node_type"] == "directory"]
    assert dir_nodes
    dir_ids = {n["id"] for n in dir_nodes}
    assert "cmd" in dir_ids or "cmd/hello" in dir_ids
    assert "docs" in dir_ids
    contains = [e for e in body["edges"] if e["relation_kind"] == "contains"]
    assert contains
    assert all(e["inferred"] is False for e in contains)
    # Generic repo: no verified-deep call edges in directory graph
    assert all(e["relation_kind"] != "calls" for e in body["edges"])


def test_directory_graph_no_fake_deep_symbols(
    client: TestClient, db_session: Session
) -> None:
    repo = _index_polyglot(db_session)
    resp = client.get(
        f"/api/v1/repositories/{repo.id}/graph/directories",
        params={"include_files": "true"},
    )
    assert resp.status_code == 200
    body = resp.json()
    file_nodes = [n for n in body["nodes"] if n["node_type"] == "file"]
    assert file_nodes
    assert all(n["support_level"] == "generic" for n in file_nodes)
    assert all(n.get("symbol_id") is None for n in body["nodes"])
