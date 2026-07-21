"""Week 9 hybrid weight eval: three configs × identifier/NL metrics."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy.orm import Session

from pydantic_settings import SettingsConfigDict

from app.core.config import Settings
from app.services.hybrid_weight_eval import (
    WEIGHT_CONFIGS,
    load_queries,
    render_report_markdown,
    run_hybrid_weight_eval,
)
from tests.conftest import requires_postgres

pytestmark = requires_postgres


class _LocalEvalSettings(Settings):
    model_config = SettingsConfigDict(env_file=None, extra="ignore")
    embedding_provider: str = "local"
    embedding_dimensions: int = 1536
    hybrid_w_exact: float = 0.50
    hybrid_w_semantic: float = 0.50


def test_hybrid_weight_eval_three_configs(db_session: Session, tmp_path: Path) -> None:
    queries = load_queries()
    assert len(queries) >= 12
    assert {q.style for q in queries} == {"identifier", "natural_language"}

    result = run_hybrid_weight_eval(db_session, work_dir=tmp_path, cfg=_LocalEvalSettings())
    assert set(result["configs"]) == {name for name, _, _ in WEIGHT_CONFIGS}
    assert result["winner"] in result["configs"]
    assert result["ranking"][0] == result["winner"]

    for name, w_exact, w_semantic in WEIGHT_CONFIGS:
        cfg = result["configs"][name]
        assert cfg["w_exact"] == w_exact
        assert cfg["w_semantic"] == w_semantic
        for bucket in ("overall", "identifier", "natural_language"):
            m = cfg[bucket]
            assert m["n"] >= 1
            assert 0.0 <= m["recall_at_5"] <= 1.0
            assert 0.0 <= m["recall_at_10"] <= 1.0
            assert 0.0 <= m["mrr"] <= 1.0
            assert m["recall_at_10"] + 1e-9 >= m["recall_at_5"]

    # Default settings should match the intended 50/50 baseline.
    cfg = _LocalEvalSettings()
    assert abs(cfg.hybrid_w_exact - 0.50) < 1e-9
    assert abs(cfg.hybrid_w_semantic - 0.50) < 1e-9

    md = render_report_markdown(result)
    assert "Recall@5" in md
    assert result["winner"] in md
