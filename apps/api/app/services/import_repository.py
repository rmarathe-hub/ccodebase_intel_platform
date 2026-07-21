"""Repository import orchestration."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import IndexingJob, JobStatus, Repository
from app.models.job_stages import JOB_STAGE_PROGRESS, JobStage
from app.services.github_url import parse_github_repository_url
from app.services.job_queue import find_active_job_for_repository
from app.services.jobs import mark_job_cancelled, new_indexing_job


class RepositoryImportError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


def get_or_create_repository(
    session: Session,
    url: str,
    *,
    branch: str | None = None,
) -> tuple[Repository, bool]:
    parsed = parse_github_repository_url(url)
    existing = session.scalars(
        select(Repository).where(
            Repository.host == parsed.host,
            Repository.owner_name == parsed.owner,
            Repository.name == parsed.name,
        )
    ).first()
    if existing is not None:
        if branch:
            existing.default_branch = branch
        return existing, False

    repo = Repository(
        host=parsed.host,
        owner_name=parsed.owner,
        name=parsed.name,
        # Empty means "use remote default HEAD" until clone resolves the real name.
        default_branch=branch or "",
        clone_url=parsed.clone_url,
    )
    session.add(repo)
    session.flush()
    return repo, True


def import_repository(
    session: Session,
    url: str,
    *,
    branch: str | None = None,
) -> tuple[Repository, IndexingJob, bool]:
    """Create repository + queued job, or return existing in-flight job.

    Returns (repository, job, created_new_job).
    When ``branch`` is set it is stored on the repository and used for shallow clone.
    """
    repo, _repo_created = get_or_create_repository(session, url, branch=branch)
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


def reindex_repository(
    session: Session,
    repository_id: UUID,
) -> tuple[Repository, IndexingJob, bool]:
    """Queue a full re-index for an existing repository (or return the active job)."""
    repo = session.get(Repository, repository_id)
    if repo is None:
        raise RepositoryImportError("repository_not_found", f"Repository {repository_id} not found")

    active = find_active_job_for_repository(session, repo.id)
    if active is not None:
        return repo, active, False

    job = new_indexing_job(repository_id=repo.id)
    session.add(job)
    session.commit()
    session.refresh(repo)
    session.refresh(job)
    return repo, job, True


def cancel_indexing_job(session: Session, job_id: UUID) -> IndexingJob:
    """Cancel a QUEUED or RUNNING job. Idempotent if already CANCELLED."""
    job = session.get(IndexingJob, job_id)
    if job is None:
        raise RepositoryImportError("job_not_found", f"Job {job_id} not found")

    if job.status == JobStatus.CANCELLED:
        return job

    if job.status not in {JobStatus.QUEUED, JobStatus.RUNNING}:
        raise RepositoryImportError(
            "job_not_cancellable",
            f"Only QUEUED or RUNNING jobs can be cancelled (status={job.status})",
        )

    mark_job_cancelled(job)
    job.error_code = "cancelled"
    job.error_message = "Indexing cancelled by user"
    session.commit()
    session.refresh(job)
    return job
