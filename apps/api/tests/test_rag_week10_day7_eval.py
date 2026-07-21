"""Week 10 Day 7: Ask/RAG eval matrix (hybrid vs rewrite vs rerank vs full RAG)."""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import SettingsConfigDict
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.services.hybrid_weight_eval import load_queries
from app.services.rag.ask_eval import (
    MODES,
    render_ask_eval_report,
    run_ask_eval,
)
from tests.conftest import requires_postgres

pytestmark = requires_postgres


class _LocalAskEvalSettings(Settings):
    model_config = SettingsConfigDict(env_file=None, extra="ignore")
    embedding_provider: str = "local"
    embedding_model: str = "local-hash-v1"
    embedding_version: str = "9.2"
    embedding_dimensions: int = 1536
    embeddings_enabled: bool = True
    hybrid_w_exact: float = 0.50
    hybrid_w_semantic: float = 0.50
    ask_enabled: bool = True
    ask_use_mock: bool = True
    ask_cache_enabled: bool = False
    ask_rerank_use_mock: bool = True
    ask_rerank_enabled: bool = True
    ask_query_rewrite_enabled: bool = True
    ask_query_max_rewrites: int = 4
    ask_context_token_budget: int = 6000
    llm_kill_switch: bool = False


def test_ask_eval_four_modes(db_session: Session, tmp_path: Path) -> None:
    queries = load_queries()
    assert len(queries) >= 12

    result = run_ask_eval(
        db_session,
        work_dir=tmp_path,
        cfg=_LocalAskEvalSettings(),
    )
    assert set(result["configs"]) == set(MODES)
    assert result["winner"] in result["configs"]
    assert result["ranking"][0] == result["winner"]
    assert "keep_llm_path" in result

    for mode in MODES:
        cfg = result["configs"][mode]
        for bucket in ("overall", "identifier", "natural_language"):
            m = cfg[bucket]
            assert m["n"] >= 1
            assert 0.0 <= m["recall_at_5"] <= 1.0
            assert 0.0 <= m["recall_at_10"] <= 1.0
            assert 0.0 <= m["mrr"] <= 1.0
            assert m["recall_at_10"] + 1e-9 >= m["recall_at_5"]
        assert cfg["latency_ms_mean"] >= 0.0

    full = result["configs"]["full_rag"]
    assert "citation_correctness_mean" in full
    assert 0.0 <= full["citation_correctness_mean"] <= 1.0
    assert 0.0 <= full["unsupported_claim_rate_mean"] <= 1.0
    # Mock grounded answers cite evidence spans → high citation correctness.
    assert full["citation_correctness_mean"] >= 0.9

    md = render_ask_eval_report(result)
    assert "Recall@5" in md
    assert result["winner"] in md
    assert "full_rag" in md
