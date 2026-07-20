"""Week 9 Day 1: EmbeddingProvider contract + local hash determinism."""

from __future__ import annotations

import math

import pytest
from pydantic_settings import SettingsConfigDict

from app.core.config import Settings
from app.services.embeddings import (
    EMBEDDING_DIMENSIONS,
    LocalHashEmbeddingProvider,
    NullEmbeddingProvider,
    get_embedding_provider,
    hash_embed_text,
)
from app.services.embeddings.azure_openai import _fit_dimensions


def test_hash_embed_text_deterministic_and_unit_length() -> None:
    a = hash_embed_text("def foo():\n    return 1\n")
    b = hash_embed_text("def foo():\n    return 1\n")
    c = hash_embed_text("def bar():\n    return 2\n")
    assert a == b
    assert a != c
    assert len(a) == EMBEDDING_DIMENSIONS
    norm = math.sqrt(sum(x * x for x in a))
    assert abs(norm - 1.0) < 1e-6


def test_local_provider_batch_matches_len() -> None:
    provider = LocalHashEmbeddingProvider()
    vectors = provider.embed_texts(["one", "two", "three"])
    assert len(vectors) == 3
    assert all(len(v) == provider.dimensions for v in vectors)
    assert provider.provider_name == "local"


def test_null_provider_returns_empty() -> None:
    provider = NullEmbeddingProvider()
    assert provider.embed_texts(["x"]) == []
    assert provider.dimensions == 0


def test_factory_defaults_to_local() -> None:
    provider = get_embedding_provider(Settings())
    assert isinstance(provider, LocalHashEmbeddingProvider)


def test_factory_disabled_returns_null() -> None:
    class Disabled(Settings):
        model_config = SettingsConfigDict(env_file=None, extra="ignore")
        embeddings_enabled: bool = False

    provider = get_embedding_provider(Disabled())
    assert isinstance(provider, NullEmbeddingProvider)


def test_factory_none_provider_returns_null() -> None:
    class NoneProv(Settings):
        model_config = SettingsConfigDict(env_file=None, extra="ignore")
        embedding_provider: str = "none"

    provider = get_embedding_provider(NoneProv())
    assert isinstance(provider, NullEmbeddingProvider)


def test_fit_dimensions_pad_and_truncate() -> None:
    padded = _fit_dimensions([1.0, 0.0], 4)
    assert len(padded) == 4
    truncated = _fit_dimensions([1.0, 0.0, 0.0, 0.0, 0.5], 2)
    assert len(truncated) == 2
    assert abs(math.sqrt(sum(x * x for x in truncated)) - 1.0) < 1e-6


def test_hash_embed_rejects_bad_dims() -> None:
    with pytest.raises(ValueError):
        hash_embed_text("x", dimensions=0)
