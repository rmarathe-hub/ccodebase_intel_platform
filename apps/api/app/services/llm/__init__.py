"""Optional LLM enrichment — parser ranges remain authoritative.

LangChain may be used as a thin Azure OpenAI adapter only.
Agents / free tool loops are forbidden for indexing enrichment.
"""

from app.services.llm.budget import EnrichmentBudget, EnrichmentBudgetExceeded
from app.services.llm.factory import get_llm_provider
from app.services.llm.null_provider import NullLLMProvider
from app.services.llm.provider import LLMProvider
from app.services.llm.schemas import (
    ConstructLabel,
    EnrichmentBatchResult,
    EnrichmentItem,
    RepositoryLlmSummary,
)

__all__ = [
    "ConstructLabel",
    "EnrichmentBatchResult",
    "EnrichmentBudget",
    "EnrichmentBudgetExceeded",
    "EnrichmentItem",
    "LLMProvider",
    "NullLLMProvider",
    "RepositoryLlmSummary",
    "get_llm_provider",
]
