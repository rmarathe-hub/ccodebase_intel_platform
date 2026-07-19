"""Factory: Null when disabled; Azure OpenAI stub when configured and enabled."""

from __future__ import annotations

from app.core.config import Settings, settings
from app.services.llm.azure_openai import AzureOpenAIProvider
from app.services.llm.null_provider import NullLLMProvider
from app.services.llm.provider import LLMProvider


def get_llm_provider(cfg: Settings | None = None) -> LLMProvider:
    conf = cfg or settings
    if not conf.llm_enrichment_active:
        return NullLLMProvider()

    if conf.llm_provider == "azure_openai":
        api_key = conf.azure_openai_api_key.strip() or conf.llm_api_key.strip()
        if not conf.azure_openai_configured:
            return NullLLMProvider()
        return AzureOpenAIProvider(
            endpoint=conf.azure_openai_endpoint.strip(),
            api_key=api_key,
            api_version=conf.azure_openai_api_version.strip(),
            deployment=conf.azure_openai_deployment.strip(),
            orchestration=conf.llm_orchestration,
            temperature=conf.llm_temperature,
            timeout_seconds=conf.llm_timeout_seconds,
            max_retries=conf.llm_max_retries,
        )

    # Other providers stay swappable; until implemented, fail closed to null.
    return NullLLMProvider()
