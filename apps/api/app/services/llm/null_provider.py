"""No-op provider for CI and enrichment-disabled runs."""

from __future__ import annotations

from app.services.llm.schemas import EnrichmentBatchResult, RepositoryLlmSummary


class NullLLMProvider:
    provider_name = "none"

    def enrich_batch(
        self,
        *,
        items: list[dict[str, object]],
        prompt_version: str,
    ) -> EnrichmentBatchResult:
        return EnrichmentBatchResult(
            items=[],
            model="",
            prompt_version=prompt_version,
            provider=self.provider_name,
        )

    def summarize_repository(
        self,
        *,
        deterministic_summary: dict[str, object],
        evidence: list[dict[str, object]],
        prompt_version: str,
    ) -> RepositoryLlmSummary:
        _ = deterministic_summary, evidence
        raise RuntimeError(
            "NullLLMProvider cannot summarize; enable enrichment with a real provider"
        )
