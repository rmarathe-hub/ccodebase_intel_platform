from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.models.entities import IndexingJob, Repository
from app.schemas.calls import SymbolCallListResponse, SymbolCallRead
from app.schemas.files import RepositoryListItem, SourceFileListResponse, SourceFileRead
from app.schemas.jobs import IndexingJobRead
from app.schemas.repositories import RepositoryImportRequest, RepositoryRead
from app.schemas.snapshots import RepositoryImportResponse
from app.schemas.symbols import SymbolListResponse, SymbolRead
from app.services.calls_query import list_symbol_calls
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
from app.services.symbols_query import list_symbols

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


@router.get(
    "/repositories/{repository_id}/symbols",
    response_model=SymbolListResponse,
)
def get_repository_symbols(
    repository_id: UUID,
    kind: str | None = Query(default=None),
    path_prefix: str | None = Query(default=None),
    name_contains: str | None = Query(default=None),
    framework_role: str | None = Query(default=None),
    is_local_import: bool | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> SymbolListResponse:
    repo = db.get(Repository, repository_id)
    if repo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found",
        )

    if kind is not None and kind.lower() not in {
        "class",
        "function",
        "method",
        "import",
    }:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "invalid_symbol_kind",
                "message": "kind must be class, function, method, or import",
            },
        )

    allowed_roles = {
        "fastapi_route",
        "flask_route",
        "django_view",
        "sqlalchemy_model",
        "celery_task",
        "pydantic_model",
    }
    if framework_role is not None and framework_role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "invalid_framework_role",
                "message": f"framework_role must be one of: {', '.join(sorted(allowed_roles))}",
            },
        )

    snapshot = latest_ready_snapshot(db, repository_id)
    if snapshot is None:
        return SymbolListResponse(
            repository_id=repository_id,
            snapshot_id=None,
            total=0,
            limit=limit,
            offset=offset,
            symbols=[],
        )

    rows, total = list_symbols(
        db,
        snapshot_id=snapshot.id,
        kind=kind,
        path_prefix=path_prefix,
        name_contains=name_contains,
        framework_role=framework_role,
        is_local_import=is_local_import,
        limit=limit,
        offset=offset,
    )
    symbols = [
        SymbolRead(
            id=sym.id,
            snapshot_id=sym.snapshot_id,
            source_file_id=sym.source_file_id,
            path=path,
            kind=sym.kind,
            name=sym.name,
            qualified_name=sym.qualified_name,
            language=sym.language,
            start_line=sym.start_line,
            end_line=sym.end_line,
            signature=sym.signature,
            docstring=sym.docstring,
            decorators=sym.decorators_json,
            parameters=sym.parameters_json,
            return_annotation=sym.return_annotation,
            is_async=sym.is_async,
            framework_role=sym.framework_role,
            framework_detail=sym.framework_detail,
            resolved_module=sym.resolved_module,
            import_style=sym.import_style,
            is_local_import=sym.is_local_import,
            import_alias=sym.import_alias,
            created_at=sym.created_at,
        )
        for sym, path in rows
    ]
    return SymbolListResponse(
        repository_id=repository_id,
        snapshot_id=snapshot.id,
        total=total,
        limit=limit,
        offset=offset,
        symbols=symbols,
    )


@router.get(
    "/repositories/{repository_id}/calls",
    response_model=SymbolCallListResponse,
)
def get_repository_calls(
    repository_id: UUID,
    confidence: str | None = Query(default=None),
    caller_contains: str | None = Query(default=None),
    path_prefix: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> SymbolCallListResponse:
    repo = db.get(Repository, repository_id)
    if repo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found",
        )

    if confidence is not None and confidence.lower() not in {
        "resolved",
        "ambiguous",
        "unresolved",
    }:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "invalid_confidence",
                "message": "confidence must be resolved, ambiguous, or unresolved",
            },
        )

    snapshot = latest_ready_snapshot(db, repository_id)
    if snapshot is None:
        return SymbolCallListResponse(
            repository_id=repository_id,
            snapshot_id=None,
            total=0,
            limit=limit,
            offset=offset,
            calls=[],
        )

    rows, total = list_symbol_calls(
        db,
        snapshot_id=snapshot.id,
        confidence=confidence,
        caller_contains=caller_contains,
        path_prefix=path_prefix,
        limit=limit,
        offset=offset,
    )
    calls = [
        SymbolCallRead(
            id=call.id,
            snapshot_id=call.snapshot_id,
            source_file_id=call.source_file_id,
            path=path,
            caller_symbol_id=call.caller_symbol_id,
            caller_qualified_name=call.caller_qualified_name,
            raw_callee=call.raw_callee,
            qualified_expression=call.qualified_expression,
            line=call.line,
            candidate_qualified_name=call.candidate_qualified_name,
            confidence=call.confidence,
            language=call.language,
            created_at=call.created_at,
        )
        for call, path in rows
    ]
    return SymbolCallListResponse(
        repository_id=repository_id,
        snapshot_id=snapshot.id,
        total=total,
        limit=limit,
        offset=offset,
        calls=calls,
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
