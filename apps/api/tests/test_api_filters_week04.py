"""API filter matrices for files / symbols / calls (Week 3–4)."""

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


def _seed_python_repo(
    db_session: Session,
    tmp_path: Path,
    *,
    source: str,
    relpath: str = "pkg/svc.py",
) -> Repository:
    target = tmp_path / relpath
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(source, encoding="utf-8")
    (tmp_path / "README.md").write_text("# demo\n", encoding="utf-8")
    (tmp_path / ".env.example").write_text("X=1\n", encoding="utf-8")

    repo = Repository(
        host="github.com",
        owner_name="rmarathe-hub",
        name=f"filt-{uuid4().hex[:8]}",
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
    db_session.commit()
    return repo


RICH_SOURCE = '''\
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class Item(BaseModel):
    id: int

def helper():
    return 1

@router.get("/items")
def list_items():
    return helper()
'''


def test_files_filter_matrix(client: TestClient, db_session: Session, tmp_path: Path) -> None:
    repo = _seed_python_repo(db_session, tmp_path, source=RICH_SOURCE)

    deep = client.get(
        f"/api/v1/repositories/{repo.id}/files",
        params={"support_level": "deep"},
    )
    assert deep.status_code == 200
    assert deep.json()["total"] >= 1
    assert all(f["support_level"] == "deep" for f in deep.json()["files"])

    skipped = client.get(
        f"/api/v1/repositories/{repo.id}/files",
        params={"include_skipped": True, "support_level": "skip"},
    )
    assert skipped.status_code == 200
    assert skipped.json()["total"] >= 1

    noskip = client.get(
        f"/api/v1/repositories/{repo.id}/files",
        params={"include_skipped": False},
    )
    assert noskip.status_code == 200
    assert all(f["support_level"] != "skip" for f in noskip.json()["files"])

    prefix = client.get(
        f"/api/v1/repositories/{repo.id}/files",
        params={"path_prefix": "pkg"},
    )
    assert prefix.status_code == 200
    assert all(f["path"].startswith("pkg") for f in prefix.json()["files"])

    bad = client.get(
        f"/api/v1/repositories/{repo.id}/files",
        params={"support_level": "magic"},
    )
    assert bad.status_code == 422


def test_symbols_filter_matrix(client: TestClient, db_session: Session, tmp_path: Path) -> None:
    repo = _seed_python_repo(db_session, tmp_path, source=RICH_SOURCE)

    routes = client.get(
        f"/api/v1/repositories/{repo.id}/symbols",
        params={"framework_role": "fastapi_route"},
    )
    assert routes.status_code == 200
    assert routes.json()["total"] >= 1
    assert all(s["framework_role"] == "fastapi_route" for s in routes.json()["symbols"])

    models = client.get(
        f"/api/v1/repositories/{repo.id}/symbols",
        params={"framework_role": "pydantic_model"},
    )
    assert models.status_code == 200
    assert models.json()["total"] >= 1

    path = client.get(
        f"/api/v1/repositories/{repo.id}/symbols",
        params={"path_prefix": "pkg"},
    )
    assert path.status_code == 200
    assert path.json()["total"] >= 1

    bad_role = client.get(
        f"/api/v1/repositories/{repo.id}/symbols",
        params={"framework_role": "express_route"},
    )
    assert bad_role.status_code == 422

    local = client.get(
        f"/api/v1/repositories/{repo.id}/symbols",
        params={"kind": "import", "is_local_import": False},
    )
    assert local.status_code == 200


def test_calls_filter_matrix(client: TestClient, db_session: Session, tmp_path: Path) -> None:
    repo = _seed_python_repo(db_session, tmp_path, source=RICH_SOURCE)

    all_calls = client.get(f"/api/v1/repositories/{repo.id}/calls")
    assert all_calls.status_code == 200
    assert all_calls.json()["total"] >= 1

    resolved = client.get(
        f"/api/v1/repositories/{repo.id}/calls",
        params={"confidence": "resolved"},
    )
    assert resolved.status_code == 200
    assert all(c["confidence"] == "resolved" for c in resolved.json()["calls"])

    unresolved = client.get(
        f"/api/v1/repositories/{repo.id}/calls",
        params={"confidence": "unresolved"},
    )
    assert unresolved.status_code == 200

    ambiguous = client.get(
        f"/api/v1/repositories/{repo.id}/calls",
        params={"confidence": "ambiguous"},
    )
    assert ambiguous.status_code == 200

    caller = client.get(
        f"/api/v1/repositories/{repo.id}/calls",
        params={"caller_contains": "list_items"},
    )
    assert caller.status_code == 200
    assert caller.json()["total"] >= 1

    prefix = client.get(
        f"/api/v1/repositories/{repo.id}/calls",
        params={"path_prefix": "pkg"},
    )
    assert prefix.status_code == 200

    for bad in ("maybe", "kinda"):
        resp = client.get(
            f"/api/v1/repositories/{repo.id}/calls",
            params={"confidence": bad},
        )
        assert resp.status_code == 422

    # Case-insensitive accept (API lowercases before validation).
    upper = client.get(
        f"/api/v1/repositories/{repo.id}/calls",
        params={"confidence": "RESOLVED"},
    )
    assert upper.status_code == 200
    assert all(c["confidence"] == "resolved" for c in upper.json()["calls"])


def test_neighbors_and_security_strings(
    client: TestClient, db_session: Session, tmp_path: Path
) -> None:
    repo = _seed_python_repo(db_session, tmp_path, source=RICH_SOURCE)
    symbols = client.get(f"/api/v1/repositories/{repo.id}/symbols").json()["symbols"]
    helper = next(s for s in symbols if s["name"] == "helper")
    list_items = next(s for s in symbols if s["name"] == "list_items")

    callers = client.get(
        f"/api/v1/repositories/{repo.id}/symbols/{helper['id']}/callers"
    )
    assert callers.status_code == 200
    assert callers.json()["direction"] == "callers"
    assert callers.json()["total"] >= 1

    callees = client.get(
        f"/api/v1/repositories/{repo.id}/symbols/{list_items['id']}/callees"
    )
    assert callees.status_code == 200
    assert callees.json()["direction"] == "callees"

    missing = client.get(
        f"/api/v1/repositories/{repo.id}/symbols/{uuid4()}/callers"
    )
    assert missing.status_code == 404

    # Injection-like filters must not 500 or leak stacks.
    for value in (
        "'; DROP TABLE symbols;--",
        "<script>alert(1)</script>",
        "../../etc/passwd",
        "a" * 5000,
    ):
        resp = client.get(
            f"/api/v1/repositories/{repo.id}/symbols",
            params={"name_contains": value},
        )
        assert resp.status_code == 200
        body = resp.text.lower()
        assert "traceback" not in body
        assert "psycopg" not in body


def test_openapi_lists_week4_routes(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()
    paths = schema["paths"]
    assert "/api/v1/repositories/{repository_id}/calls" in paths
    assert "/api/v1/repositories/{repository_id}/symbols/{symbol_id}/callers" in paths
    assert "/api/v1/repositories/{repository_id}/symbols/{symbol_id}/callees" in paths
    # Honesty: Search/Ask not implemented.
    assert "/api/v1/search" not in paths
    assert "/api/v1/ask" not in paths
