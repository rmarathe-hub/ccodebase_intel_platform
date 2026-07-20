"""Deterministic local hash embeddings — CI-safe, no network, no ML deps."""

from __future__ import annotations

import hashlib
import math
import struct

from app.services.embeddings.constants import EMBEDDING_DIMENSIONS


def hash_embed_text(text: str, *, dimensions: int = EMBEDDING_DIMENSIONS) -> list[float]:
    """Expand SHA-256 rounds into a fixed-dim unit vector (deterministic)."""
    if dimensions < 1:
        raise ValueError("dimensions must be >= 1")
    values: list[float] = []
    counter = 0
    payload = text.encode("utf-8", errors="replace")
    while len(values) < dimensions:
        digest = hashlib.sha256(counter.to_bytes(4, "big") + payload).digest()
        for offset in range(0, len(digest), 4):
            if len(values) >= dimensions:
                break
            raw = struct.unpack_from(">i", digest, offset)[0]
            values.append(raw / 2147483648.0)
        counter += 1
    norm = math.sqrt(sum(v * v for v in values)) or 1.0
    return [v / norm for v in values]


class LocalHashEmbeddingProvider:
    """Default Week 9 provider: stable vectors for plumbing + hybrid tests."""

    provider_name = "local"

    def __init__(
        self,
        *,
        model_name: str = "local-hash-v1",
        dimensions: int = EMBEDDING_DIMENSIONS,
    ) -> None:
        self._model_name = model_name
        self._dimensions = dimensions

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def dimensions(self) -> int:
        return self._dimensions

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [hash_embed_text(t, dimensions=self._dimensions) for t in texts]
