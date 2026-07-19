"""Extra coverage for error branches and helpers."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy import update
from sqlalchemy.orm import Session

from app.models import IndexingJob, JobStatus, Repository
from app.schemas.repositories import ParsedRepositoryURL
from app.services.github_url import (
    GitHubURLValidationError,
    parse_github_repository_url,
)
from app.services.import_repository import (
    RepositoryImportError,
    import_repository,
    retry_indexing_job,
)
from app.services.job_queue import JobQueueError, get_repository_for_job, heartbeat_job
from app.services.jobs import new_indexing_job
from tests.conftest import requires_postgres

pytestmark = requires_postgres


def test_parse_rejects_none_url() -> None:
    with pytest.raises(GitHubURLValidationError) as exc:
        parse_github_repository_url(None)  # type: ignore[arg-type]
    assert exc.value.code == "empty_url"


def test_parsed_repository_url_schema_roundtrip() -> None:
    parsed = parse_github_repository_url(
        "https://github.com/rmarathe-hub/retail-retention-revenue-intel"
    )
    model = ParsedRepositoryURL.from_parsed(parsed)
    assert model.full_name == "rmarathe-hub/retail-retention-revenue-intel"
    assert model.clone_url.endswith(".git")


def test_heartbeat_rejects_non_running_job(db_session: Session) -> None:
    db_session.execute(
        update(IndexingJob)
        .where(IndexingJob.status.in_((JobStatus.QUEUED, JobStatus.RUNNING)))
        .values(status=JobStatus.CANCELLED, locked_by=None, locked_until=None)
    )
    db_session.commit()
    repo = Repository(
        host="github.com",
        owner_name="rmarathe-hub",
        name=f"hb-{uuid4().hex[:8]}",
        default_branch="main",
        clone_url="https://github.com/rmarathe-hub/retail-retention-revenue-intel.git",
    )
    db_session.add(repo)
    db_session.flush()
    job = new_indexing_job(repository_id=repo.id)
    db_session.add(job)
    db_session.commit()
    with pytest.raises(JobQueueError, match="not running"):
        heartbeat_job(db_session, job_id=job.id, worker_id="w", lease_seconds=30)


def test_get_repository_for_job(db_session: Session) -> None:
    repo = Repository(
        host="github.com",
        owner_name="rmarathe-hub",
        name=f"getrepo-{uuid4().hex[:8]}",
        default_branch="main",
        clone_url="https://github.com/rmarathe-hub/retail-retention-revenue-intel.git",
    )
    db_session.add(repo)
    db_session.flush()
    job = new_indexing_job(repository_id=repo.id)
    db_session.add(job)
    db_session.commit()
    found = get_repository_for_job(db_session, job)
    assert found.id == repo.id

    orphan = new_indexing_job(repository_id=uuid4())
    with pytest.raises(JobQueueError, match="not found"):
        get_repository_for_job(db_session, orphan)


def test_retry_blocked_when_other_job_active(db_session: Session) -> None:
    url = f"https://github.com/rmarathe-hub/retry-block-{uuid4().hex[:8]}"
    repo, failed, _ = import_repository(db_session, url)
    failed.status = JobStatus.FAILED
    failed.error_code = "clone_failed"
    failed.error_message = "boom"
    db_session.flush()
    # Second active job for same repo
    active = new_indexing_job(repository_id=repo.id)
    db_session.add(active)
    db_session.commit()
    with pytest.raises(RepositoryImportError) as exc:
        retry_indexing_job(db_session, failed.id)
    assert exc.value.code == "job_already_active"


def test_mark_job_running_preserves_started_at() -> None:
    from app.services.jobs import mark_job_running

    job = new_indexing_job(repository_id=uuid4())
    started = datetime.now(UTC) - timedelta(minutes=5)
    job.started_at = started
    job.stage = "cloning"
    mark_job_running(
        job,
        worker_id="w",
        lease_until=datetime.now(UTC) + timedelta(seconds=30),
    )
    assert job.started_at == started
