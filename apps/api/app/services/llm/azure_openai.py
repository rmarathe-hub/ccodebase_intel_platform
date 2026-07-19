"""Azure OpenAI adapter stub.

Live calls are wired in Week 7 enrichment days. This module documents the
boundary: LangChain AzureChatOpenAI (orchestration) or direct openai.AzureOpenAI
when simpler — chosen via Settings.llm_orchestration. No agents.
"""

from __future__ import annotations

from app.services.llm.schemas import EnrichmentBatchResult, RepositoryLlmSummary


class AzureOpenAIProvider:
    """Placeholder until enrichment pipeline is implemented."""

    provider_name = "azure_openai"

    def __init__(
        self,
        *,
        endpoint: str,
        api_key: str,
        api_version: str,
        deployment: str,
        orchestration: str = "auto",
        temperature: float = 0.0,
        timeout_seconds: float = 60.0,
        max_retries: int = 2,
    ) -> None:
        self.endpoint = endpoint
        self.api_key = api_key
        self.api_version = api_version
        self.deployment = deployment
        self.orchestration = orchestration
        self.temperature = temperature
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries

    def enrich_batch(
        self,
        *,
        items: list[dict[str, object]],
        prompt_version: str,
    ) -> EnrichmentBatchResult:
        _ = items, prompt_version
        raise NotImplementedError(
            "Azure OpenAI enrich_batch is not wired yet; "
            "deterministic indexing must proceed without enrichment"
        )

    def summarize_repository(
        self,
        *,
        deterministic_summary: dict[str, object],
        evidence: list[dict[str, object]],
        prompt_version: str,
    ) -> RepositoryLlmSummary:
        _ = deterministic_summary, evidence, prompt_version
        raise NotImplementedError(
            "Azure OpenAI summarize_repository is not wired yet; "
            "deterministic summaries remain authoritative"
        )
