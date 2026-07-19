"""LLMProvider protocol — provider-specific SDKs stay behind this boundary."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.services.llm.schemas import EnrichmentBatchResult, RepositoryLlmSummary


@runtime_checkable
class LLMProvider(Protocol):
    """Enrichment and summary calls. Never owns parser ranges or verified symbols."""

    @property
    def provider_name(self) -> str: ...

    def enrich_batch(
        self,
        *,
        items: list[dict[str, object]],
        prompt_version: str,
    ) -> EnrichmentBatchResult:
        """Enrich a batch of parser-derived chunk payloads (not one-call-per-chunk)."""
        ...

    def summarize_repository(
        self,
        *,
        deterministic_summary: dict[str, object],
        evidence: list[dict[str, object]],
        prompt_version: str,
    ) -> RepositoryLlmSummary: ...
