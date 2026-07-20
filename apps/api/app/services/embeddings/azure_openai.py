"""Optional Azure OpenAI embeddings — pad/truncate to platform dimensions."""

from __future__ import annotations

import logging
import math

from app.services.embeddings.constants import EMBEDDING_DIMENSIONS

logger = logging.getLogger(__name__)


def _fit_dimensions(vector: list[float], dimensions: int) -> list[float]:
    if len(vector) == dimensions:
        out = vector
    elif len(vector) > dimensions:
        out = vector[:dimensions]
    else:
        out = vector + [0.0] * (dimensions - len(vector))
    norm = math.sqrt(sum(v * v for v in out)) or 1.0
    return [v / norm for v in out]


class AzureOpenAIEmbeddingProvider:
    """Thin Azure embeddings client. Optional; not required for CI."""

    provider_name = "azure_openai"

    def __init__(
        self,
        *,
        endpoint: str,
        api_key: str,
        api_version: str,
        deployment: str,
        model_name: str | None = None,
        dimensions: int = EMBEDDING_DIMENSIONS,
        timeout_seconds: float = 60.0,
        max_retries: int = 2,
    ) -> None:
        self._endpoint = endpoint.rstrip("/")
        self._api_key = api_key
        self._api_version = api_version
        self._deployment = deployment
        self._model_name = model_name or deployment
        self._dimensions = dimensions
        self._timeout_seconds = timeout_seconds
        self._max_retries = max_retries

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def dimensions(self) -> int:
        return self._dimensions

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        try:
            from openai import AzureOpenAI
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "openai package required for Azure embeddings (pip install '.[llm]')"
            ) from exc

        client = AzureOpenAI(
            azure_endpoint=self._endpoint,
            api_key=self._api_key,
            api_version=self._api_version,
            timeout=self._timeout_seconds,
            max_retries=self._max_retries,
        )
        response = client.embeddings.create(model=self._deployment, input=texts)
        by_index = {item.index: item.embedding for item in response.data}
        out: list[list[float]] = []
        for i in range(len(texts)):
            raw = list(by_index[i])
            out.append(_fit_dimensions(raw, self._dimensions))
        return out
