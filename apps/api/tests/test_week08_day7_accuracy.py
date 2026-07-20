"""Week 8 Day 7 — graph accuracy matrix.

Covers circular imports, ambiguous callees, Java implementations,
mixed-language module graphs, and large directory structures.
"""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.main import app
from app.models import Repository, SnapshotStatus, Symbol, SymbolCall
from app.services.chunking import replace_chunks_for_snapshot
from app.services.discovery import discover_repository
from app.services.java_symbols import replace_java_symbols_for_snapshot
from app.services.js_ts_symbols import replace_js_ts_symbols_for_snapshot
from app.services.relationships import replace_structural_relations_for_snapshot
from app.services.snapshots import create_or_update_snapshot
from app.services.source_files import replace_source_files_for_snapshot
from app.services.symbols import replace_python_symbols_for_snapshot
from tests.conftest import requires_postgres

pytestmark = requires_postgres

ACCURACY = Path(__file__).resolve().parent / "fixtures" / "graph_accuracy"
SPRING = Path(__file__).resolve().parent / "fixtures" / "spring_fixture"
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


def _repo(db_session: Session, name: str) -> Repository:
    repo = Repository(
        host="github.com",
        owner_name="rmarathe-hub",
        name=f"{name}-{uuid4().hex[:8]}",
        default_branch="main",
        clone_url="https://github.com/rmarathe-hub/retail-retention-revenue-intel.git",
    )
    db_session.add(repo)
    db_session.flush()
    return repo


def _snapshot(db_session: Session, repo: Repository) -> object:
    return create_or_update_snapshot(
        db_session,
        repository_id=repo.id,
        branch="main",
        commit_sha=uuid4().hex[:12],
        file_count=0,
        status=SnapshotStatus.READY,
    )


def _index_python(db_session: Session, root: Path, name: str) -> Repository:
    repo = _repo(db_session, name)
    snapshot = _snapshot(db_session, repo)
    discovery = discover_repository(root)
    replace_source_files_for_snapshot(
        db_session, snapshot_id=snapshot.id, discovery=discovery
    )
    db_session.flush()
    replace_python_symbols_for_snapshot(
        db_session, snapshot_id=snapshot.id, repo_root=root
    )
    replace_structural_relations_for_snapshot(db_session, snapshot_id=snapshot.id)
    db_session.commit()
    return repo


def _index_spring(db_session: Session) -> Repository:
    repo = _repo(db_session, "w8d7-spring")
    snapshot = _snapshot(db_session, repo)
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
    return repo


def _index_mixed(db_session: Session) -> Repository:
    repo = _repo(db_session, "w8d7-mixed")
    snapshot = _snapshot(db_session, repo)
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
    repo = _repo(db_session, "w8d7-poly")
    snapshot = _snapshot(db_session, repo)
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


def test_circular_imports_appear_in_module_graph(
    client: TestClient, db_session: Session
) -> None:
    repo = _index_python(db_session, ACCURACY, "w8d7-circ")
    resp = client.get(
        f"/api/v1/repositories/{repo.id}/graph/modules",
        params={"language": "python", "local_imports_only": "false"},
    )
    assert resp.status_code == 200
    body = resp.json()
    node_ids = {n["id"] for n in body["nodes"]}
    assert "circ.a" in node_ids
    assert "circ.b" in node_ids
    edges = {(e["source"], e["target"]) for e in body["edges"] if e["relation_kind"] == "imports"}
    # Mutual IMPORTS (cycle) — both directions present
    assert ("circ.a", "circ.b") in edges
    assert ("circ.b", "circ.a") in edges


def test_ambiguous_calls_preserved_in_call_graph(
    client: TestClient, db_session: Session
) -> None:
    repo = _index_python(db_session, ACCURACY, "w8d7-ambig")
    # Confirm ambiguous call sites were persisted
    snapshot_id = client.get(f"/api/v1/repositories/{repo.id}/graph/modules").json()[
        "snapshot_id"
    ]
    assert snapshot_id
    ambig_calls = list(
        db_session.scalars(
            select(SymbolCall).where(
                SymbolCall.snapshot_id == snapshot_id,
                SymbolCall.confidence == "ambiguous",
            )
        ).all()
    )
    assert ambig_calls, "expected ambiguous helper() calls from ambig/caller.py"

    caller = db_session.scalars(
        select(Symbol).where(
            Symbol.snapshot_id == snapshot_id,
            Symbol.name == "main",
            Symbol.qualified_name.like("%caller%"),
        )
    ).first()
    assert caller is not None

    # Unfiltered neighborhood includes the center; confidence=ambiguous filters edges
    all_graph = client.get(
        f"/api/v1/repositories/{repo.id}/graph/calls",
        params={"symbol_id": str(caller.id), "depth": 1},
    )
    assert all_graph.status_code == 200
    assert all_graph.json()["node_count"] >= 1

    ambig_graph = client.get(
        f"/api/v1/repositories/{repo.id}/graph/calls",
        params={"symbol_id": str(caller.id), "depth": 1, "confidence": "ambiguous"},
    )
    assert ambig_graph.status_code == 200
    body = ambig_graph.json()
    # Ambiguous edges may not resolve to a callee node (candidate_qname is None),
    # so edge list can be empty while calls API still reports ambiguity.
    calls_api = client.get(
        f"/api/v1/repositories/{repo.id}/calls",
        params={"confidence": "ambiguous", "limit": 50},
    )
    assert calls_api.status_code == 200
    assert calls_api.json()["total"] >= 1
    assert all(c["confidence"] == "ambiguous" for c in calls_api.json()["calls"])
    assert body["center_symbol_id"] == str(caller.id)


def test_interface_implementations_accuracy(
    client: TestClient, db_session: Session
) -> None:
    repo = _index_spring(db_session)
    iface = client.get(
        f"/api/v1/repositories/{repo.id}/symbols",
        params={"name_contains": "UserService", "kind": "interface", "limit": 20},
    )
    assert iface.status_code == 200
    # UserService may be kind interface or class depending on parser; fall back
    symbols = iface.json()["symbols"]
    if not symbols:
        all_syms = client.get(
            f"/api/v1/repositories/{repo.id}/symbols",
            params={"name_contains": "UserService", "limit": 50},
        ).json()["symbols"]
        symbols = [s for s in all_syms if s["name"] == "UserService"]
    assert symbols
    iface_id = next(s["id"] for s in symbols if s["name"] == "UserService")

    impl = client.get(
        f"/api/v1/repositories/{repo.id}/symbols/{iface_id}/implementations"
    )
    assert impl.status_code == 200
    body = impl.json()
    assert body["total"] >= 1
    names = {i["name"] for i in body["implementations"]}
    assert "UserServiceImpl" in names
    assert all(i["relation_kind"] == "implements" for i in body["implementations"])
    assert all(i["confidence"] == "resolved" for i in body["implementations"])

    # Package graph for Java should include demo.user package nodes
    pkgs = client.get(
        f"/api/v1/repositories/{repo.id}/graph/packages",
        params={"language": "java", "local_imports_only": "false"},
    )
    assert pkgs.status_code == 200
    assert pkgs.json()["node_count"] >= 1


def test_mixed_language_module_graph_honesty(
    client: TestClient, db_session: Session
) -> None:
    repo = _index_mixed(db_session)
    resp = client.get(
        f"/api/v1/repositories/{repo.id}/graph/modules",
        params={"local_imports_only": "true", "max_nodes": 200},
    )
    assert resp.status_code == 200
    body = resp.json()
    langs = {n["language"] for n in body["nodes"] if n["language"]}
    assert "python" in langs
    assert langs & {"javascript", "typescript"}
    # Every node is deep — no generic pollution in module graph
    assert all(n["support_level"] == "deep" for n in body["nodes"])
    assert all(e["relation_kind"] == "imports" for e in body["edges"])

    py_only = client.get(
        f"/api/v1/repositories/{repo.id}/graph/modules",
        params={"language": "python", "local_imports_only": "true"},
    )
    assert py_only.status_code == 200
    assert all(
        n["language"] in (None, "python") for n in py_only.json()["nodes"]
    )


def test_large_directory_structure_polyglot(
    client: TestClient, db_session: Session
) -> None:
    repo = _index_polyglot(db_session)
    resp = client.get(
        f"/api/v1/repositories/{repo.id}/graph/directories",
        params={"include_files": "false", "max_nodes": 500},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["node_count"] >= 8
    dir_ids = {n["id"] for n in body["nodes"] if n["node_type"] == "directory"}
    # Multiple top-level dirs from the polyglot fixture
    expected_dirs = {"cmd", "docs", "ruby", "scripts", "src", "c", "cpp", "csharp", "db"}
    assert len(dir_ids & expected_dirs) >= 5
    contains = [e for e in body["edges"] if e["relation_kind"] == "contains"]
    assert len(contains) >= 5
    # No fake deep call edges on a generic-heavy repo directory graph
    assert all(e["relation_kind"] != "calls" for e in body["edges"])
    assert all(n.get("symbol_id") is None for n in body["nodes"])

    # Caps work under "large" graph pressure
    capped = client.get(
        f"/api/v1/repositories/{repo.id}/graph/directories",
        params={"max_nodes": 3},
    )
    assert capped.status_code == 200
    assert capped.json()["node_count"] <= 3
    assert capped.json()["filters"]["max_nodes"] == 3


def test_graph_accuracy_matrix_rollup(
    client: TestClient, db_session: Session
) -> None:
    """Single rollup asserting Day 7 scenarios all remain available via APIs."""
    circ = _index_python(db_session, ACCURACY, "w8d7-roll-circ")
    spring = _index_spring(db_session)
    mixed = _index_mixed(db_session)
    poly = _index_polyglot(db_session)

    checks = {
        "circular_modules": client.get(
            f"/api/v1/repositories/{circ.id}/graph/modules",
            params={"language": "python"},
        ),
        "spring_packages": client.get(
            f"/api/v1/repositories/{spring.id}/graph/packages",
            params={"language": "java"},
        ),
        "mixed_modules": client.get(
            f"/api/v1/repositories/{mixed.id}/graph/modules",
            params={"local_imports_only": "true"},
        ),
        "poly_directories": client.get(
            f"/api/v1/repositories/{poly.id}/graph/directories"
        ),
    }
    for name, resp in checks.items():
        assert resp.status_code == 200, name
        assert resp.json()["node_count"] >= 1, name
