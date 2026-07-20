"""EmbeddingProvider protocol — vectors only; never alters parser ranges."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class EmbeddingProvider(Protocol):
    """Batch-embed texts. Provider must not invent file/line citations."""

    @property
    def provider_name(self) -> str: ...

    @property
    def model_name(self) -> str: ...

    @property
    def dimensions(self) -> int: ...

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Return one L2-oriented vector per input text (same length as texts)."""
        ...
