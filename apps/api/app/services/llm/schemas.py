"""Strict structured schemas for LLM enrichment output."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, model_validator


class ConstructLabel(StrEnum):
    FUNCTION_LIKE = "function_like"
    METHOD_LIKE = "method_like"
    CLASS_LIKE = "class_like"
    INTERFACE_LIKE = "interface_like"
    MODULE_LIKE = "module_like"
    CONFIGURATION_SECTION = "configuration_section"
    DOCUMENTATION_SECTION = "documentation_section"
    SQL_STATEMENT_GROUP = "SQL_statement_group"
    BUILD_DEFINITION = "build_definition"
    TEST_SECTION = "test_section"
    ENTRY_POINT_CANDIDATE = "entry_point_candidate"
    UNKNOWN = "unknown"


class LineRange(BaseModel):
    start_line: int = Field(ge=1)
    end_line: int = Field(ge=1)

    @model_validator(mode="after")
    def end_ge_start(self) -> LineRange:
        if self.end_line < self.start_line:
            raise ValueError("end_line must be >= start_line")
        return self


class EnrichmentItem(BaseModel):
    """One enrichment for a single parser-derived chunk."""

    chunk_id: str
    path: str
    semantic_label: str = Field(min_length=1, max_length=200)
    concise_summary: str = Field(min_length=1, max_length=2000)
    probable_construct_type: ConstructLabel
    entry_point_likelihood: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_line_ranges: list[LineRange] = Field(min_length=1)
    uncertainty_reason: str | None = None
    # Must remain false for generic enrichment — validator enforces.
    claims_verified_deep: bool = False


class EnrichmentBatchResult(BaseModel):
    items: list[EnrichmentItem]
    model: str
    prompt_version: str
    provider: str


class RepositoryLlmSummary(BaseModel):
    probable_architecture: str = Field(min_length=1, max_length=4000)
    major_components: list[str] = Field(default_factory=list)
    likely_entry_points: list[str] = Field(default_factory=list)
    notable_frameworks: list[str] = Field(default_factory=list)
    repository_purpose: str = Field(min_length=1, max_length=2000)
    uncertainty_notes: list[str] = Field(default_factory=list)
    evidence_line_ranges: list[LineRange] = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    claims_verified_deep: bool = False
    model: str
    prompt_version: str
    provider: str
