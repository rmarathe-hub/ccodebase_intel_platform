"""Week 8 Day 3 — call neighborhood graph + implementations API."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.main import app
from app.models import Repository, SnapshotStatus, Symbol
from app.services.discovery import discover_repository
from app.services.java_symbols import replace_java_symbols_for_snapshot
from app.services.relationships import replace_structural_relations_for_snapshot
from app.services.snapshots import create_or_update_snapshot
from app.services.source_files import replace_source_files_for_snapshot
from app.services.symbols import replace_python_symbols_for_snapshot
from tests.conftest import requires_postgres

pytestmark = requires_postgres

SPRING = Path(__file__).resolve().parent / "fixtures" / "spring_fixture"


@pytest.fixture()
def client(db_session: Session) -> TestClient:
    def _override() -> Session:
        return db_session

    app.dependency_overrides[get_db] = _override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _index_python_calls(db_session: Session, tmp_path: Path) -> tuple[Repository, Symbol, Symbol]:
    (tmp_path / "svc.py").write_text(
        "def helper():\n"
        "    return 1\n\n"
        "def main():\n"
        "    return helper()\n",
        encoding="utf-8",
    )
    repo = Repository(
        host="github.com",
        owner_name="rmarathe-hub",
        name=f"w8d3-{uuid4().hex[:8]}",
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
    discovery = discover_repository(tmp_path)
    replace_source_files_for_snapshot(
        db_session, snapshot_id=snapshot.id, discovery=discovery
    )
    db_session.flush()
    replace_python_symbols_for_snapshot(
        db_session, snapshot_id=snapshot.id, repo_root=tmp_path
    )
    replace_structural_relations_for_snapshot(db_session, snapshot_id=snapshot.id)
    db_session.commit()
    symbols = list(
        db_session.scalars(select(Symbol).where(Symbol.snapshot_id == snapshot.id)).all()
    )
    by_name = {s.name: s for s in symbols}
    return repo, by_name["main"], by_name["helper"]


def _index_spring(db_session: Session) -> tuple[Repository, Symbol]:
    repo = Repository(
        host="github.com",
        owner_name="rmarathe-hub",
        name=f"w8d3-spring-{uuid4().hex[:8]}",
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
    discovery = discover_repository(SPRING)
    replace_source_files_for_snapshot(
        db_session, snapshot_id=snapshot.id, discovery=discovery
    )
    db_session.flush()
    replace_java_symbols_for_snapshot(
        db_session, snapshot_id=snapshot.id, repo_root=SPRING
    )
    replace_structural_relations_for_snapshot(db_session, snapshot_id=snapshot.id)
    db_session.commit()
    iface = db_session.scalars(
        select(Symbol).where(
            Symbol.snapshot_id == snapshot.id,
            Symbol.name == "UserService",
        )
    ).first()
    assert iface is not None
    return repo, iface


def test_call_neighborhood_graph_api(
    client: TestClient, db_session: Session, tmp_path: Path
) -> None:
    repo, main, helper = _index_python_calls(db_session, tmp_path)
    resp = client.get(
        f"/api/v1/repositories/{repo.id}/graph/calls",
        params={"symbol_id": str(main.id), "depth": 1},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["graph_type"] == "calls"
    assert body["center_symbol_id"] == str(main.id)
    assert body["node_count"] >= 2
    assert body["edge_count"] >= 1
    assert all(n["node_type"] == "symbol" for n in body["nodes"])
    assert all(n["support_level"] == "deep" for n in body["nodes"])
    assert all(e["relation_kind"] == "calls" for e in body["edges"])
    node_ids = {n["id"] for n in body["nodes"]}
    assert str(main.id) in node_ids
    assert str(helper.id) in node_ids


def test_implementations_api_spring(
    client: TestClient, db_session: Session
) -> None:
    repo, iface = _index_spring(db_session)
    resp = client.get(
        f"/api/v1/repositories/{repo.id}/symbols/{iface.id}/implementations"
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["symbol_qualified_name"].endswith("UserService")
    assert body["total"] >= 1
    assert any(i["name"] == "UserServiceImpl" for i in body["implementations"])
    assert all(i["relation_kind"] == "implements" for i in body["implementations"])
    assert all(i["confidence"] == "resolved" for i in body["implementations"])
