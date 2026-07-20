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
    file_count: int = 0
    symbol_id: UUID | None = None
    kind: str | None = None


class GraphEdgeRead(BaseModel):
    source: str
    target: str
    relation_kind: str
    confidence: str
    language: str | None = None
    weight: int = 1
    inferred: bool = False
    line: int | None = None


class RepositoryGraphResponse(BaseModel):
    repository_id: UUID
    snapshot_id: UUID | None
    graph_type: str
    node_count: int
    edge_count: int
    center_symbol_id: UUID | None = None
    depth: int | None = None
    filters: dict[str, object] = Field(default_factory=dict)
    nodes: list[GraphNodeRead] = Field(default_factory=list)
    edges: list[GraphEdgeRead] = Field(default_factory=list)
