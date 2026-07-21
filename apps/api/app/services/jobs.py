"""Helpers for constructing and updating indexing jobs."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from app.models.entities import IndexingJob, JobStatus
from app.models.job_stages import JOB_STAGE_PROGRESS, JobStage


def new_indexing_job(
    *,
    repository_id: UUID,
    snapshot_id: UUID | None = None,
    max_attempts: int = 3,
) -> IndexingJob:
    """Create an in-memory queued indexing job (not yet persisted)."""
    return IndexingJob(
        repository_id=repository_id,
        snapshot_id=snapshot_id,
        status=JobStatus.QUEUED,
        stage=JobStage.QUEUED.value,
        progress_percentage=JOB_STAGE_PROGRESS[JobStage.QUEUED],
        attempt_count=0,
        max_attempts=max_attempts,
    )


def mark_job_running(job: IndexingJob, *, worker_id: str, lease_until: datetime) -> None:
    job.status = JobStatus.RUNNING
    job.attempt_count += 1
    job.locked_by = worker_id
    job.locked_until = lease_until
    job.heartbeat_at = datetime.now(UTC)
    if job.started_at is None:
        job.started_at = datetime.now(UTC)
    if job.stage == JobStage.QUEUED.value:
        set_job_stage(job, JobStage.CLONING)


def set_job_stage(job: IndexingJob, stage: JobStage) -> None:
    job.stage = stage.value
    job.progress_percentage = JOB_STAGE_PROGRESS[stage]
    job.heartbeat_at = datetime.now(UTC)


def mark_job_succeeded(
    job: IndexingJob,
    *,
    info_code: str | None = None,
    info_message: str | None = None,
) -> None:
    job.status = JobStatus.SUCCEEDED
    set_job_stage(job, JobStage.COMPLETED)
    job.locked_by = None
    job.locked_until = None
    job.completed_at = datetime.now(UTC)
    # Optional non-error outcome (e.g. index_unchanged / index_incremental).
    job.error_code = info_code
    job.error_message = info_message


def mark_job_failed(job: IndexingJob, *, error_code: str, error_message: str) -> None:
    job.status = JobStatus.FAILED
    job.locked_by = None
    job.locked_until = None
    job.completed_at = datetime.now(UTC)
    job.error_code = error_code
    job.error_message = error_message


def mark_job_cancelled(job: IndexingJob) -> None:
    job.status = JobStatus.CANCELLED
    job.locked_by = None
    job.locked_until = None
    job.completed_at = datetime.now(UTC)


REQUIRED_JOB_FIELDS = (
    "status",
    "stage",
    "progress_percentage",
    "attempt_count",
    "max_attempts",
    "locked_by",
    "locked_until",
    "heartbeat_at",
    "error_code",
    "error_message",
    "started_at",
    "completed_at",
)
