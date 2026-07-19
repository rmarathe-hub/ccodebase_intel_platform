"""Validate LLM structured output against parser-derived chunk bounds."""

from __future__ import annotations

from dataclasses import dataclass

from app.services.llm.schemas import EnrichmentItem, LineRange, RepositoryLlmSummary


@dataclass(frozen=True)
class ChunkEvidenceBounds:
    chunk_id: str
    path: str
    start_line: int
    end_line: int
    content: str


@dataclass
class ValidationResult:
    ok: bool
    errors: list[str]


def _range_inside(bounds: ChunkEvidenceBounds, rng: LineRange) -> bool:
    return bounds.start_line <= rng.start_line <= rng.end_line <= bounds.end_line


def validate_enrichment_item(
    item: EnrichmentItem,
    bounds_by_id: dict[str, ChunkEvidenceBounds],
) -> ValidationResult:
    errors: list[str] = []
    if item.claims_verified_deep:
        errors.append("claims_verified_deep must be false for enrichment")
    bounds = bounds_by_id.get(item.chunk_id)
    if bounds is None:
        errors.append(f"unknown chunk_id: {item.chunk_id}")
        return ValidationResult(ok=False, errors=errors)
    if item.path != bounds.path:
        errors.append("path does not match parser chunk path")
    for rng in item.evidence_line_ranges:
        if not _range_inside(bounds, rng):
            errors.append(
                f"evidence range {rng.start_line}-{rng.end_line} outside "
                f"chunk {bounds.start_line}-{bounds.end_line}"
            )
    return ValidationResult(ok=not errors, errors=errors)


def validate_repository_summary(
    summary: RepositoryLlmSummary,
    allowed_ranges: list[tuple[int, int]],
) -> ValidationResult:
    """allowed_ranges are inclusive (start, end) line pairs from supplied evidence."""
    errors: list[str] = []
    if summary.claims_verified_deep:
        errors.append("claims_verified_deep must be false for LLM summary")
    for rng in summary.evidence_line_ranges:
        if not any(start <= rng.start_line <= rng.end_line <= end for start, end in allowed_ranges):
            errors.append(
                f"summary evidence {rng.start_line}-{rng.end_line} not in supplied evidence"
            )
    return ValidationResult(ok=not errors, errors=errors)
