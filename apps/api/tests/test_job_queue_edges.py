"""Lease exhaustion and schedule_retry permanent failure paths."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy import update
from sqlalchemy.orm import Session

from app.models import IndexingJob, JobStatus, Repository
from app.services.job_queue import (
    JobQueueError,
    heartbeat_job,
    recover_expired_leases,
    schedule_retry,
)
from app.services.jobs import new_indexing_job
from tests.conftest import requires_postgres

pytestmark = requires_postgres


def _clear(session: Session) -> None:
    session.execute(
        update(IndexingJob)
        .where(IndexingJob.status.in_((JobStatus.QUEUED, JobStatus.RUNNING)))
        .values(status=JobStatus.CANCELLED, locked_by=None, locked_until=None)
    )
    session.commit()


def _repo(session: Session) -> Repository:
    repo = Repository(
        host="github.com",
        owner_name="rmarathe-hub",
        name=f"lease-{uuid4().hex[:8]}",
        default_branch="main",
        clone_url="https://github.com/rmarathe-hub/retail-retention-revenue-intel.git",
    )
    session.add(repo)
    session.flush()
    return repo


def test_recover_expired_lease_fails_when_attempts_exhausted(db_session: Session) -> None:
    _clear(db_session)
    repo = _repo(db_session)
    job = new_indexing_job(repository_id=repo.id, max_attempts=2)
    job.status = JobStatus.RUNNING
    job.attempt_count = 2
    job.locked_by = "dead"
    job.locked_until = datetime.now(UTC) - timedelta(seconds=1)
    db_session.add(job)
    db_session.commit()

    recovered = recover_expired_leases(db_session, retry_delay_seconds=0)
    db_session.commit()
    assert recovered == 1
    db_session.refresh(job)
    assert job.status == JobStatus.FAILED
    assert job.error_code == "lease_exhausted"


def test_schedule_retry_fails_at_max_attempts(db_session: Session) -> None:
    _clear(db_session)
    repo = _repo(db_session)
    job = new_indexing_job(repository_id=repo.id, max_attempts=1)
    job.status = JobStatus.RUNNING
    job.attempt_count = 1
    db_session.add(job)
    db_session.commit()

    schedule_retry(
        db_session,
        job,
        delay_seconds=0,
        error_code="clone_failed",
        error_message="permanent",
    )
    db_session.commit()
    db_session.refresh(job)
    assert job.status == JobStatus.FAILED
    assert job.error_code == "clone_failed"


def test_heartbeat_rejects_wrong_worker(db_session: Session) -> None:
    _clear(db_session)
    repo = _repo(db_session)
    job = new_indexing_job(repository_id=repo.id)
    job.status = JobStatus.RUNNING
    job.locked_by = "worker-a"
    job.locked_until = datetime.now(UTC) + timedelta(seconds=60)
    db_session.add(job)
    db_session.commit()

    try:
        heartbeat_job(db_session, job_id=job.id, worker_id="worker-b", lease_seconds=30)
        raise AssertionError("expected JobQueueError")
    except JobQueueError as exc:
        assert "not locked" in str(exc)


def test_heartbeat_rejects_missing_job(db_session: Session) -> None:
    try:
        heartbeat_job(db_session, job_id=uuid4(), worker_id="worker-a", lease_seconds=30)
        raise AssertionError("expected JobQueueError")
    except JobQueueError as exc:
        assert "not found" in str(exc)
