"""Job stage labels/progress invariants and transition helper coverage."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from app.models.entities import JobStatus
from app.models.job_stages import JOB_STAGE_LABELS, JOB_STAGE_PROGRESS, JobStage
from app.services.jobs import (
    mark_job_cancelled,
    mark_job_failed,
    mark_job_running,
    mark_job_succeeded,
    new_indexing_job,
    set_job_stage,
)

REQUIRED_UI_LABELS = [
    "Queued",
    "Cloning",
    "Discovering files",
    "Parsing",
    "Building relationships",
    "Chunking",
    "Embedding",
    "Validating",
    "Completed",
]


def test_stage_labels_match_week2_ui_contract() -> None:
    labels = [JOB_STAGE_LABELS[stage] for stage in JobStage]
    assert labels == REQUIRED_UI_LABELS


def test_progress_is_monotonic_nondecreasing() -> None:
    values = [JOB_STAGE_PROGRESS[stage] for stage in JobStage]
    assert values[0] == 0
    assert values[-1] == 100
    assert values == sorted(values)


@pytest.mark.parametrize("stage", list(JobStage))
def test_each_stage_has_label_and_progress(stage: JobStage) -> None:
    assert stage in JOB_STAGE_LABELS
    assert 0 <= JOB_STAGE_PROGRESS[stage] <= 100


def test_set_job_stage_updates_progress() -> None:
    job = new_indexing_job(repository_id=uuid4())
    for stage in JobStage:
        set_job_stage(job, stage)
        assert job.stage == stage.value
        assert job.progress_percentage == JOB_STAGE_PROGRESS[stage]


def test_mark_running_moves_from_queued_to_cloning() -> None:
    job = new_indexing_job(repository_id=uuid4())
    mark_job_running(
        job,
        worker_id="w1",
        lease_until=datetime.now(UTC) + timedelta(seconds=30),
    )
    assert job.status == JobStatus.RUNNING
    assert job.stage == JobStage.CLONING.value
    assert job.attempt_count == 1


def test_success_clears_lock_and_completes() -> None:
    job = new_indexing_job(repository_id=uuid4())
    mark_job_running(job, worker_id="w1", lease_until=datetime.now(UTC) + timedelta(seconds=30))
    mark_job_succeeded(job)
    assert job.status == JobStatus.SUCCEEDED
    assert job.stage == JobStage.COMPLETED.value
    assert job.locked_by is None
    assert job.progress_percentage == 100


def test_failure_and_cancel_terminal() -> None:
    failed = new_indexing_job(repository_id=uuid4())
    mark_job_failed(failed, error_code="x", error_message="y")
    assert failed.status == JobStatus.FAILED
    cancelled = new_indexing_job(repository_id=uuid4())
    mark_job_cancelled(cancelled)
    assert cancelled.status == JobStatus.CANCELLED
