"""API contract matrix for all implemented Week 2 routes."""

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
from app.services.jobs import new_indexing_job
from tests.conftest import postgres_available, requires_postgres

RETAIL = "https://github.com/rmarathe-hub/retail-retention-revenue-intel"

pytestmark = requires_postgres


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


def test_health_and_ready(client: TestClient) -> None:
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json() == {"status": "ok"}
    ready = client.get("/ready")
    assert ready.status_code == 200
    body = ready.json()
    assert "status" in body and "database" in body


def test_openapi_exposes_week2_paths(client: TestClient) -> None:
    response = client.get("/openapi.json")
    assert response.status_code == 200
    paths = response.json()["paths"]
    for required in (
        "/health",
        "/ready",
        "/api/v1/repositories/import",
        "/api/v1/jobs",
        "/api/v1/jobs/{job_id}",
        "/api/v1/repositories/{repository_id}/jobs",
        "/api/v1/jobs/{job_id}/retry",
    ):
        assert required in paths


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"url": None},
        {"url": ""},
        {"url": "   "},
        {"url": 123},
        {"url": ["https://github.com/a/b"]},
        {"url": {"href": RETAIL}},
        {"not_url": RETAIL},
        {"url": "https://gitlab.com/a/b"},
        {"url": "git@github.com:a/b.git"},
        {"url": "/tmp/repo"},
        {"url": "https://user:pass@github.com/a/b"},
    ],
)
def test_import_rejects_invalid_payloads(client: TestClient, payload: object) -> None:
    response = client.post("/api/v1/repositories/import", json=payload)
    assert response.status_code in {400, 422}


def test_import_rejects_malformed_json(client: TestClient) -> None:
    response = client.post(
        "/api/v1/repositories/import",
        content=b"{not-json",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 422


def test_import_rejects_wrong_content_type(client: TestClient) -> None:
    response = client.post(
        "/api/v1/repositories/import",
        content=f"url={RETAIL}".encode(),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code in {415, 422}


def test_import_success_schema(client: TestClient) -> None:
    response = client.post("/api/v1/repositories/import", json={"url": RETAIL})
    assert response.status_code == 202
    body = response.json()
    assert set(body.keys()) >= {"repository", "job", "created_new_job"}
    assert body["repository"]["owner_name"] == "rmarathe-hub"
    assert body["repository"]["name"] == "retail-retention-revenue-intel"
    assert body["job"]["status"] in {"QUEUED", "RUNNING"}
    assert "stack" not in str(body).lower()
    assert "traceback" not in str(body).lower()


def test_get_job_not_found(client: TestClient) -> None:
    missing = uuid4()
    response = client.get(f"/api/v1/jobs/{missing}")
    assert response.status_code == 404


@pytest.mark.parametrize("bad_id", ["not-a-uuid", "123", "null", "../../../etc/passwd"])
def test_get_job_invalid_id(client: TestClient, bad_id: str) -> None:
    response = client.get(f"/api/v1/jobs/{bad_id}")
    # Path traversal segments may 404 at the router; malformed UUIDs yield 422.
    assert response.status_code in {404, 422}


def test_list_jobs_limit_bounds(client: TestClient) -> None:
    assert client.get("/api/v1/jobs?limit=1").status_code == 200
    assert client.get("/api/v1/jobs?limit=200").status_code == 200
    # Out-of-range still handled without 500
    response = client.get("/api/v1/jobs?limit=99999")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_repository_jobs_not_found(client: TestClient) -> None:
    response = client.get(f"/api/v1/repositories/{uuid4()}/jobs")
    assert response.status_code == 404


def test_retry_nonexistent_job(client: TestClient) -> None:
    response = client.post(f"/api/v1/jobs/{uuid4()}/retry")
    assert response.status_code == 404
    detail = response.json()["detail"]
    assert detail["code"] == "job_not_found"


def test_retry_rejects_queued_job(client: TestClient) -> None:
    engine = create_engine(settings.database_url, pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    with SessionLocal() as session:
        repo = Repository(
            host="github.com",
            owner_name="rmarathe-hub",
            name=f"retry-queued-{uuid4().hex[:8]}",
            default_branch="main",
            clone_url=f"{RETAIL}.git",
        )
        session.add(repo)
        session.flush()
        job = new_indexing_job(repository_id=repo.id)
        session.add(job)
        session.commit()
        job_id = str(job.id)
    response = client.post(f"/api/v1/jobs/{job_id}/retry")
    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "job_not_retryable"
    engine.dispose()


def test_errors_do_not_leak_database_url(client: TestClient) -> None:
    response = client.post("/api/v1/repositories/import", json={"url": "https://gitlab.com/a/b"})
    text = response.text.lower()
    assert "codeintel:codeintel" not in text
    assert "postgresql" not in text or "url" in text  # may mention field name only
    assert settings.database_url.lower() not in text
