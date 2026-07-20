"""API schemas for module / package graphs."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field


class GraphNodeRead(BaseModel):
    id: str
    label: str
    node_type: str
    language: str | None = None
    support_level: str
    path: str | None = None
    symbol_count: int = 0


class GraphEdgeRead(BaseModel):
    source: str
    target: str
    relation_kind: str
    confidence: str
    language: str | None = None
    weight: int = 1
    inferred: bool = False


class RepositoryGraphResponse(BaseModel):
    repository_id: UUID
    snapshot_id: UUID | None
    graph_type: str
    node_count: int
    edge_count: int
    nodes: list[GraphNodeRead] = Field(default_factory=list)
    edges: list[GraphEdgeRead] = Field(default_factory=list)
