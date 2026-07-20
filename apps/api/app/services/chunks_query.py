"""Exact PostgreSQL search over persisted chunks (LLM-independent)."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.models import Chunk


def _escape_like(term: str) -> str:
    return term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def search_chunks(
    session: Session,
    *,
    snapshot_id: UUID,
    query: str,
    language: str | None = None,
    path_prefix: str | None = None,
    support_level: str | None = None,
    chunk_type: str | None = None,
    extraction_method: str | None = None,
    parser_name: str | None = None,
    llm_enriched: bool | None = None,
    validation_status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[Chunk], int]:
    """Case-insensitive substring match on chunk content. No embeddings."""
    q = query.strip()
    if not q:
        return [], 0

    capped = max(1, min(limit, 200))
    start = max(0, offset)
    pattern = f"%{_escape_like(q)}%"

    filters = [
        Chunk.snapshot_id == snapshot_id,
        Chunk.content.ilike(pattern, escape="\\"),
    ]
    if language:
        filters.append(Chunk.language == language)
    if path_prefix:
        filters.append(Chunk.path.startswith(path_prefix))
    if support_level:
        filters.append(Chunk.support_level == support_level.lower())
    if chunk_type:
        filters.append(Chunk.chunk_type == chunk_type)
    if extraction_method:
        filters.append(Chunk.extraction_method == extraction_method)
    if parser_name:
        filters.append(Chunk.parser_name == parser_name)
    if llm_enriched is not None:
        filters.append(Chunk.llm_enriched.is_(llm_enriched))
    if validation_status:
        filters.append(Chunk.validation_status == validation_status)

    count_stmt: Select[tuple[int]] = select(func.count()).select_from(Chunk).where(*filters)
    total = int(session.scalar(count_stmt) or 0)
    rows = list(
        session.scalars(
            select(Chunk)
            .where(*filters)
            .order_by(Chunk.path.asc(), Chunk.start_line.asc())
            .offset(start)
            .limit(capped)
        ).all()
    )
    return rows, total
