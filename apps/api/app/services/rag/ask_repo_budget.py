"""Process-local per-repository Ask budgets (Week 11 Day 6)."""

from __future__ import annotations

from dataclasses import dataclass
from threading import Lock
from uuid import UUID

from app.core.config import Settings, settings
from app.services.llm.budget import EnrichmentBudget, EnrichmentBudgetExceeded

_lock = Lock()
_budgets: dict[UUID, EnrichmentBudget] = {}


@dataclass(frozen=True, slots=True)
class AskRepoBudgetSnapshot:
    repository_id: UUID
    requests_used: int
    requests_limit: int
    tokens_used: int
    tokens_limit: int
    estimated_cost_usd: float
    cost_limit_usd: float
    exhausted: bool
    skipped_reason: str | None
    remaining_requests: int


def _new_budget(conf: Settings) -> EnrichmentBudget:
    return EnrichmentBudget(
        max_requests=max(1, conf.ask_max_requests_per_repository),
        max_tokens=max(1, conf.ask_max_tokens_per_repository),
        max_estimated_cost_usd=max(0.0, conf.ask_max_estimated_cost_usd_per_repository),
    )


def get_repository_ask_budget(
    repository_id: UUID,
    *,
    conf: Settings | None = None,
) -> EnrichmentBudget:
    cfg = conf or settings
    with _lock:
        budget = _budgets.get(repository_id)
        if budget is None:
            budget = _new_budget(cfg)
            _budgets[repository_id] = budget
        return budget


def snapshot_repository_ask_budget(
    repository_id: UUID,
    *,
    conf: Settings | None = None,
) -> AskRepoBudgetSnapshot:
    cfg = conf or settings
    budget = get_repository_ask_budget(repository_id, conf=cfg)
    return AskRepoBudgetSnapshot(
        repository_id=repository_id,
        requests_used=budget.requests_used,
        requests_limit=budget.max_requests,
        tokens_used=budget.tokens_used,
        tokens_limit=budget.max_tokens,
        estimated_cost_usd=budget.estimated_cost_usd,
        cost_limit_usd=budget.max_estimated_cost_usd,
        exhausted=budget.skipped_reason is not None,
        skipped_reason=budget.skipped_reason,
        remaining_requests=max(0, budget.max_requests - budget.requests_used),
    )


def reset_repository_ask_budget(repository_id: UUID | None = None) -> None:
    """Test helper: clear one or all per-repo Ask budgets."""
    with _lock:
        if repository_id is None:
            _budgets.clear()
        else:
            _budgets.pop(repository_id, None)


def consume_repository_ask_budget(
    repository_id: UUID,
    *,
    requests: int = 1,
    tokens: int = 0,
    cost_usd: float = 0.0,
    conf: Settings | None = None,
) -> AskRepoBudgetSnapshot:
    budget = get_repository_ask_budget(repository_id, conf=conf)
    budget.consume(requests=requests, tokens=tokens, cost_usd=cost_usd)
    return snapshot_repository_ask_budget(repository_id, conf=conf)


__all__ = [
    "AskRepoBudgetSnapshot",
    "EnrichmentBudgetExceeded",
    "consume_repository_ask_budget",
    "get_repository_ask_budget",
    "reset_repository_ask_budget",
    "snapshot_repository_ask_budget",
]
