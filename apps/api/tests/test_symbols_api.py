"""API tests for repository symbols listing."""

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
from app.services.snapshots import create_or_update_snapshot
from app.services.source_files import replace_source_files_for_snapshot
from app.services.symbols import replace_python_symbols_for_snapshot
from tests.conftest import postgres_available, requires_postgres

pytestmark = requires_postgres


@pytest.fixture()
def client(db_session: Session) -> TestClient:
    def _override() -> Session:
        return db_session

    app.dependency_overrides[get_db] = _override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_list_symbols_api(client: TestClient, db_session: Session, tmp_path: Path) -> None:
    (tmp_path / "svc.py").write_text(
        "class Service:\n"
        "    def start(self):\n"
        "        pass\n\n"
        "def build():\n"
        "    return Service()\n",
        encoding="utf-8",
    )
    repo = Repository(
        host="github.com",
        owner_name="rmarathe-hub",
        name=f"sym-api-{uuid4().hex[:8]}",
        default_branch="main",
        clone_url="https://github.com/rmarathe-hub/retail-retention-revenue-intel.git",
    )
    db_session.add(repo)
    db_session.flush()
    snapshot = create_or_update_snapshot(
        db_session,
        repository_id=repo.id,
        branch="main",
        commit_sha="api123",
        file_count=1,
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
    db_session.commit()

    empty = client.get(f"/api/v1/repositories/{uuid4()}/symbols")
    assert empty.status_code == 404

    all_resp = client.get(f"/api/v1/repositories/{repo.id}/symbols")
    assert all_resp.status_code == 200
    body = all_resp.json()
    assert body["snapshot_id"] == str(snapshot.id)
    assert body["total"] >= 3
    assert any(s["kind"] == "class" for s in body["symbols"])

    filtered = client.get(
        f"/api/v1/repositories/{repo.id}/symbols",
        params={"kind": "method", "name_contains": "start"},
    )
    assert filtered.status_code == 200
    assert filtered.json()["total"] >= 1
    assert all(s["kind"] == "method" for s in filtered.json()["symbols"])

    bad_kind = client.get(
        f"/api/v1/repositories/{repo.id}/symbols",
        params={"kind": "heuristic"},
    )
    assert bad_kind.status_code == 422


def test_symbols_empty_without_snapshot(client: TestClient, db_session: Session) -> None:
    if not postgres_available():
        pytest.skip("PostgreSQL required")
    repo = Repository(
        host="github.com",
        owner_name="rmarathe-hub",
        name=f"nosnap-{uuid4().hex[:8]}",
        default_branch="main",
        clone_url="https://github.com/rmarathe-hub/retail-retention-revenue-intel.git",
    )
    db_session.add(repo)
    db_session.commit()
    resp = client.get(f"/api/v1/repositories/{repo.id}/symbols")
    assert resp.status_code == 200
    assert resp.json()["total"] == 0
    assert resp.json()["symbols"] == []
