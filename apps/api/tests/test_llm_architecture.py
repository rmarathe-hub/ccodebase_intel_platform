"""LLM enrichment architecture contracts (no paid API calls)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.core.config import Settings
from app.services.llm import (
    ConstructLabel,
    EnrichmentBudget,
    EnrichmentBudgetExceeded,
    EnrichmentItem,
    NullLLMProvider,
    get_llm_provider,
)
from app.services.llm.azure_openai import AzureOpenAIProvider
from app.services.llm.priority import EnrichmentPriority, pack_batches
from app.services.llm.schemas import LineRange
from app.services.llm.validation import (
    ChunkEvidenceBounds,
    validate_enrichment_item,
)


def test_factory_returns_null_when_disabled() -> None:
    provider = get_llm_provider(Settings(llm_enrichment_enabled=False, llm_provider="none"))
    assert isinstance(provider, NullLLMProvider)
    assert provider.provider_name == "none"


def test_factory_returns_azure_stub_when_configured() -> None:
    cfg = Settings(
        llm_enrichment_enabled=True,
        llm_provider="azure_openai",
        azure_openai_endpoint="https://example.openai.azure.com/",
        azure_openai_api_key="test-key-not-real",
        azure_openai_deployment="gpt-test",
    )
    provider = get_llm_provider(cfg)
    assert isinstance(provider, AzureOpenAIProvider)
    assert provider.provider_name == "azure_openai"
    with pytest.raises(NotImplementedError):
        provider.enrich_batch(items=[], prompt_version="1")


def test_factory_null_when_azure_incomplete() -> None:
    cfg = Settings(
        llm_enrichment_enabled=True,
        llm_provider="azure_openai",
        azure_openai_endpoint="",
        azure_openai_api_key="",
        azure_openai_deployment="",
    )
    assert isinstance(get_llm_provider(cfg), NullLLMProvider)


def test_budget_blocks_overspend() -> None:
    budget = EnrichmentBudget(max_requests=2, max_tokens=100, max_estimated_cost_usd=0.1)
    budget.consume(requests=1, tokens=40, cost_usd=0.04)
    budget.consume(requests=1, tokens=40, cost_usd=0.04)
    with pytest.raises(EnrichmentBudgetExceeded):
        budget.consume(requests=1, tokens=1, cost_usd=0.0)
    assert budget.skipped_reason == "budget_exceeded"


def test_pack_batches_never_forces_singleton_policy() -> None:
    items = [(EnrichmentPriority.README_DOCS, f"c{i}") for i in range(5)]
    batches = pack_batches(items, max_chunks_per_request=3)
    assert batches == [["c0", "c1", "c2"], ["c3", "c4"]]


def test_validation_rejects_out_of_bounds_and_deep_claim() -> None:
    bounds = {
        "a": ChunkEvidenceBounds(
            chunk_id="a",
            path="main.go",
            start_line=10,
            end_line=20,
            content="func main() {}",
        )
    }
    bad = EnrichmentItem(
        chunk_id="a",
        path="main.go",
        semantic_label="entry",
        concise_summary="main",
        probable_construct_type=ConstructLabel.ENTRY_POINT_CANDIDATE,
        entry_point_likelihood=0.9,
        confidence=0.8,
        evidence_line_ranges=[LineRange(start_line=1, end_line=5)],
        claims_verified_deep=True,
    )
    result = validate_enrichment_item(bad, bounds)
    assert result.ok is False
    assert any("verified_deep" in e for e in result.errors)
    assert any("outside" in e for e in result.errors)


def test_construct_label_is_enum_only() -> None:
    with pytest.raises(ValidationError):
        EnrichmentItem(
            chunk_id="a",
            path="x",
            semantic_label="s",
            concise_summary="c",
            probable_construct_type="not_a_real_label",  # type: ignore[arg-type]
            entry_point_likelihood=0.1,
            confidence=0.1,
            evidence_line_ranges=[LineRange(start_line=1, end_line=1)],
        )


def test_null_enrich_batch_empty() -> None:
    out = NullLLMProvider().enrich_batch(items=[{"chunk_id": "1"}], prompt_version="1")
    assert out.items == []
    assert out.provider == "none"
