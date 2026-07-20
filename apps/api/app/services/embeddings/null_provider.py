"""No-op embedding provider when embeddings are disabled."""

from __future__ import annotations


class NullEmbeddingProvider:
    provider_name = "none"
    model_name = ""
    dimensions = 0

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        _ = texts
        return []
