#!/usr/bin/env python3
"""Run Week 9 hybrid weight eval and write REPORT.md + results.json."""

from __future__ import annotations

import json
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models import Base
from app.services.hybrid_weight_eval import render_report_markdown, run_hybrid_weight_eval

OUT_DIR = Path(__file__).resolve().parents[3] / "docs" / "testing" / "week9-hybrid-eval"


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    engine = create_engine(settings.database_url, pool_pre_ping=True)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = SessionLocal()
    try:
        with tempfile.TemporaryDirectory(prefix="hybrid-weight-eval-") as tmp:
            result = run_hybrid_weight_eval(session, work_dir=Path(tmp))
        result["generated_at"] = datetime.now(UTC).isoformat()
        (OUT_DIR / "results.json").write_text(
            json.dumps(result, indent=2, default=str) + "\n", encoding="utf-8"
        )
        report = render_report_markdown(result)
        (OUT_DIR / "REPORT.md").write_text(report, encoding="utf-8")
        print(f"Wrote {OUT_DIR / 'REPORT.md'}", flush=True)
        print(f"Wrote {OUT_DIR / 'results.json'}", flush=True)
        print(f"WINNER={result['winner']}", flush=True)
        return 0
    finally:
        session.close()
        engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
