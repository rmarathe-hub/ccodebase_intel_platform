"""Structured schemas for Ask/RAG LLM reranking (Week 10 Day 2)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class RerankItem(BaseModel):
    chunk_id: str = Field(min_length=1, max_length=64)
    relevance_score: float = Field(ge=0.0, le=1.0)
    relevance_reason: str = Field(min_length=1, max_length=500)


class RerankBatchResult(BaseModel):
    items: list[RerankItem] = Field(default_factory=list)
