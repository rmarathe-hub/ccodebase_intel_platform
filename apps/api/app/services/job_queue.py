"""PostgreSQL-backed job queue using FOR UPDATE SKIP LOCKED."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.entities import IndexingJob, JobStatus, Repository
from app.models.job_stages import JobStage
from app.services.jobs import mark_job_failed, mark_job_running, set_job_stage


class JobQueueError(RuntimeError):
    """Raised when a queue operation cannot be completed safely."""


def _utcnow() -> datetime:
    return datetime.now(UTC)


def recover_expired_leases(
    session: Session,
    *,
    now: datetime | None = None,
    retry_delay_seconds: int = 30,
) -> int:
    """Re-queue or fail jobs whose worker lease has expired.

    Returns the number of recovered jobs.
    """
    current = now or _utcnow()
    stmt = (
        select(IndexingJob)
        .where(
            IndexingJob.status == JobStatus.RUNNING,
            IndexingJob.locked_until.is_not(None),
            IndexingJob.locked_until < current,
        )
        .with_for_update(skip_locked=True)
    )
    recovered = 0
    for job in session.scalars(stmt).all():
        if job.attempt_count >= job.max_attempts:
            mark_job_failed(
                job,
                error_code="lease_exhausted",
                error_message="Worker lease expired and max attempts reached",
            )
        else:
            job.status = JobStatus.QUEUED
            job.locked_by = None
            job.locked_until = current + timedelta(seconds=retry_delay_seconds)
            job.heartbeat_at = current
            job.error_code = "lease_expired"
            job.error_message = "Worker lease expired; job re-queued"
            set_job_stage(job, JobStage.QUEUED)
        recovered += 1
    if recovered:
        session.flush()
    return recovered


def claim_next_job(
    session: Session,
    *,
    worker_id: str,
    lease_seconds: int = 60,
    retry_delay_seconds: int = 30,
    now: datetime | None = None,
) -> IndexingJob | None:
    """Claim the next available queued job using SKIP LOCKED."""
    current = now or _utcnow()
    recover_expired_leases(
        session,
        now=current,
        retry_delay_seconds=retry_delay_seconds,
    )

    stmt = (
        select(IndexingJob)
        .where(
            IndexingJob.status == JobStatus.QUEUED,
            or_(
                IndexingJob.locked_until.is_(None),
                IndexingJob.locked_until <= current,
            ),
        )
        .order_by(IndexingJob.created_at.asc())
        .limit(1)
        .with_for_update(skip_locked=True)
    )
    job = session.scalars(stmt).first()
    if job is None:
        return None

    lease_until = current + timedelta(seconds=lease_seconds)
    mark_job_running(job, worker_id=worker_id, lease_until=lease_until)
    session.flush()
    return job


def heartbeat_job(
    session: Session,
    *,
    job_id: UUID,
    worker_id: str,
    lease_seconds: int = 60,
    now: datetime | None = None,
) -> IndexingJob:
    """Extend the lease for a job owned by this worker."""
    current = now or _utcnow()
    stmt = select(IndexingJob).where(IndexingJob.id == job_id).with_for_update()
    job = session.scalars(stmt).first()
    if job is None:
        raise JobQueueError(f"Job {job_id} not found")
    if job.status != JobStatus.RUNNING:
        raise JobQueueError(f"Job {job_id} is not running")
    if job.locked_by != worker_id:
        raise JobQueueError(f"Job {job_id} is not locked by {worker_id}")

    job.heartbeat_at = current
    job.locked_until = current + timedelta(seconds=lease_seconds)
    session.flush()
    return job


def schedule_retry(
    session: Session,
    job: IndexingJob,
    *,
    delay_seconds: int,
    error_code: str,
    error_message: str,
    now: datetime | None = None,
) -> IndexingJob:
    """Return a failed attempt to the queue after a delay, or permanently fail."""
    current = now or _utcnow()
    if job.attempt_count >= job.max_attempts:
        mark_job_failed(job, error_code=error_code, error_message=error_message)
    else:
        job.status = JobStatus.QUEUED
        job.locked_by = None
        job.locked_until = current + timedelta(seconds=delay_seconds)
        job.heartbeat_at = current
        job.error_code = error_code
        job.error_message = error_message
        job.completed_at = None
        set_job_stage(job, JobStage.QUEUED)
    session.flush()
    return job


def find_active_job_for_repository(
    session: Session,
    repository_id: UUID,
) -> IndexingJob | None:
    """Idempotency helper: an in-flight import for this repository, if any."""
    stmt = (
        select(IndexingJob)
        .where(
            IndexingJob.repository_id == repository_id,
            IndexingJob.status.in_((JobStatus.QUEUED, JobStatus.RUNNING)),
        )
        .order_by(IndexingJob.created_at.desc())
        .limit(1)
    )
    return session.scalars(stmt).first()


def get_repository_for_job(session: Session, job: IndexingJob) -> Repository:
    repo = session.get(Repository, job.repository_id)
    if repo is None:
        raise JobQueueError(f"Repository {job.repository_id} not found for job {job.id}")
    return repo
