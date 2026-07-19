"""Pydantic schemas for verified deep symbols."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SymbolParameterRead(BaseModel):
    name: str
    annotation: str | None = None
    kind: str


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
    docstring: str | None = None
    decorators: list[str] = Field(default_factory=list)
    parameters: list[SymbolParameterRead] = Field(default_factory=list)
    return_annotation: str | None = None
    is_async: bool = False
    framework_role: str | None = None
    framework_detail: str | None = None
    resolved_module: str | None = None
    import_style: str | None = None
    is_local_import: bool | None = None
    import_alias: str | None = None
    created_at: datetime

    @field_validator("decorators", mode="before")
    @classmethod
    def _parse_decorators(cls, value: Any) -> list[str]:
        if value is None or value == "":
            return []
        if isinstance(value, list):
            return [str(v) for v in value]
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
            except json.JSONDecodeError:
                return []
            if isinstance(parsed, list):
                return [str(v) for v in parsed]
        return []

    @field_validator("parameters", mode="before")
    @classmethod
    def _parse_parameters(cls, value: Any) -> list[dict[str, Any]]:
        if value is None or value == "":
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
            except json.JSONDecodeError:
                return []
            if isinstance(parsed, list):
                return parsed
        return []


class SymbolListResponse(BaseModel):
    repository_id: UUID
    snapshot_id: UUID | None
    total: int
    limit: int
    offset: int
    symbols: list[SymbolRead]
