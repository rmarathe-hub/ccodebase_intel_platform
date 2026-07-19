"""Pydantic schemas for verified deep symbols."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SymbolRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    snapshot_id: UUID
    source_file_id: UUID
    path: str
    kind: str
    name: str
    qualified_name: str
    language: str
    start_line: int
    end_line: int
    signature: str | None
    created_at: datetime


class SymbolListResponse(BaseModel):
    repository_id: UUID
    snapshot_id: UUID | None
    total: int
    limit: int
    offset: int
    symbols: list[SymbolRead]
