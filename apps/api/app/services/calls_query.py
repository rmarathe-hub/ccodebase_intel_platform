"""Query extracted symbol call sites."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from app.models.entities import SourceFile, Symbol, SymbolCall


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


def get_symbol_in_snapshot(
    session: Session,
    *,
    snapshot_id: UUID,
    symbol_id: UUID,
) -> Symbol | None:
    return session.scalars(
        select(Symbol).where(
            Symbol.id == symbol_id,
            Symbol.snapshot_id == snapshot_id,
        )
    ).first()


def list_callees_for_symbol(
    session: Session,
    *,
    snapshot_id: UUID,
    symbol_id: UUID,
    limit: int = 100,
) -> list[tuple[SymbolCall, str]]:
    """Calls made *by* this symbol (outgoing)."""
    capped = max(1, min(limit, 500))
    rows = list(
        session.execute(
            select(SymbolCall, SourceFile.path)
            .join(SourceFile, SourceFile.id == SymbolCall.source_file_id)
            .where(
                SymbolCall.snapshot_id == snapshot_id,
                SymbolCall.caller_symbol_id == symbol_id,
            )
            .order_by(SymbolCall.line.asc())
            .limit(capped)
        ).all()
    )
    return [(call, path) for call, path in rows]


def list_callers_for_symbol(
    session: Session,
    *,
    snapshot_id: UUID,
    symbol: Symbol,
    limit: int = 100,
) -> list[tuple[SymbolCall, str]]:
    """Calls that target this symbol (incoming), best-effort via candidate QName."""
    capped = max(1, min(limit, 500))
    qname = symbol.qualified_name
    rows = list(
        session.execute(
            select(SymbolCall, SourceFile.path)
            .join(SourceFile, SourceFile.id == SymbolCall.source_file_id)
            .where(
                SymbolCall.snapshot_id == snapshot_id,
                or_(
                    SymbolCall.candidate_qualified_name == qname,
                    SymbolCall.raw_callee == symbol.name,
                ),
            )
            .order_by(SymbolCall.line.asc())
            .limit(capped)
        ).all()
    )
    filtered: list[tuple[SymbolCall, str]] = []
    for call, path in rows:
        if call.candidate_qualified_name == qname:
            filtered.append((call, path))
        elif call.candidate_qualified_name is None and call.raw_callee == symbol.name:
            filtered.append((call, path))
    return filtered
