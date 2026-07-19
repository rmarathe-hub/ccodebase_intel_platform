from datetime import UTC, datetime, timedelta
from uuid import uuid4

from app.models import JOB_STAGE_PROGRESS, JobStage, JobStatus
from app.schemas.jobs import IndexingJobCreateDefaults, IndexingJobRead
from app.services.jobs import (
    REQUIRED_JOB_FIELDS,
    mark_job_cancelled,
    mark_job_failed,
    mark_job_running,
    mark_job_succeeded,
    new_indexing_job,
    set_job_stage,
)


def test_required_job_columns_exist() -> None:
    from app.models import IndexingJob

    columns = set(IndexingJob.__table__.c.keys())
    assert set(REQUIRED_JOB_FIELDS).issubset(columns)


def test_job_statuses_match_contract() -> None:
    assert {status.value for status in JobStatus} == {
        "QUEUED",
        "RUNNING",
        "SUCCEEDED",
        "FAILED",
        "CANCELLED",
    }


def test_job_stages_cover_progress_ui() -> None:
    assert list(JobStage) == [
        JobStage.QUEUED,
        JobStage.CLONING,
        JobStage.DISCOVERING_FILES,
        JobStage.PARSING,
        JobStage.BUILDING_RELATIONSHIPS,
        JobStage.CHUNKING,
        JobStage.EMBEDDING,
        JobStage.VALIDATING,
        JobStage.COMPLETED,
    ]
    assert JOB_STAGE_PROGRESS[JobStage.QUEUED] == 0
    assert JOB_STAGE_PROGRESS[JobStage.COMPLETED] == 100


def test_new_indexing_job_defaults() -> None:
    repo_id = uuid4()
    job = new_indexing_job(repository_id=repo_id)
    assert job.repository_id == repo_id
    assert job.status == JobStatus.QUEUED
    assert job.stage == JobStage.QUEUED.value
    assert job.progress_percentage == 0
    assert job.attempt_count == 0
    assert job.max_attempts == 3
    assert job.locked_by is None
    assert job.error_code is None


def test_job_lifecycle_helpers() -> None:
    job = new_indexing_job(repository_id=uuid4())
    lease = datetime.now(UTC) + timedelta(minutes=5)

    mark_job_running(job, worker_id="worker-1", lease_until=lease)
    assert job.status == JobStatus.RUNNING
    assert job.attempt_count == 1
    assert job.locked_by == "worker-1"
    assert job.stage == JobStage.CLONING.value
    assert job.started_at is not None

    set_job_stage(job, JobStage.PARSING)
    assert job.stage == "parsing"
    assert job.progress_percentage == JOB_STAGE_PROGRESS[JobStage.PARSING]

    mark_job_succeeded(job)
    assert job.status == JobStatus.SUCCEEDED
    assert job.stage == JobStage.COMPLETED.value
    assert job.progress_percentage == 100
    assert job.locked_by is None
    assert job.completed_at is not None


def test_job_failure_and_cancel() -> None:
    failed = new_indexing_job(repository_id=uuid4())
    mark_job_failed(failed, error_code="clone_timeout", error_message="clone timed out")
    assert failed.status == JobStatus.FAILED
    assert failed.error_code == "clone_timeout"

    cancelled = new_indexing_job(repository_id=uuid4())
    mark_job_cancelled(cancelled)
    assert cancelled.status == JobStatus.CANCELLED


def test_job_schemas() -> None:
    defaults = IndexingJobCreateDefaults()
    assert defaults.status == JobStatus.QUEUED
    assert defaults.stage == JobStage.QUEUED

    # Ensure read schema lists every Day-2 field.
    fields = set(IndexingJobRead.model_fields.keys())
    assert {
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
    }.issubset(fields)
