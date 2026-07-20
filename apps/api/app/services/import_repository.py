"""Repository import orchestration."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import IndexingJob, JobStatus, Repository
from app.models.job_stages import JOB_STAGE_PROGRESS, JobStage
from app.services.github_url import parse_github_repository_url
from app.services.job_queue import find_active_job_for_repository
from app.services.jobs import new_indexing_job


class RepositoryImportError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


def get_or_create_repository(session: Session, url: str) -> tuple[Repository, bool]:
    parsed = parse_github_repository_url(url)
    existing = session.scalars(
        select(Repository).where(
            Repository.host == parsed.host,
            Repository.owner_name == parsed.owner,
            Repository.name == parsed.name,
        )
    ).first()
    if existing is not None:
        return existing, False

    repo = Repository(
        host=parsed.host,
        owner_name=parsed.owner,
        name=parsed.name,
        default_branch="main",
        clone_url=parsed.clone_url,
    )
    session.add(repo)
    session.flush()
    return repo, True


def import_repository(session: Session, url: str) -> tuple[Repository, IndexingJob, bool]:
    """Create repository + queued job, or return existing in-flight job.

    Returns (repository, job, created_new_job).
    """
    repo, _repo_created = get_or_create_repository(session, url)
    active = find_active_job_for_repository(session, repo.id)
    if active is not None:
        return repo, active, False

    job = new_indexing_job(repository_id=repo.id)
    session.add(job)
    # Commit before the HTTP response is returned. FastAPI runs dependency teardown
    # (including get_db's commit) after the response is sent, so flush-only left a
    # race where GET /jobs/{id} could 404 for a just-created job.
    session.commit()
    session.refresh(repo)
    session.refresh(job)
    return repo, job, True


def retry_indexing_job(session: Session, job_id: UUID) -> IndexingJob:
    job = session.get(IndexingJob, job_id)
    if job is None:
        raise RepositoryImportError("job_not_found", f"Job {job_id} not found")

    if job.status not in {JobStatus.FAILED, JobStatus.CANCELLED}:
        raise RepositoryImportError(
            "job_not_retryable",
            f"Only FAILED or CANCELLED jobs can be retried (status={job.status})",
        )

    active = find_active_job_for_repository(session, job.repository_id)
    if active is not None and active.id != job.id:
        raise RepositoryImportError(
            "job_already_active",
            "An active indexing job already exists for this repository",
        )

    job.status = JobStatus.QUEUED
    job.stage = JobStage.QUEUED.value
    job.progress_percentage = JOB_STAGE_PROGRESS[JobStage.QUEUED]
    job.attempt_count = 0
    job.locked_by = None
    job.locked_until = None
    job.heartbeat_at = None
    job.error_code = None
    job.error_message = None
    job.started_at = None
    job.completed_at = None
    session.commit()
    session.refresh(job)
    return job
