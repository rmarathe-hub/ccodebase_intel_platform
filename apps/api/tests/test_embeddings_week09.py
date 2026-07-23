"""Week 9 Day 1: EmbeddingProvider contract + local hash determinism."""

from __future__ import annotations

import math

import pytest
from pydantic_settings import SettingsConfigDict

from pydantic_settings import SettingsConfigDict

from app.core.config import Settings
from app.services.embeddings import (
    EMBEDDING_DIMENSIONS,
    LocalHashEmbeddingProvider,
    NullEmbeddingProvider,
    get_embedding_provider,
    hash_embed_text,
)


class _LocalOnlySettings(Settings):
    model_config = SettingsConfigDict(env_file=None, extra="ignore")
    embedding_provider: str = "local"
    embedding_dimensions: int = EMBEDDING_DIMENSIONS


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
    provider = get_embedding_provider(_LocalOnlySettings())
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


def test_azure_provider_validates_dimensions() -> None:
    from app.services.embeddings.azure_openai import _validate_vector

    assert _validate_vector([1.0, 0.0, 0.0], 3) == [1.0, 0.0, 0.0]
    with pytest.raises(RuntimeError):
        _validate_vector([1.0], 3)


def test_endpoint_type_detection() -> None:
    from app.services.embeddings.azure_openai import endpoint_type

    assert endpoint_type("https://foo.services.ai.azure.com") == "foundry_v1"
    assert endpoint_type("https://foo.openai.azure.com/") == "legacy_azure_openai"

    from app.services.embeddings.azure_openai import normalize_azure_resource_endpoint

    assert (
        normalize_azure_resource_endpoint(
            "https://foo.openai.azure.com/openai/deployments/x/embeddings?api-version=1"
        )
        == "https://foo.openai.azure.com"
    )
    assert (
        normalize_azure_resource_endpoint("https://foo.openai.azure.com/")
        == "https://foo.openai.azure.com"
    )


def test_hash_embed_rejects_bad_dims() -> None:
    with pytest.raises(ValueError):
        hash_embed_text("x", dimensions=0)
