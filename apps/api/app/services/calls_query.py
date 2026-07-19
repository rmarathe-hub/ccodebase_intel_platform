"""Query extracted symbol call sites."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.models.entities import SourceFile, SymbolCall


def list_symbol_calls(
    session: Session,
    *,
    snapshot_id: UUID,
    confidence: str | None = None,
    caller_contains: str | None = None,
    path_prefix: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> tuple[list[tuple[SymbolCall, str]], int]:
    capped = max(1, min(limit, 500))
    start = max(0, offset)

    filters = [SymbolCall.snapshot_id == snapshot_id]
    if confidence:
        filters.append(SymbolCall.confidence == confidence.lower())
    if caller_contains:
        filters.append(SymbolCall.caller_qualified_name.ilike(f"%{caller_contains}%"))

    stmt = (
        select(SymbolCall, SourceFile.path)
        .join(SourceFile, SourceFile.id == SymbolCall.source_file_id)
        .where(*filters)
    )
    if path_prefix:
        stmt = stmt.where(SourceFile.path.startswith(path_prefix))

    count_stmt: Select[tuple[int]] = (
        select(func.count())
        .select_from(SymbolCall)
        .join(SourceFile, SourceFile.id == SymbolCall.source_file_id)
        .where(*filters)
    )
    if path_prefix:
        count_stmt = count_stmt.where(SourceFile.path.startswith(path_prefix))

    total = int(session.scalar(count_stmt) or 0)
    rows = list(
        session.execute(
            stmt.order_by(SourceFile.path.asc(), SymbolCall.line.asc())
            .offset(start)
            .limit(capped)
        ).all()
    )
    return [(call, path) for call, path in rows], total
