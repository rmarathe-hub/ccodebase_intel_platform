#!/usr/bin/env python3
"""Run Week 10 Ask/RAG eval matrix and write REPORT.md + results.json."""

from __future__ import annotations

import json
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from pydantic_settings import SettingsConfigDict
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import Settings, settings
from app.models import Base
from app.services.rag.ask_eval import render_ask_eval_report, run_ask_eval

OUT_DIR = Path(__file__).resolve().parents[3] / "docs" / "testing" / "week10-ask-eval"


class _EvalSettings(Settings):
    model_config = SettingsConfigDict(env_file=None, extra="ignore")
    embedding_provider: str = "local"
    embedding_model: str = "local-hash-v1"
    embedding_dimensions: int = 1536
    embeddings_enabled: bool = True
    ask_enabled: bool = True
    ask_use_mock: bool = True
    ask_cache_enabled: bool = False
    ask_rerank_use_mock: bool = True
    ask_query_rewrite_enabled: bool = True
    llm_kill_switch: bool = False


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # Default: local-hash embeddings (CI-safe). Opt into Azure with ASK_EVAL_USE_AZURE=1.
    import os

    use_azure = os.environ.get("ASK_EVAL_USE_AZURE", "").lower() in {"1", "true", "yes"}
    cfg = _EvalSettings()
    if (
        use_azure
        and settings.azure_openai_embeddings_configured
        and settings.embedding_provider == "azure_openai"
    ):
        cfg = _EvalSettings(
            embedding_provider="azure_openai",
            embedding_model=settings.embedding_model or "text-embedding-3-small",
            embedding_dimensions=settings.embedding_dimensions,
            azure_openai_endpoint=settings.azure_openai_endpoint,
            azure_openai_api_key=settings.azure_openai_api_key,
            azure_openai_embedding_deployment=settings.azure_openai_embedding_deployment,
        )

    engine = create_engine(settings.database_url, pool_pre_ping=True)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = SessionLocal()
    try:
        with tempfile.TemporaryDirectory(prefix="ask-eval-") as tmp:
            result = run_ask_eval(session, work_dir=Path(tmp), cfg=cfg)
        result["generated_at"] = datetime.now(UTC).isoformat()
        (OUT_DIR / "results.json").write_text(
            json.dumps(result, indent=2, default=str) + "\n", encoding="utf-8"
        )
        report = render_ask_eval_report(result)
        (OUT_DIR / "REPORT.md").write_text(report, encoding="utf-8")
        print(f"Wrote {OUT_DIR / 'REPORT.md'}", flush=True)
        print(f"Wrote {OUT_DIR / 'results.json'}", flush=True)
        print(f"WINNER={result['winner']}", flush=True)
        print(f"KEEP_LLM={result['keep_llm_path']}", flush=True)
        return 0
    finally:
        session.close()
        engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
