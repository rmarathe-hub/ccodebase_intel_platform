"""Unit and integration tests for the PostgreSQL job queue."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy import update
from sqlalchemy.orm import Session

from app.models import IndexingJob, JobStatus, Repository
from app.services.job_queue import (
    claim_next_job,
    find_active_job_for_repository,
    heartbeat_job,
    recover_expired_leases,
    schedule_retry,
)
from app.services.jobs import new_indexing_job
from tests.conftest import requires_postgres

pytestmark = requires_postgres


def _clear_open_jobs(session: Session) -> None:
    session.execute(
        update(IndexingJob)
        .where(IndexingJob.status.in_((JobStatus.QUEUED, JobStatus.RUNNING)))
        .values(
            status=JobStatus.CANCELLED,
            locked_by=None,
            locked_until=None,
        )
    )
    session.commit()


def _seed_repo(session: Session) -> Repository:
    repo = Repository(
        host="github.com",
        owner_name="rmarathe-hub",
        name=f"retail-retention-revenue-intel-{uuid4().hex[:8]}",
        default_branch="main",
        clone_url="https://github.com/rmarathe-hub/retail-retention-revenue-intel.git",
    )
    session.add(repo)
    session.flush()
    return repo


def test_claim_next_job_skip_locked(db_session: Session) -> None:
    _clear_open_jobs(db_session)
    repo = _seed_repo(db_session)
    job = new_indexing_job(repository_id=repo.id)
    db_session.add(job)
    db_session.commit()

    claimed = claim_next_job(
        db_session,
        worker_id="worker-a",
        lease_seconds=60,
    )
    db_session.commit()

    assert claimed is not None
    assert claimed.id == job.id
    assert claimed.status == JobStatus.RUNNING
    assert claimed.locked_by == "worker-a"
    assert claimed.attempt_count == 1
    assert claimed.stage == "cloning"

    other = claim_next_job(db_session, worker_id="worker-b", lease_seconds=60)
    assert other is None or other.id != job.id


def test_heartbeat_extends_lease(db_session: Session) -> None:
    _clear_open_jobs(db_session)
    repo = _seed_repo(db_session)
    job = new_indexing_job(repository_id=repo.id)
    db_session.add(job)
    db_session.commit()

    claimed = claim_next_job(db_session, worker_id="worker-a", lease_seconds=30)
    db_session.commit()
    assert claimed is not None
    original_lease = claimed.locked_until

    updated = heartbeat_job(
        db_session,
        job_id=claimed.id,
        worker_id="worker-a",
        lease_seconds=120,
    )
    db_session.commit()
    assert updated.locked_until is not None
    assert original_lease is not None
    assert updated.locked_until > original_lease


def test_recover_expired_lease_requeues(db_session: Session) -> None:
    _clear_open_jobs(db_session)
    repo = _seed_repo(db_session)
    job = new_indexing_job(repository_id=repo.id, max_attempts=3)
    job.status = JobStatus.RUNNING
    job.attempt_count = 1
    job.locked_by = "dead-worker"
    job.locked_until = datetime.now(UTC) - timedelta(seconds=5)
    db_session.add(job)
    db_session.commit()

    recovered = recover_expired_leases(db_session, retry_delay_seconds=0)
    db_session.commit()
    assert recovered == 1

    db_session.refresh(job)
    assert job.status == JobStatus.QUEUED
    assert job.error_code == "lease_expired"

    claimed = claim_next_job(db_session, worker_id="worker-b", lease_seconds=60)
    db_session.commit()
    assert claimed is not None
    assert claimed.id == job.id
    assert claimed.locked_by == "worker-b"
    assert claimed.attempt_count == 2


def test_schedule_retry_and_idempotent_active_lookup(db_session: Session) -> None:
    _clear_open_jobs(db_session)
    repo = _seed_repo(db_session)
    job = new_indexing_job(repository_id=repo.id)
    db_session.add(job)
    db_session.commit()

    claimed = claim_next_job(db_session, worker_id="worker-a", lease_seconds=60)
    db_session.commit()
    assert claimed is not None

    active = find_active_job_for_repository(db_session, repo.id)
    assert active is not None
    assert active.id == claimed.id

    schedule_retry(
        db_session,
        claimed,
        delay_seconds=0,
        error_code="clone_timeout",
        error_message="timed out",
    )
    db_session.commit()
    db_session.refresh(claimed)
    assert claimed.status == JobStatus.QUEUED
    assert claimed.error_code == "clone_timeout"
