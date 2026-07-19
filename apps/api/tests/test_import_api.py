"""API tests for repository import and job endpoints."""

from __future__ import annotations

from collections.abc import Generator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.db.deps import get_db
from app.main import create_app
from app.models import Base, IndexingJob, JobStatus, Repository
from app.services.jobs import new_indexing_job
from tests.conftest import postgres_available, requires_postgres

RETAIL_URL = "https://github.com/rmarathe-hub/retail-retention-revenue-intel"

pytestmark = requires_postgres


def _cancel_open_jobs(session: Session) -> None:
    from sqlalchemy import update

    session.execute(
        update(IndexingJob)
        .where(IndexingJob.status.in_((JobStatus.QUEUED, JobStatus.RUNNING)))
        .values(status=JobStatus.CANCELLED, locked_by=None, locked_until=None)
    )
    session.commit()


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    if not postgres_available():
        pytest.skip("PostgreSQL required for import API tests")
    engine = create_engine(settings.database_url, pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as session:
        _cancel_open_jobs(session)

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


def test_import_repository_queues_job(client: TestClient) -> None:
    response = client.post("/api/v1/repositories/import", json={"url": RETAIL_URL})
    assert response.status_code == 202, response.text
    body = response.json()
    assert body["repository"]["owner_name"] == "rmarathe-hub"
    assert body["repository"]["name"] == "retail-retention-revenue-intel"
    assert body["job"]["status"] == "QUEUED"
    assert body["job"]["stage"] == "queued"
    assert "id" in body["job"]

    job_id = body["job"]["id"]
    repo_id = body["repository"]["id"]

    get_job = client.get(f"/api/v1/jobs/{job_id}")
    assert get_job.status_code == 200
    assert get_job.json()["id"] == job_id

    listed = client.get(f"/api/v1/repositories/{repo_id}/jobs")
    assert listed.status_code == 200
    assert any(job["id"] == job_id for job in listed.json())


def test_import_is_idempotent_while_active(client: TestClient) -> None:
    first = client.post("/api/v1/repositories/import", json={"url": RETAIL_URL})
    assert first.status_code == 202
    second = client.post("/api/v1/repositories/import", json={"url": RETAIL_URL})
    assert second.status_code == 202
    assert first.json()["job"]["id"] == second.json()["job"]["id"]
    assert second.json()["created_new_job"] is False


def test_import_rejects_invalid_url(client: TestClient) -> None:
    response = client.post(
        "/api/v1/repositories/import",
        json={"url": "https://gitlab.com/foo/bar"},
    )
    assert response.status_code == 422


def test_retry_failed_job(client: TestClient) -> None:
    engine = create_engine(settings.database_url, pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    with SessionLocal() as session:
        repo = Repository(
            host="github.com",
            owner_name="rmarathe-hub",
            name=f"retry-demo-{uuid4().hex[:8]}",
            default_branch="main",
            clone_url="https://github.com/rmarathe-hub/retail-retention-revenue-intel.git",
        )
        session.add(repo)
        session.flush()
        job = new_indexing_job(repository_id=repo.id)
        job.status = JobStatus.FAILED
        job.error_code = "clone_failed"
        job.error_message = "boom"
        session.add(job)
        session.commit()
        job_id = str(job.id)

    response = client.post(f"/api/v1/jobs/{job_id}/retry")
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "QUEUED"
    assert body["attempt_count"] == 0
    assert body["error_code"] is None

    engine.dispose()
