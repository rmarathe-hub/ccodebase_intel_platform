"""API schemas for symbol inheritance relations."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SymbolRelationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    snapshot_id: UUID
    source_file_id: UUID
    path: str
    from_symbol_id: UUID | None = None
    from_qualified_name: str
    relation_kind: str
    raw_target: str
    line: int
    candidate_qualified_name: str | None = None
    to_symbol_id: UUID | None = None
    confidence: str
    language: str
    created_at: datetime


class SymbolRelationListResponse(BaseModel):
    repository_id: UUID
    snapshot_id: UUID | None
    total: int
    limit: int
    offset: int
    relations: list[SymbolRelationRead] = Field(default_factory=list)
