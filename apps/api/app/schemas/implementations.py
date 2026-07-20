"""API schemas for symbol interface implementations."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SymbolImplementationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    symbol_id: UUID
    qualified_name: str
    name: str
    kind: str
    path: str
    line: int
    confidence: str
    relation_kind: str
    language: str
    created_at: datetime


class SymbolImplementationsResponse(BaseModel):
    repository_id: UUID
    snapshot_id: UUID
    symbol_id: UUID
    symbol_qualified_name: str
    symbol_kind: str
    total: int
    implementations: list[SymbolImplementationRead] = Field(default_factory=list)
