"""Query verified symbols for repository snapshots."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.models.entities import SourceFile, Symbol


def list_symbols(
    session: Session,
    *,
    snapshot_id: UUID,
    kind: str | None = None,
    path_prefix: str | None = None,
    name_contains: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> tuple[list[tuple[Symbol, str]], int]:
    """Return ``(symbol, source_path)`` rows plus total count."""
    capped = max(1, min(limit, 500))
    start = max(0, offset)

    filters = [Symbol.snapshot_id == snapshot_id]
    if kind:
        filters.append(Symbol.kind == kind.lower())
    if name_contains:
        filters.append(Symbol.name.ilike(f"%{name_contains}%"))

    stmt = (
        select(Symbol, SourceFile.path)
        .join(SourceFile, SourceFile.id == Symbol.source_file_id)
        .where(*filters)
    )
    if path_prefix:
        stmt = stmt.where(SourceFile.path.startswith(path_prefix))

    count_stmt: Select[tuple[int]] = (
        select(func.count())
        .select_from(Symbol)
        .join(SourceFile, SourceFile.id == Symbol.source_file_id)
        .where(*filters)
    )
    if path_prefix:
        count_stmt = count_stmt.where(SourceFile.path.startswith(path_prefix))

    total = int(session.scalar(count_stmt) or 0)
    rows = list(
        session.execute(
            stmt.order_by(SourceFile.path.asc(), Symbol.start_line.asc(), Symbol.name.asc())
            .offset(start)
            .limit(capped)
        ).all()
    )
    return [(sym, path) for sym, path in rows], total
