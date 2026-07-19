"""List repositories and discovered source files."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.models.entities import Repository, RepositorySnapshot, SnapshotStatus, SourceFile


def list_repositories(session: Session, *, limit: int = 50) -> list[Repository]:
    capped = max(1, min(limit, 200))
    return list(
        session.scalars(
            select(Repository).order_by(Repository.created_at.desc()).limit(capped)
        ).all()
    )


def latest_ready_snapshot(
    session: Session,
    repository_id: UUID,
) -> RepositorySnapshot | None:
    return session.scalars(
        select(RepositorySnapshot)
        .where(
            RepositorySnapshot.repository_id == repository_id,
            RepositorySnapshot.status == SnapshotStatus.READY,
        )
        .order_by(RepositorySnapshot.created_at.desc())
        .limit(1)
    ).first()


def list_source_files(
    session: Session,
    *,
    snapshot_id: UUID,
    support_level: str | None = None,
    path_prefix: str | None = None,
    include_skipped: bool = True,
    limit: int = 100,
    offset: int = 0,
) -> tuple[list[SourceFile], int]:
    capped = max(1, min(limit, 500))
    start = max(0, offset)

    filters = [SourceFile.snapshot_id == snapshot_id]
    if support_level:
        filters.append(SourceFile.support_level == support_level.lower())
    if path_prefix:
        filters.append(SourceFile.path.startswith(path_prefix))
    if not include_skipped:
        filters.append(SourceFile.support_level != "skip")

    count_stmt: Select[tuple[int]] = select(func.count()).select_from(SourceFile).where(*filters)
    total = int(session.scalar(count_stmt) or 0)

    rows = list(
        session.scalars(
            select(SourceFile)
            .where(*filters)
            .order_by(SourceFile.path.asc())
            .offset(start)
            .limit(capped)
        ).all()
    )
    return rows, total
