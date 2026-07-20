"""Chunk embedding providers (Week 9) — local default, Azure optional."""

from app.services.embeddings.constants import EMBEDDING_DIMENSIONS
from app.services.embeddings.factory import get_embedding_provider
from app.services.embeddings.local_hash import LocalHashEmbeddingProvider, hash_embed_text
from app.services.embeddings.null_provider import NullEmbeddingProvider
from app.services.embeddings.persist import replace_embeddings_for_snapshot
from app.services.embeddings.provider import EmbeddingProvider

__all__ = [
    "EMBEDDING_DIMENSIONS",
    "EmbeddingProvider",
    "LocalHashEmbeddingProvider",
    "NullEmbeddingProvider",
    "get_embedding_provider",
    "hash_embed_text",
    "replace_embeddings_for_snapshot",
]
