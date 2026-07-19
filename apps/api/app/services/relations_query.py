"""Query helpers for symbol inheritance relations."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.entities import SourceFile, SymbolRelation


def list_symbol_relations(
    session: Session,
    *,
    snapshot_id: UUID,
    relation_kind: str | None = None,
    confidence: str | None = None,
    path_prefix: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> tuple[list[tuple[SymbolRelation, str]], int]:
    filters = [SymbolRelation.snapshot_id == snapshot_id]
    if relation_kind:
        filters.append(SymbolRelation.relation_kind == relation_kind.lower())
    if confidence:
        filters.append(SymbolRelation.confidence == confidence.lower())

    stmt = (
        select(SymbolRelation, SourceFile.path)
        .join(SourceFile, SourceFile.id == SymbolRelation.source_file_id)
        .where(*filters)
    )
    if path_prefix:
        stmt = stmt.where(SourceFile.path.startswith(path_prefix))

    count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
    total = int(session.scalar(count_stmt) or 0)

    rows = list(
        session.execute(
            stmt.order_by(SymbolRelation.line, SymbolRelation.from_qualified_name)
            .limit(limit)
            .offset(offset)
        ).all()
    )
    return [(rel, path) for rel, path in rows], total
