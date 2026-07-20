"""Schemas for repository summary and exact chunk search."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class DeterministicSummary(BaseModel):
    language_mix: dict[str, int]
    support_level_mix: dict[str, int]
    important_directories: list[str]
    test_directories: list[str]
    documentation_directories: list[str]
    build_systems: list[str]
    configuration_files: list[str]
    documentation_files: list[str]
    entry_point_candidates: list[str]
    chunk_counts: dict[str, Any]
    parser_coverage: dict[str, int]
    skipped_file_counts: dict[str, int]
    file_count: int


class EvidenceRef(BaseModel):
    path: str
    start_line: int
    end_line: int


class RepositorySummaryResponse(BaseModel):
    repository_id: UUID
    snapshot_id: UUID | None
    deterministic_summary: DeterministicSummary | None = None
    llm_summary: dict[str, Any] | None = None
    llm_summary_status: str
    evidence: list[EvidenceRef] = Field(default_factory=list)
    model_provenance: dict[str, Any] | None = None


class ChunkSearchHit(BaseModel):
    id: UUID
    path: str
    language: str | None
    support_level: str
    chunk_type: str
    start_line: int
    end_line: int
    content: str
    content_hash: str
    extraction_method: str
    parser_name: str
    parser_version: str
    verified_deep: bool
    llm_enriched: bool
    validation_status: str | None
    semantic_label: str | None
    concise_summary: str | None
    parent_context: str | None
    created_at: datetime


class ChunkSearchResponse(BaseModel):
    repository_id: UUID
    snapshot_id: UUID | None
    query: str
    total: int
    limit: int
    offset: int
    # Reserved for Week 9 hybrid / semantic / LLM rerank layers.
    search_mode: str = "exact"
    hits: list[ChunkSearchHit]
