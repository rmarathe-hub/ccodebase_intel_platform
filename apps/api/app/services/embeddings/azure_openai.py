"""Azure OpenAI embeddings — Foundry v1 and legacy Azure OpenAI endpoints."""

from __future__ import annotations

import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# Azure text-embedding-3-small input cap (8192 tokens); conservative for dense code.
MAX_EMBEDDING_INPUT_CHARS = 6_000


def _clip_embedding_input(text: str) -> str:
    if len(text) <= MAX_EMBEDDING_INPUT_CHARS:
        return text
    return text[:MAX_EMBEDDING_INPUT_CHARS]


def _endpoint_hostname(endpoint: str) -> str:
    parsed = urlparse(endpoint if "://" in endpoint else f"https://{endpoint}")
    return parsed.hostname or endpoint


def endpoint_type(endpoint: str) -> str:
    host = _endpoint_hostname(endpoint).lower()
    if host.endswith("services.ai.azure.com"):
        return "foundry_v1"
    if host.endswith("openai.azure.com"):
        return "legacy_azure_openai"
    return "unknown"


def normalize_azure_resource_endpoint(endpoint: str) -> str:
    """Return Azure OpenAI resource root (scheme://host) for *.openai.azure.com URLs.

    Accepts pasted deployment/embeddings URLs with path/query and strips them so
    AzureOpenAI(azure_endpoint=...) receives the resource root only.
    """
    raw = (endpoint or "").strip()
    if not raw:
        return raw
    parsed = urlparse(raw if "://" in raw else f"https://{raw}")
    host = (parsed.hostname or "").lower()
    if host.endswith("openai.azure.com") and parsed.scheme and parsed.netloc:
        return f"{parsed.scheme}://{parsed.netloc}"
    return raw.rstrip("/")


def _foundry_v1_base_url(endpoint: str) -> str:
    base = endpoint.rstrip("/")
    if base.endswith("/openai/v1"):
        return base + "/"
    if base.endswith("/openai/v1/"):
        return base
    return base + "/openai/v1/"


def _validate_vector(vector: list[float], dimensions: int) -> list[float]:
    if len(vector) != dimensions:
        raise RuntimeError(
            f"Azure embedding returned {len(vector)} dimensions; expected {dimensions}"
        )
    return vector


class AzureOpenAIEmbeddingProvider:
    """Azure embeddings via Foundry v1 (OpenAI client) or legacy AzureOpenAI."""

    provider_name = "azure_openai"

    def __init__(
        self,
        *,
        endpoint: str,
        api_key: str,
        api_version: str,
        deployment: str,
        model_name: str | None = None,
        dimensions: int,
        timeout_seconds: float = 60.0,
        max_retries: int = 2,
    ) -> None:
        self._endpoint = normalize_azure_resource_endpoint(endpoint)
        self._api_key = api_key
        self._api_version = api_version
        self._deployment = deployment
        self._model_name = model_name or deployment
        self._dimensions = dimensions
        self._timeout_seconds = timeout_seconds
        self._max_retries = max_retries
        self._endpoint_kind = endpoint_type(self._endpoint)

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def dimensions(self) -> int:
        return self._dimensions

    @property
    def endpoint_kind(self) -> str:
        return self._endpoint_kind

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        clipped = [_clip_embedding_input(t) for t in texts]
        try:
            if self._endpoint_kind == "foundry_v1":
                return self._embed_foundry_v1(clipped)
            return self._embed_legacy_azure(clipped)
        except Exception:
            logger.exception(
                "Azure embedding request failed endpoint_type=%s deployment=%s",
                self._endpoint_kind,
                self._deployment,
            )
            raise

    def _embed_foundry_v1(self, texts: list[str]) -> list[list[float]]:
        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "openai package required for Azure embeddings (pip install '.[llm]')"
            ) from exc

        client = OpenAI(
            api_key=self._api_key,
            base_url=_foundry_v1_base_url(self._endpoint),
            timeout=self._timeout_seconds,
            max_retries=self._max_retries,
        )
        response = client.embeddings.create(
            model=self._deployment,
            input=texts,
            dimensions=self._dimensions,
        )
        return self._vectors_from_response(response, len(texts))

    def _embed_legacy_azure(self, texts: list[str]) -> list[list[float]]:
        try:
            from openai import AzureOpenAI
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "openai package required for Azure embeddings (pip install '.[llm]')"
            ) from exc

        client = AzureOpenAI(
            azure_endpoint=self._endpoint + "/",
            api_key=self._api_key,
            api_version=self._api_version,
            timeout=self._timeout_seconds,
            max_retries=self._max_retries,
        )
        response = client.embeddings.create(
            model=self._deployment,
            input=texts,
            dimensions=self._dimensions,
        )
        return self._vectors_from_response(response, len(texts))

    def _vectors_from_response(self, response: object, count: int) -> list[list[float]]:
        data = getattr(response, "data", None)
        if not data:
            raise RuntimeError("Azure embedding response contained no data")
        by_index = {item.index: item.embedding for item in data}
        out: list[list[float]] = []
        for i in range(count):
            if i not in by_index:
                raise RuntimeError(f"Azure embedding response missing index {i}")
            out.append(_validate_vector(list(by_index[i]), self._dimensions))
        return out
