"""Week 5 Day 7 — mixed React frontend + Python API repository test."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.main import app
from app.models import (
    Repository,
    RepositorySnapshot,
    SnapshotStatus,
    SourceFile,
    Symbol,
    SymbolCall,
)
from app.services.discovery import discover_repository
from app.services.java_symbols import replace_java_symbols_for_snapshot
from app.services.js_ts_symbols import replace_js_ts_symbols_for_snapshot
from app.services.snapshots import create_or_update_snapshot
from app.services.source_files import replace_source_files_for_snapshot
from app.services.symbols import replace_python_symbols_for_snapshot
from tests.conftest import requires_postgres

pytestmark = requires_postgres

FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "mixed_frontend_backend"


@pytest.fixture()
def client(db_session: Session) -> TestClient:
    def _override() -> Session:
        return db_session

    app.dependency_overrides[get_db] = _override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _index_fixture(
    db_session: Session,
) -> tuple[Repository, RepositorySnapshot, tuple[int, int, int, int, int, int, int, int]]:
    repo = Repository(
        host="github.com",
        owner_name="rmarathe-hub",
        name=f"mixed-{uuid4().hex[:8]}",
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
    discovery = discover_repository(FIXTURE_ROOT)
    replace_source_files_for_snapshot(
        db_session, snapshot_id=snapshot.id, discovery=discovery
    )
    db_session.flush()

    py_files, py_syms, py_calls = replace_python_symbols_for_snapshot(
        db_session, snapshot_id=snapshot.id, repo_root=FIXTURE_ROOT
    )
    js_files, js_syms, js_calls = replace_js_ts_symbols_for_snapshot(
        db_session, snapshot_id=snapshot.id, repo_root=FIXTURE_ROOT
    )
    java_files, java_syms, _java_rels = replace_java_symbols_for_snapshot(
        db_session, snapshot_id=snapshot.id, repo_root=FIXTURE_ROOT
    )
    db_session.commit()
    return (
        repo,
        snapshot,
        (py_files, py_syms, py_calls, js_files, js_syms, js_calls, java_files, java_syms),
    )


def test_mixed_fixture_discovery_shape() -> None:
    result = discover_repository(FIXTURE_ROOT)
    paths = {f.path for f in result.files}
    assert "backend/main.py" in paths
    assert "backend/services.py" in paths
    assert "backend/models.py" in paths
    assert "frontend/App.tsx" in paths
    assert "frontend/lib/helpers.ts" in paths
    assert "backend/Main.java" in paths
    assert result.deep_count >= 6


def test_mixed_frontend_backend_index_and_api(
    client: TestClient, db_session: Session
) -> None:
    repo, snapshot, counts = _index_fixture(db_session)
    py_files, py_syms, py_calls, js_files, js_syms, js_calls, java_files_n, java_syms = (
        counts
    )

    assert py_files >= 3
    assert js_files >= 2
    assert java_files_n >= 1
    assert py_syms >= 4
    assert js_syms >= 4
    assert java_syms >= 1
    assert py_calls >= 1
    assert js_calls >= 1

    symbols = list(
        db_session.scalars(select(Symbol).where(Symbol.snapshot_id == snapshot.id)).all()
    )
    langs = {s.language for s in symbols}
    assert "python" in langs
    assert "typescript" in langs
    assert "java" in langs
    assert any(s.framework_role == "fastapi_route" and s.name == "get_item" for s in symbols)
    assert any(s.framework_role == "pydantic_model" and s.name == "Item" for s in symbols)
    assert any(s.framework_role == "react_component" and s.name == "Badge" for s in symbols)
    assert any(s.framework_role == "react_component" and s.name == "App" for s in symbols)

    calls = list(
        db_session.scalars(
            select(SymbolCall).where(SymbolCall.snapshot_id == snapshot.id)
        ).all()
    )
    assert any(c.language == "python" and c.confidence == "resolved" for c in calls)
    assert any(c.language == "typescript" and c.confidence == "resolved" for c in calls)
    assert any(
        c.raw_callee == "compute_score" and c.confidence == "resolved" for c in calls
    )
    assert any(
        c.raw_callee == "formatTitle" and c.confidence == "resolved" for c in calls
    )

    # Java is DEEP and stamped when parse succeeds.
    java_files = list(
        db_session.scalars(
            select(SourceFile).where(
                SourceFile.snapshot_id == snapshot.id,
                SourceFile.language == "java",
            )
        ).all()
    )
    assert java_files
    assert any(f.parser_name == "java-treesitter" for f in java_files)
    assert any(s.language == "java" and s.name == "Main" for s in symbols)

    # API surfaces both stacks.
    all_syms = client.get(f"/api/v1/repositories/{repo.id}/symbols", params={"limit": 200})
    assert all_syms.status_code == 200
    body = all_syms.json()
    assert body["total"] >= py_syms + js_syms - 2  # room for shared names
    api_langs = {s["language"] for s in body["symbols"]}
    assert "python" in api_langs
    assert "typescript" in api_langs
    assert "java" in api_langs

    fastapi = client.get(
        f"/api/v1/repositories/{repo.id}/symbols",
        params={"framework_role": "fastapi_route"},
    )
    assert fastapi.status_code == 200
    assert fastapi.json()["total"] >= 1
    assert all(s["framework_role"] == "fastapi_route" for s in fastapi.json()["symbols"])

    react = client.get(
        f"/api/v1/repositories/{repo.id}/symbols",
        params={"framework_role": "react_component"},
    )
    assert react.status_code == 200
    assert react.json()["total"] >= 1
    assert all(s["framework_role"] == "react_component" for s in react.json()["symbols"])

    backend_prefix = client.get(
        f"/api/v1/repositories/{repo.id}/symbols",
        params={"path_prefix": "backend/"},
    )
    assert backend_prefix.status_code == 200
    assert backend_prefix.json()["total"] >= 1
    assert all(s["path"].startswith("backend/") for s in backend_prefix.json()["symbols"])

    frontend_prefix = client.get(
        f"/api/v1/repositories/{repo.id}/symbols",
        params={"path_prefix": "frontend/"},
    )
    assert frontend_prefix.status_code == 200
    assert frontend_prefix.json()["total"] >= 1
    assert all(
        s["path"].startswith("frontend/") for s in frontend_prefix.json()["symbols"]
    )

    calls_api = client.get(
        f"/api/v1/repositories/{repo.id}/calls",
        params={"confidence": "resolved", "limit": 200},
    )
    assert calls_api.status_code == 200
    assert calls_api.json()["total"] >= 2
    call_langs = {c["language"] for c in calls_api.json()["calls"]}
    assert "python" in call_langs
    assert "typescript" in call_langs

    # Language-scoped replace must not clobber the other stack.
    replace_python_symbols_for_snapshot(
        db_session, snapshot_id=snapshot.id, repo_root=FIXTURE_ROOT
    )
    db_session.commit()
    after_py = list(
        db_session.scalars(select(Symbol).where(Symbol.snapshot_id == snapshot.id)).all()
    )
    assert any(s.language == "typescript" and s.name == "Badge" for s in after_py)

    replace_js_ts_symbols_for_snapshot(
        db_session, snapshot_id=snapshot.id, repo_root=FIXTURE_ROOT
    )
    db_session.commit()
    after_js = list(
        db_session.scalars(select(Symbol).where(Symbol.snapshot_id == snapshot.id)).all()
    )
    assert any(s.language == "python" and s.name == "get_item" for s in after_js)
