"""Week 11 Days 3–4: cancel + reindex API."""

from __future__ import annotations

from collections.abc import Generator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, update
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.db.deps import get_db
from app.main import create_app
from app.models import Base, IndexingJob, JobStatus, Repository
from app.services.import_repository import cancel_indexing_job, reindex_repository
from app.services.jobs import mark_job_running, new_indexing_job
from tests.conftest import postgres_available, requires_postgres

pytestmark = requires_postgres

RETAIL = "https://github.com/rmarathe-hub/retail-retention-revenue-intel"


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    if not postgres_available():
        pytest.skip("PostgreSQL required")
    engine = create_engine(settings.database_url, pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as session:
        session.execute(
            update(IndexingJob)
            .where(IndexingJob.status.in_((JobStatus.QUEUED, JobStatus.RUNNING)))
            .values(status=JobStatus.CANCELLED, locked_by=None, locked_until=None)
        )
        session.commit()

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


def test_cancel_queued_job(client: TestClient) -> None:
    imported = client.post("/api/v1/repositories/import", json={"url": RETAIL})
    assert imported.status_code == 202
    job_id = imported.json()["job"]["id"]

    cancelled = client.post(f"/api/v1/jobs/{job_id}/cancel")
    assert cancelled.status_code == 200
    body = cancelled.json()
    assert body["status"] == "CANCELLED"
    assert body["error_code"] == "cancelled"

    again = client.post(f"/api/v1/jobs/{job_id}/cancel")
    assert again.status_code == 200
    assert again.json()["status"] == "CANCELLED"


def test_cancel_rejects_succeeded(client: TestClient) -> None:
    engine = create_engine(settings.database_url, pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    with SessionLocal() as session:
        repo = Repository(
            host="github.com",
            owner_name="t",
            name=f"cancel-{uuid4().hex[:8]}",
            default_branch="main",
            clone_url="https://github.com/t/t.git",
        )
        session.add(repo)
        session.flush()
        job = new_indexing_job(repository_id=repo.id)
        job.status = JobStatus.SUCCEEDED
        session.add(job)
        session.commit()
        job_id = str(job.id)

    response = client.post(f"/api/v1/jobs/{job_id}/cancel")
    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "job_not_cancellable"
    engine.dispose()


def test_reindex_queues_new_job(client: TestClient) -> None:
    imported = client.post("/api/v1/repositories/import", json={"url": RETAIL})
    assert imported.status_code == 202
    repo_id = imported.json()["repository"]["id"]
    job_id = imported.json()["job"]["id"]

    # Free the active job so reindex can create a new one.
    cancel = client.post(f"/api/v1/jobs/{job_id}/cancel")
    assert cancel.status_code == 200

    reindexed = client.post(f"/api/v1/repositories/{repo_id}/reindex")
    assert reindexed.status_code == 202
    body = reindexed.json()
    assert body["created_new_job"] is True
    assert body["repository"]["id"] == repo_id
    assert body["job"]["status"] == "QUEUED"
    assert body["job"]["id"] != job_id


def test_reindex_returns_active_job(client: TestClient) -> None:
    imported = client.post("/api/v1/repositories/import", json={"url": RETAIL})
    assert imported.status_code == 202
    repo_id = imported.json()["repository"]["id"]
    job_id = imported.json()["job"]["id"]

    again = client.post(f"/api/v1/repositories/{repo_id}/reindex")
    assert again.status_code == 202
    body = again.json()
    assert body["created_new_job"] is False
    assert body["job"]["id"] == job_id


def test_cancel_and_reindex_service_helpers() -> None:
    if not postgres_available():
        pytest.skip("PostgreSQL required")
    engine = create_engine(settings.database_url, pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    with SessionLocal() as session:
        session.execute(
            update(IndexingJob)
            .where(IndexingJob.status.in_((JobStatus.QUEUED, JobStatus.RUNNING)))
            .values(status=JobStatus.CANCELLED, locked_by=None, locked_until=None)
        )
        session.commit()

        repo = Repository(
            host="github.com",
            owner_name="t",
            name=f"svc-{uuid4().hex[:8]}",
            default_branch="main",
            clone_url="https://github.com/t/svc.git",
        )
        session.add(repo)
        session.flush()
        job = new_indexing_job(repository_id=repo.id)
        session.add(job)
        session.commit()

        from datetime import UTC, datetime, timedelta

        mark_job_running(
            job,
            worker_id="test-worker",
            lease_until=datetime.now(UTC) + timedelta(minutes=5),
        )
        session.commit()

        cancelled = cancel_indexing_job(session, job.id)
        assert cancelled.status == JobStatus.CANCELLED

        repo2, job2, created = reindex_repository(session, repo.id)
        assert created is True
        assert repo2.id == repo.id
        assert job2.status == JobStatus.QUEUED
    engine.dispose()
