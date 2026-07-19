"""API tests for repository list and discovered files."""

from __future__ import annotations

from collections.abc import Generator
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.db.deps import get_db
from app.main import create_app
from app.models import Base, Repository, SnapshotStatus
from app.services.discovery import discover_repository
from app.services.snapshots import create_or_update_snapshot
from app.services.source_files import replace_source_files_for_snapshot
from tests.conftest import postgres_available, requires_postgres

pytestmark = requires_postgres


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    if not postgres_available():
        pytest.skip("PostgreSQL required")
    engine = create_engine(settings.database_url, pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    def _override_db() -> Generator[Session, None, None]:
        session = SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    application = create_app()
    application.dependency_overrides[get_db] = _override_db
    with TestClient(application) as test_client:
        yield test_client
    application.dependency_overrides.clear()
    engine.dispose()


def _seed_repo_with_files(tmp_path: Path) -> str:
    (tmp_path / "app.py").write_text("print(1)\n", encoding="utf-8")
    (tmp_path / "notes.md").write_text("# n\n", encoding="utf-8")
    (tmp_path / "blob.bin").write_bytes(b"\x00\x01\x02")

    engine = create_engine(settings.database_url, pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    with SessionLocal() as session:
        repo = Repository(
            host="github.com",
            owner_name="rmarathe-hub",
            name=f"files-api-{uuid4().hex[:8]}",
            default_branch="main",
            clone_url="https://github.com/rmarathe-hub/retail-retention-revenue-intel.git",
        )
        session.add(repo)
        session.flush()
        discovery = discover_repository(tmp_path)
        snapshot = create_or_update_snapshot(
            session,
            repository_id=repo.id,
            branch="main",
            commit_sha=uuid4().hex,
            file_count=len(discovery.files),
            status=SnapshotStatus.READY,
        )
        replace_source_files_for_snapshot(
            session,
            snapshot_id=snapshot.id,
            discovery=discovery,
        )
        session.commit()
        repo_id = str(repo.id)
    engine.dispose()
    return repo_id


def test_list_repositories(client: TestClient, tmp_path: Path) -> None:
    repo_id = _seed_repo_with_files(tmp_path)
    response = client.get("/api/v1/repositories?limit=50")
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert any(item["id"] == repo_id for item in body)


def test_list_repository_files_matrix(client: TestClient, tmp_path: Path) -> None:
    repo_id = _seed_repo_with_files(tmp_path)

    all_files = client.get(f"/api/v1/repositories/{repo_id}/files")
    assert all_files.status_code == 200
    payload = all_files.json()
    assert payload["repository_id"] == repo_id
    assert payload["snapshot_id"] is not None
    assert payload["total"] >= 3
    paths = {item["path"] for item in payload["files"]}
    assert "app.py" in paths
    assert "notes.md" in paths

    deep = client.get(f"/api/v1/repositories/{repo_id}/files?support_level=deep")
    assert deep.status_code == 200
    assert all(item["support_level"] == "deep" for item in deep.json()["files"])
    assert any(item["path"] == "app.py" for item in deep.json()["files"])

    no_skip = client.get(f"/api/v1/repositories/{repo_id}/files?include_skipped=false")
    assert no_skip.status_code == 200
    assert all(item["support_level"] != "skip" for item in no_skip.json()["files"])

    prefixed = client.get(f"/api/v1/repositories/{repo_id}/files?path_prefix=app")
    assert prefixed.status_code == 200
    assert all(item["path"].startswith("app") for item in prefixed.json()["files"])


def test_files_invalid_support_level(client: TestClient, tmp_path: Path) -> None:
    repo_id = _seed_repo_with_files(tmp_path)
    response = client.get(f"/api/v1/repositories/{repo_id}/files?support_level=magic")
    assert response.status_code == 422


def test_files_repo_not_found(client: TestClient) -> None:
    response = client.get(f"/api/v1/repositories/{uuid4()}/files")
    assert response.status_code == 404


def test_openapi_includes_files_routes(client: TestClient) -> None:
    paths = client.get("/openapi.json").json()["paths"]
    assert "/api/v1/repositories" in paths
    assert "/api/v1/repositories/{repository_id}/files" in paths
