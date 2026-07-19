"""API tests for repository call listing."""

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
from tests.conftest import requires_postgres

pytestmark = requires_postgres


@pytest.fixture()
def client(db_session: Session) -> TestClient:
    def _override() -> Session:
        return db_session

    app.dependency_overrides[get_db] = _override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_list_calls_api(client: TestClient, db_session: Session, tmp_path: Path) -> None:
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
        name=f"calls-api-{uuid4().hex[:8]}",
        default_branch="main",
        clone_url="https://github.com/rmarathe-hub/retail-retention-revenue-intel.git",
    )
    db_session.add(repo)
    db_session.flush()
    snapshot = create_or_update_snapshot(
        db_session,
        repository_id=repo.id,
        branch="main",
        commit_sha="call123",
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

    resp = client.get(f"/api/v1/repositories/{repo.id}/calls")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] >= 1
    assert any(c["confidence"] == "resolved" for c in body["calls"])

    filtered = client.get(
        f"/api/v1/repositories/{repo.id}/calls",
        params={"confidence": "resolved"},
    )
    assert filtered.status_code == 200
    assert all(c["confidence"] == "resolved" for c in filtered.json()["calls"])

    bad = client.get(
        f"/api/v1/repositories/{repo.id}/calls",
        params={"confidence": "maybe"},
    )
    assert bad.status_code == 422
