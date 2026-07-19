from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.models.entities import IndexingJob, Repository
from app.schemas.files import RepositoryListItem, SourceFileListResponse, SourceFileRead
from app.schemas.jobs import IndexingJobRead
from app.schemas.repositories import RepositoryImportRequest, RepositoryRead
from app.schemas.snapshots import RepositoryImportResponse
from app.services.files_query import (
    latest_ready_snapshot,
    list_repositories,
    list_source_files,
)
from app.services.github_url import GitHubURLValidationError
from app.services.import_repository import (
    RepositoryImportError,
    import_repository,
    retry_indexing_job,
)

router = APIRouter(prefix="/api/v1")


@router.post(
    "/repositories/import",
    response_model=RepositoryImportResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def import_github_repository(
    body: RepositoryImportRequest,
    db: Session = Depends(get_db),
) -> RepositoryImportResponse:
    try:
        repo, job, created = import_repository(db, body.url)
    except GitHubURLValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": exc.code, "message": str(exc)},
        ) from exc
    return RepositoryImportResponse(
        repository=RepositoryRead.model_validate(repo),
        job=IndexingJobRead.model_validate(job),
        created_new_job=created,
    )


@router.get("/repositories", response_model=list[RepositoryListItem])
def get_repositories(
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[RepositoryListItem]:
    repos = list_repositories(db, limit=limit)
    return [RepositoryListItem.model_validate(repo) for repo in repos]


@router.get(
    "/repositories/{repository_id}/files",
    response_model=SourceFileListResponse,
)
def get_repository_files(
    repository_id: UUID,
    support_level: str | None = Query(default=None),
    path_prefix: str | None = Query(default=None),
    include_skipped: bool = Query(default=True),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> SourceFileListResponse:
    repo = db.get(Repository, repository_id)
    if repo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found",
        )

    if support_level is not None and support_level.lower() not in {
        "deep",
        "generic",
        "skip",
    }:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "invalid_support_level",
                "message": "support_level must be deep, generic, or skip",
            },
        )

    snapshot = latest_ready_snapshot(db, repository_id)
    if snapshot is None:
        return SourceFileListResponse(
            repository_id=repository_id,
            snapshot_id=None,
            total=0,
            limit=limit,
            offset=offset,
            files=[],
        )

    rows, total = list_source_files(
        db,
        snapshot_id=snapshot.id,
        support_level=support_level,
        path_prefix=path_prefix,
        include_skipped=include_skipped,
        limit=limit,
        offset=offset,
    )
    return SourceFileListResponse(
        repository_id=repository_id,
        snapshot_id=snapshot.id,
        total=total,
        limit=limit,
        offset=offset,
        files=[SourceFileRead.model_validate(row) for row in rows],
    )


@router.get("/jobs", response_model=list[IndexingJobRead])
def list_jobs(
    limit: int = 50,
    db: Session = Depends(get_db),
) -> list[IndexingJobRead]:
    capped = max(1, min(limit, 200))
    jobs = db.scalars(
        select(IndexingJob).order_by(IndexingJob.created_at.desc()).limit(capped)
    ).all()
    return [IndexingJobRead.model_validate(job) for job in jobs]


@router.get("/jobs/{job_id}", response_model=IndexingJobRead)
def get_job(job_id: UUID, db: Session = Depends(get_db)) -> IndexingJobRead:
    job = db.get(IndexingJob, job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return IndexingJobRead.model_validate(job)


@router.get("/repositories/{repository_id}/jobs", response_model=list[IndexingJobRead])
def list_repository_jobs(
    repository_id: UUID,
    db: Session = Depends(get_db),
) -> list[IndexingJobRead]:
    repo = db.get(Repository, repository_id)
    if repo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found")
    jobs = db.scalars(
        select(IndexingJob)
        .where(IndexingJob.repository_id == repo.id)
        .order_by(IndexingJob.created_at.desc())
    ).all()
    return [IndexingJobRead.model_validate(job) for job in jobs]


@router.post("/jobs/{job_id}/retry", response_model=IndexingJobRead)
def retry_job(job_id: UUID, db: Session = Depends(get_db)) -> IndexingJobRead:
    try:
        job = retry_indexing_job(db, job_id)
    except RepositoryImportError as exc:
        code = (
            status.HTTP_404_NOT_FOUND
            if exc.code == "job_not_found"
            else status.HTTP_409_CONFLICT
        )
        raise HTTPException(
            status_code=code,
            detail={"code": exc.code, "message": str(exc)},
        ) from exc
    return IndexingJobRead.model_validate(job)
