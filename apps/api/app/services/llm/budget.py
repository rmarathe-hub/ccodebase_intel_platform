"""Per-job enrichment budget. Over budget → skip LLM only."""

from __future__ import annotations

from dataclasses import dataclass, field


class EnrichmentBudgetExceeded(Exception):
    """Raised when a job would exceed configured LLM limits."""


@dataclass
class EnrichmentBudget:
    max_requests: int
    max_tokens: int
    max_estimated_cost_usd: float
    requests_used: int = 0
    tokens_used: int = 0
    estimated_cost_usd: float = 0.0
    skipped_reason: str | None = field(default=None, init=False)

    def can_afford(self, *, requests: int = 1, tokens: int = 0, cost_usd: float = 0.0) -> bool:
        if self.skipped_reason is not None:
            return False
        if self.requests_used + requests > self.max_requests:
            return False
        if self.tokens_used + tokens > self.max_tokens:
            return False
        if self.estimated_cost_usd + cost_usd > self.max_estimated_cost_usd:
            return False
        return True

    def consume(
        self,
        *,
        requests: int = 1,
        tokens: int = 0,
        cost_usd: float = 0.0,
    ) -> None:
        if not self.can_afford(requests=requests, tokens=tokens, cost_usd=cost_usd):
            self.skipped_reason = self.skipped_reason or "budget_exceeded"
            raise EnrichmentBudgetExceeded(self.skipped_reason)
        self.requests_used += requests
        self.tokens_used += tokens
        self.estimated_cost_usd += cost_usd

    def mark_exhausted(self, reason: str = "budget_exceeded") -> None:
        self.skipped_reason = reason
