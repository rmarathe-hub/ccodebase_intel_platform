"""Ask (grounded RAG) request/response schemas."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    language: str | None = None
    path_prefix: str | None = None
    support_level: str | None = None
    apply_rerank: bool = True
    expand: bool = True


class AskCitation(BaseModel):
    path: str
    start_line: int
    end_line: int
    chunk_id: UUID | None = None
    valid: bool = True
    reason: str = "ok"
    raw: str | None = None


class AskEvidenceItem(BaseModel):
    chunk_id: UUID
    path: str
    start_line: int
    end_line: int
    support_level: str
    role: str
    depth: int
    citation: str
    evidence_tier: int | None = None
    chars_stored: int | None = None
    chars_sent: int | None = None
    content_truncated: bool | None = None
    estimated_tokens_sent: int | None = None


class AskAnalysisEcho(BaseModel):
    kind: str
    rewrite_applied: bool
    retrieval_queries: list[str] = Field(default_factory=list)
    identifiers: list[str] = Field(default_factory=list)
    paths: list[str] = Field(default_factory=list)


class AskValidationEcho(BaseModel):
    ok: bool
    valid_count: int
    dropped_count: int
    errors: list[str] = Field(default_factory=list)


class AskBudgetEcho(BaseModel):
    requests_used: int
    requests_limit: int
    tokens_used: int
    tokens_limit: int
    estimated_cost_usd: float
    cost_limit_usd: float
    exhausted: bool = False
    skipped_reason: str | None = None
    remaining_requests: int = 0


class AskFileCoverage(BaseModel):
    requested_file: str | None = None
    path: str | None = None
    indexed: bool = False
    coverage_complete: bool = False
    indexed_line_range: list[int] | None = None
    retrieved_line_ranges: list[list[int]] = Field(default_factory=list)
    missing_ranges: list[list[int]] = Field(default_factory=list)
    chunk_count: int = 0
    language: str | None = None
    classification: str | None = None


class AskFileDiagnostic(BaseModel):
    path: str
    indexed: bool = False
    source_file_present: bool = False
    skip_reason: str | None = None
    classification: str | None = None
    language: str | None = None
    chunk_count: int = 0
    line_coverage: list[list[int]] | None = None
    indexed_line_range: list[int] | None = None
    coverage_complete: bool | None = None
    missing_ranges: list[list[int]] | None = None
    retrieval_reason: str | None = None
    basename_aliases: list[str] = Field(default_factory=list)
    snapshot_id: str | None = None


class AskResponse(BaseModel):
    repository_id: UUID
    snapshot_id: UUID | None
    question: str
    answer: str
    status: str
    citations: list[AskCitation] = Field(default_factory=list)
    evidence: list[AskEvidenceItem] = Field(default_factory=list)
    analysis: AskAnalysisEcho | None = None
    validation: AskValidationEcho
    context_depth: int = 0
    context_tokens_used: int = 0
    context_token_budget: int = 0
    ranked_chunk_ids: list[UUID] = Field(default_factory=list)
    model_provenance: dict[str, Any] | None = None
    cached: bool = False
    notes: list[str] = Field(default_factory=list)
    budget: AskBudgetEcho | None = None
    context_truncated: bool = False
    exact_file_mode: bool = False
    file_coverage: list[AskFileCoverage] = Field(default_factory=list)
    file_diagnostics: list[AskFileDiagnostic] = Field(default_factory=list)
