"""Week 8 Day 5 — graph API filter polish."""

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
from app.services.graph_filters import apply_graph_filters
from app.services.graphs import GraphEdge, GraphNode
from app.services.java_symbols import replace_java_symbols_for_snapshot
from app.services.js_ts_symbols import replace_js_ts_symbols_for_snapshot
from app.services.relationships import replace_structural_relations_for_snapshot
from app.services.snapshots import create_or_update_snapshot
from app.services.source_files import replace_source_files_for_snapshot
from app.services.symbols import replace_python_symbols_for_snapshot
from tests.conftest import requires_postgres

pytestmark = requires_postgres

MIXED = Path(__file__).resolve().parent / "fixtures" / "mixed_frontend_backend"
POLYGLOT = Path(__file__).resolve().parent / "fixtures" / "generic_polyglot"


@pytest.fixture()
def client(db_session: Session) -> TestClient:
    def _override() -> Session:
        return db_session

    app.dependency_overrides[get_db] = _override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _index_mixed(db_session: Session) -> Repository:
    repo = Repository(
        host="github.com",
        owner_name="rmarathe-hub",
        name=f"w8d5-{uuid4().hex[:8]}",
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
    discovery = discover_repository(MIXED)
    replace_source_files_for_snapshot(
        db_session, snapshot_id=snapshot.id, discovery=discovery
    )
    db_session.flush()
    replace_python_symbols_for_snapshot(
        db_session, snapshot_id=snapshot.id, repo_root=MIXED
    )
    replace_js_ts_symbols_for_snapshot(
        db_session, snapshot_id=snapshot.id, repo_root=MIXED
    )
    replace_java_symbols_for_snapshot(
        db_session, snapshot_id=snapshot.id, repo_root=MIXED
    )
    replace_structural_relations_for_snapshot(db_session, snapshot_id=snapshot.id)
    db_session.commit()
    return repo


def _index_polyglot(db_session: Session) -> Repository:
    repo = Repository(
        host="github.com",
        owner_name="rmarathe-hub",
        name=f"w8d5-poly-{uuid4().hex[:8]}",
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


def test_apply_graph_filters_unit() -> None:
    nodes = [
        GraphNode("a", "a", "module", "python", "deep", path="pkg/a.py"),
        GraphNode("b", "b", "module", "javascript", "deep", path="src/b.ts"),
        GraphNode("c", "c", "module", "go", "generic", path="cmd/c.go"),
    ]
    edges = [
        GraphEdge("a", "b", "imports", "resolved", "python"),
        GraphEdge("b", "c", "imports", "unresolved", "javascript", inferred=True),
    ]
    n, e = apply_graph_filters(nodes, edges, language="python")
    assert {x.id for x in n} == {"a"}
    assert e == []

    n2, e2 = apply_graph_filters(nodes, edges, support_level="generic")
    assert {x.id for x in n2} == {"c"}

    n3, e3 = apply_graph_filters(nodes, edges, relation_kind="imports", confidence="resolved")
    assert len(e3) == 1
    assert e3[0].source == "a"
    assert {x.id for x in n3} == {"a", "b", "c"}

    n4, e4 = apply_graph_filters(nodes, edges, max_nodes=1)
    assert len(n4) == 1
    assert len(e4) <= 1


def test_module_graph_filters_and_echo(client: TestClient, db_session: Session) -> None:
    repo = _index_mixed(db_session)
    resp = client.get(
        f"/api/v1/repositories/{repo.id}/graph/modules",
        params={
            "language": "python",
            "local_imports_only": "true",
            "max_nodes": 50,
            "max_edges": 100,
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["filters"]["language"] == "python"
    assert body["filters"]["local_imports_only"] is True
    assert body["filters"]["max_nodes"] == 50
    assert all(
        n["language"] in (None, "python") for n in body["nodes"]
    )


def test_directory_graph_path_prefix_and_relation_kind(
    client: TestClient, db_session: Session
) -> None:
    repo = _index_polyglot(db_session)
    resp = client.get(
        f"/api/v1/repositories/{repo.id}/graph/directories",
        params={"path_prefix": "docs", "relation_kind": "contains"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["filters"]["path_prefix"] == "docs"
    assert body["filters"]["relation_kind"] == "contains"
    assert body["node_count"] >= 1
    assert all(e["relation_kind"] == "contains" for e in body["edges"])
    assert all(
        n["id"].startswith("docs") or n["id"] == "docs" or n["label"].startswith("docs")
        for n in body["nodes"]
    )


def test_invalid_support_level_rejected(client: TestClient, db_session: Session) -> None:
    repo = _index_mixed(db_session)
    resp = client.get(
        f"/api/v1/repositories/{repo.id}/graph/modules",
        params={"support_level": "verified"},
    )
    assert resp.status_code == 422
