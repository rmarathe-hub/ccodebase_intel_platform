"""Week 8 Day 2 — module and package graph APIs."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.main import app
from app.models import Repository, SnapshotStatus
from app.services.discovery import discover_repository
from app.services.java_symbols import replace_java_symbols_for_snapshot
from app.services.js_ts_symbols import replace_js_ts_symbols_for_snapshot
from app.services.relationships import replace_structural_relations_for_snapshot
from app.services.snapshots import create_or_update_snapshot
from app.services.source_files import replace_source_files_for_snapshot
from app.services.symbols import replace_python_symbols_for_snapshot
from tests.conftest import requires_postgres

pytestmark = requires_postgres

MIXED = Path(__file__).resolve().parent / "fixtures" / "mixed_frontend_backend"
SPRING = Path(__file__).resolve().parent / "fixtures" / "spring_fixture"


@pytest.fixture()
def client(db_session: Session) -> TestClient:
    def _override() -> Session:
        return db_session

    app.dependency_overrides[get_db] = _override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _index(db_session: Session, root: Path) -> Repository:
    repo = Repository(
        host="github.com",
        owner_name="rmarathe-hub",
        name=f"w8d2-{uuid4().hex[:8]}",
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
    replace_js_ts_symbols_for_snapshot(
        db_session, snapshot_id=snapshot.id, repo_root=root
    )
    replace_java_symbols_for_snapshot(
        db_session, snapshot_id=snapshot.id, repo_root=root
    )
    replace_structural_relations_for_snapshot(db_session, snapshot_id=snapshot.id)
    db_session.commit()
    return repo


def test_module_graph_api_mixed_repo(client: TestClient, db_session: Session) -> None:
    repo = _index(db_session, MIXED)
    resp = client.get(
        f"/api/v1/repositories/{repo.id}/graph/modules",
        params={"local_imports_only": "true"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["graph_type"] == "modules"
    assert body["node_count"] >= 2
    assert body["edge_count"] >= 1
    assert all(n["node_type"] == "module" for n in body["nodes"])
    assert all(e["relation_kind"] == "imports" for e in body["edges"])
    langs = {n["language"] for n in body["nodes"]}
    assert "python" in langs
    assert langs & {"javascript", "typescript"}


def test_package_graph_api_spring_java(client: TestClient, db_session: Session) -> None:
    repo = _index(db_session, SPRING)
    resp = client.get(
        f"/api/v1/repositories/{repo.id}/graph/packages",
        params={"language": "java", "local_imports_only": "false"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["graph_type"] == "packages"
    assert body["node_count"] >= 1
    assert all(n["node_type"] == "package" for n in body["nodes"])
    if body["edges"]:
        assert all(e["inferred"] is True for e in body["edges"])


def test_relations_api_accepts_imports_kind(
    client: TestClient, db_session: Session
) -> None:
    repo = _index(db_session, MIXED)
    resp = client.get(
        f"/api/v1/repositories/{repo.id}/relations",
        params={"relation_kind": "imports", "limit": 20},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] >= 1
    assert all(r["relation_kind"] == "imports" for r in body["relations"])
