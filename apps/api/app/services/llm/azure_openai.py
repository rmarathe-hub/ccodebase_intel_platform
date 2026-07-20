"""Azure OpenAI enrichment via LangChain (default). Direct SDK only if LC unavailable."""

from __future__ import annotations

import json
import logging
from typing import Any

from app.services.llm.schemas import (
    ConstructLabel,
    EnrichmentBatchResult,
    EnrichmentItem,
    LineRange,
    RepositoryLlmSummary,
)

logger = logging.getLogger(__name__)


class AzureOpenAIProvider:
    """LangChain + Azure OpenAI structured enrichment. Not an agent runtime."""

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
        self.endpoint = endpoint.rstrip("/")
        self.api_key = api_key
        self.api_version = api_version
        self.deployment = deployment
        self.orchestration = orchestration
        self.temperature = temperature
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries

    def _langchain_model(self) -> Any:
        from langchain_openai import AzureChatOpenAI

        return AzureChatOpenAI(
            azure_endpoint=self.endpoint,
            api_key=self.api_key,
            api_version=self.api_version,
            azure_deployment=self.deployment,
            temperature=self.temperature,
            timeout=self.timeout_seconds,
            max_retries=self.max_retries,
        )

    def enrich_batch(
        self,
        *,
        items: list[dict[str, object]],
        prompt_version: str,
    ) -> EnrichmentBatchResult:
        """One LLM call per logical batch (not per chunk). Prefer LangChain."""
        if not items:
            return EnrichmentBatchResult(
                items=[],
                model=self.deployment,
                prompt_version=prompt_version,
                provider=self.provider_name,
            )

        use_langchain = self.orchestration in {"auto", "langchain"}
        if use_langchain:
            try:
                return self._enrich_batch_langchain(items=items, prompt_version=prompt_version)
            except ImportError:
                logger.warning(
                    "LangChain not installed; falling back to direct Azure OpenAI SDK "
                    "for enrich_batch only (install optional [llm] extra for LangChain)"
                )
                if self.orchestration == "langchain":
                    raise
            except Exception:
                if self.orchestration == "langchain":
                    raise
                logger.exception(
                    "LangChain enrich_batch failed; trying direct Azure OpenAI SDK"
                )

        return self._enrich_batch_direct(items=items, prompt_version=prompt_version)

    def _enrich_batch_langchain(
        self,
        *,
        items: list[dict[str, object]],
        prompt_version: str,
    ) -> EnrichmentBatchResult:
        from langchain_core.prompts import ChatPromptTemplate

        class _BatchOut(EnrichmentBatchResult):
            pass

        llm = self._langchain_model().with_structured_output(_BatchOut)
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You enrich parser-derived code chunks. Never invent line ranges "
                    "outside the supplied start/end. Never claim verified deep analysis. "
                    "claims_verified_deep must always be false. "
                    "probable_construct_type must be one of the allowed enum values. "
                    "Return one enrichment item per input chunk_id. Prompt version: {pv}.",
                ),
                (
                    "human",
                    "Enrich this batch of chunks as JSON matching the schema.\n{payload}",
                ),
            ]
        )
        chain = prompt | llm
        result = chain.invoke(
            {"pv": prompt_version, "payload": json.dumps(items, ensure_ascii=False)}
        )
        if isinstance(result, EnrichmentBatchResult):
            return EnrichmentBatchResult(
                items=result.items,
                model=self.deployment,
                prompt_version=prompt_version,
                provider=self.provider_name,
            )
        # Some LC versions return dict.
        return EnrichmentBatchResult.model_validate(result)

    def _enrich_batch_direct(
        self,
        *,
        items: list[dict[str, object]],
        prompt_version: str,
    ) -> EnrichmentBatchResult:
        """Direct Azure OpenAI SDK path — used only when LangChain is unavailable."""
        from openai import AzureOpenAI

        client = AzureOpenAI(
            azure_endpoint=self.endpoint,
            api_key=self.api_key,
            api_version=self.api_version,
            timeout=self.timeout_seconds,
            max_retries=self.max_retries,
        )
        schema = EnrichmentBatchResult.model_json_schema()
        completion = client.beta.chat.completions.parse(
            model=self.deployment,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Enrich parser-derived chunks. Never invent ranges outside "
                        "supplied bounds. claims_verified_deep must be false. "
                        f"Prompt version: {prompt_version}."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(items, ensure_ascii=False),
                },
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "EnrichmentBatchResult",
                    "schema": schema,
                    "strict": False,
                },
            },
            temperature=self.temperature,
        )
        raw = completion.choices[0].message.content or "{}"
        parsed = EnrichmentBatchResult.model_validate_json(raw)
        return EnrichmentBatchResult(
            items=parsed.items,
            model=self.deployment,
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
        """LangChain structured summary grounded in deterministic metadata + evidence."""
        use_langchain = self.orchestration in {"auto", "langchain"}
        payload = {
            "deterministic_summary": deterministic_summary,
            "evidence": evidence,
            "prompt_version": prompt_version,
        }
        if use_langchain:
            try:
                return self._summarize_langchain(payload=payload, prompt_version=prompt_version)
            except ImportError:
                logger.warning(
                    "LangChain not installed; falling back to direct Azure OpenAI SDK "
                    "for summarize_repository only"
                )
                if self.orchestration == "langchain":
                    raise
            except Exception:
                if self.orchestration == "langchain":
                    raise
                logger.exception(
                    "LangChain summarize_repository failed; trying direct Azure OpenAI SDK"
                )
        return self._summarize_direct(payload=payload, prompt_version=prompt_version)

    def _summarize_langchain(
        self,
        *,
        payload: dict[str, object],
        prompt_version: str,
    ) -> RepositoryLlmSummary:
        from langchain_core.prompts import ChatPromptTemplate

        llm = self._langchain_model().with_structured_output(RepositoryLlmSummary)
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You write an enhanced repository summary from deterministic metadata "
                    "and supplied evidence chunks. Never invent line ranges outside evidence. "
                    "claims_verified_deep must be false. Cite evidence_line_ranges from "
                    "supplied chunk lines only. Prompt version: {pv}.",
                ),
                ("human", "{body}"),
            ]
        )
        result = (prompt | llm).invoke(
            {"pv": prompt_version, "body": json.dumps(payload, ensure_ascii=False)}
        )
        if isinstance(result, RepositoryLlmSummary):
            return result.model_copy(
                update={
                    "model": self.deployment,
                    "prompt_version": prompt_version,
                    "provider": self.provider_name,
                    "claims_verified_deep": False,
                }
            )
        parsed = RepositoryLlmSummary.model_validate(result)
        return parsed.model_copy(
            update={
                "model": self.deployment,
                "prompt_version": prompt_version,
                "provider": self.provider_name,
                "claims_verified_deep": False,
            }
        )

    def _summarize_direct(
        self,
        *,
        payload: dict[str, object],
        prompt_version: str,
    ) -> RepositoryLlmSummary:
        from openai import AzureOpenAI

        client = AzureOpenAI(
            azure_endpoint=self.endpoint,
            api_key=self.api_key,
            api_version=self.api_version,
            timeout=self.timeout_seconds,
            max_retries=self.max_retries,
        )
        schema = RepositoryLlmSummary.model_json_schema()
        completion = client.beta.chat.completions.parse(
            model=self.deployment,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Enhanced repository summary from deterministic metadata + evidence. "
                        "Never invent ranges. claims_verified_deep=false. "
                        f"Prompt version: {prompt_version}."
                    ),
                },
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "RepositoryLlmSummary",
                    "schema": schema,
                    "strict": False,
                },
            },
            temperature=self.temperature,
        )
        raw = completion.choices[0].message.content or "{}"
        parsed = RepositoryLlmSummary.model_validate_json(raw)
        return parsed.model_copy(
            update={
                "model": self.deployment,
                "prompt_version": prompt_version,
                "provider": self.provider_name,
                "claims_verified_deep": False,
            }
        )


def mock_enrichment_for_items(
    items: list[dict[str, object]],
    *,
    prompt_version: str,
    model: str = "mock",
) -> EnrichmentBatchResult:
    """Deterministic mock used by tests — no network."""
    out: list[EnrichmentItem] = []
    for item in items:
        start = int(item["start_line"])
        end = int(item["end_line"])
        out.append(
            EnrichmentItem(
                chunk_id=str(item["chunk_id"]),
                path=str(item["path"]),
                semantic_label="mock_label",
                concise_summary="mock summary",
                probable_construct_type=ConstructLabel.UNKNOWN,
                entry_point_likelihood=0.1,
                confidence=0.5,
                evidence_line_ranges=[LineRange(start_line=start, end_line=end)],
                claims_verified_deep=False,
            )
        )
    return EnrichmentBatchResult(
        items=out,
        model=model,
        prompt_version=prompt_version,
        provider="mock",
    )
