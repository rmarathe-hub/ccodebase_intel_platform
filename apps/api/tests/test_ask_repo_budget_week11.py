"""Week 11 Day 6: per-repository Ask budget."""

from __future__ import annotations

from uuid import uuid4

from app.core.config import Settings
from app.services.llm.budget import EnrichmentBudgetExceeded
from app.services.rag.ask_repo_budget import (
    consume_repository_ask_budget,
    reset_repository_ask_budget,
    snapshot_repository_ask_budget,
)


def test_per_repo_ask_budget_exhausts() -> None:
    reset_repository_ask_budget()
    repo = uuid4()
    conf = Settings(
        ask_max_requests_per_repository=2,
        ask_max_tokens_per_repository=1000,
        ask_max_estimated_cost_usd_per_repository=1.0,
    )
    consume_repository_ask_budget(repo, conf=conf)
    snap = snapshot_repository_ask_budget(repo, conf=conf)
    assert snap.requests_used == 1
    assert snap.remaining_requests == 1

    consume_repository_ask_budget(repo, conf=conf)
    try:
        consume_repository_ask_budget(repo, conf=conf)
        raised = False
    except EnrichmentBudgetExceeded:
        raised = True
    assert raised
    exhausted = snapshot_repository_ask_budget(repo, conf=conf)
    assert exhausted.exhausted or exhausted.requests_used >= exhausted.requests_limit
