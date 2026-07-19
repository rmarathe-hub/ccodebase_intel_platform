"""Pydantic schemas for extracted call sites."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SymbolCallRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    snapshot_id: UUID
    source_file_id: UUID
    path: str
    caller_symbol_id: UUID | None
    caller_qualified_name: str | None
    raw_callee: str
    qualified_expression: str
    line: int
    candidate_qualified_name: str | None
    confidence: str
    language: str
    created_at: datetime


class SymbolCallListResponse(BaseModel):
    repository_id: UUID
    snapshot_id: UUID | None
    total: int
    limit: int
    offset: int
    calls: list[SymbolCallRead]


class SymbolNeighborsResponse(BaseModel):
    """Callers or callees for one symbol (Week 4 Day 7)."""

    repository_id: UUID
    snapshot_id: UUID
    symbol_id: UUID
    symbol_qualified_name: str
    direction: str  # callers | callees
    total: int
    calls: list[SymbolCallRead]
