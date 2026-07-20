"""Factory: local hash by default; Azure when configured; null when disabled."""

from __future__ import annotations

from app.core.config import Settings, settings
from app.services.embeddings.azure_openai import AzureOpenAIEmbeddingProvider
from app.services.embeddings.local_hash import LocalHashEmbeddingProvider
from app.services.embeddings.null_provider import NullEmbeddingProvider
from app.services.embeddings.provider import EmbeddingProvider


def get_embedding_provider(cfg: Settings | None = None) -> EmbeddingProvider:
    conf = cfg or settings
    if not conf.embeddings_active:
        return NullEmbeddingProvider()

    if conf.embedding_provider == "azure_openai":
        if not conf.azure_openai_embeddings_configured:
            return NullEmbeddingProvider()
        api_key = conf.azure_openai_api_key.strip() or conf.llm_api_key.strip()
        return AzureOpenAIEmbeddingProvider(
            endpoint=conf.azure_openai_endpoint.strip(),
            api_key=api_key,
            api_version=conf.azure_openai_api_version.strip(),
            deployment=conf.azure_openai_embedding_deployment.strip(),
            model_name=conf.embedding_model.strip()
            or conf.azure_openai_embedding_deployment.strip(),
            dimensions=conf.embedding_dimensions,
            timeout_seconds=conf.llm_timeout_seconds,
            max_retries=conf.llm_max_retries,
        )

    if conf.embedding_provider == "local":
        return LocalHashEmbeddingProvider(
            model_name=conf.embedding_model.strip() or "local-hash-v1",
            dimensions=conf.embedding_dimensions,
        )

    return NullEmbeddingProvider()
