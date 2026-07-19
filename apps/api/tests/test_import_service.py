"""Import orchestration unit tests (DB-backed)."""

from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.models import JobStatus
from app.services.github_url import GitHubURLValidationError
from app.services.import_repository import (
    RepositoryImportError,
    get_or_create_repository,
    import_repository,
    retry_indexing_job,
)
from tests.conftest import requires_postgres

RETAIL = "https://github.com/rmarathe-hub/retail-retention-revenue-intel"

pytestmark = requires_postgres


def test_get_or_create_repository_idempotent(db_session: Session) -> None:
    first, created1 = get_or_create_repository(db_session, RETAIL)
    db_session.commit()
    second, created2 = get_or_create_repository(db_session, RETAIL + ".git")
    db_session.commit()
    assert first.id == second.id
    assert created1 is True or created2 is False
    assert created2 is False
    assert first.owner_name == "rmarathe-hub"
    assert first.name == "retail-retention-revenue-intel"


def test_import_creates_queued_job(db_session: Session) -> None:
    # Use unique repo name path via a distinct URL owner/name
    url = f"https://github.com/rmarathe-hub/import-unit-{uuid4().hex[:8]}"
    repo, job, created = import_repository(db_session, url)
    db_session.commit()
    assert created is True
    assert job.status == JobStatus.QUEUED
    assert job.repository_id == repo.id
    assert job.stage == "queued"
    assert job.progress_percentage == 0


def test_import_returns_active_job(db_session: Session) -> None:
    url = f"https://github.com/rmarathe-hub/import-active-{uuid4().hex[:8]}"
    _, job1, created1 = import_repository(db_session, url)
    db_session.commit()
    _, job2, created2 = import_repository(db_session, url)
    db_session.commit()
    assert created1 is True
    assert created2 is False
    assert job1.id == job2.id


def test_retry_failed_then_reject_active(db_session: Session) -> None:
    url = f"https://github.com/rmarathe-hub/import-retry-{uuid4().hex[:8]}"
    repo, job, _ = import_repository(db_session, url)
    job.status = JobStatus.FAILED
    job.error_code = "clone_failed"
    job.error_message = "boom"
    db_session.commit()

    retried = retry_indexing_job(db_session, job.id)
    db_session.commit()
    assert retried.status == JobStatus.QUEUED
    assert retried.attempt_count == 0
    assert retried.error_code is None

    with pytest.raises(RepositoryImportError) as exc:
        retry_indexing_job(db_session, job.id)
    assert exc.value.code == "job_not_retryable"


def test_retry_missing_job(db_session: Session) -> None:
    with pytest.raises(RepositoryImportError) as exc:
        retry_indexing_job(db_session, uuid4())
    assert exc.value.code == "job_not_found"


def test_import_rejects_bad_url(db_session: Session) -> None:
    with pytest.raises(GitHubURLValidationError):
        import_repository(db_session, "https://gitlab.com/a/b")
