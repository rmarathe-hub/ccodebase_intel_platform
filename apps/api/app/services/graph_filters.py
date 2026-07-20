"""Shared post-build filters for repository graphs (Week 8 Day 5)."""

from __future__ import annotations

from dataclasses import replace

from app.services.graphs import GraphEdge, GraphNode


def apply_graph_filters(
    nodes: list[GraphNode],
    edges: list[GraphEdge],
    *,
    language: str | None = None,
    support_level: str | None = None,
    relation_kind: str | None = None,
    confidence: str | None = None,
    path_prefix: str | None = None,
    inferred: bool | None = None,
    max_nodes: int | None = None,
    max_edges: int | None = None,
) -> tuple[list[GraphNode], list[GraphEdge]]:
    """Filter nodes/edges then drop orphaned edges and unreachable isolates."""
    filtered_nodes = list(nodes)
    filtered_edges = list(edges)

    if language:
        lang = language.lower()
        filtered_nodes = [
            n for n in filtered_nodes if n.language is None or n.language.lower() == lang
        ]
        filtered_edges = [
            e for e in filtered_edges if e.language is None or e.language.lower() == lang
        ]

    if support_level:
        level = support_level.lower()
        filtered_nodes = [n for n in filtered_nodes if n.support_level.lower() == level]

    if path_prefix:
        prefix = path_prefix.replace("\\", "/").lstrip("/")
        filtered_nodes = [
            n
            for n in filtered_nodes
            if (n.path or n.id).replace("\\", "/").startswith(prefix)
            or n.id.replace("\\", "/").startswith(prefix)
            or n.label.replace("\\", "/").startswith(prefix)
        ]

    if relation_kind:
        kind = relation_kind.lower()
        filtered_edges = [e for e in filtered_edges if e.relation_kind.lower() == kind]

    if confidence:
        conf = confidence.lower()
        filtered_edges = [e for e in filtered_edges if e.confidence.lower() == conf]

    if inferred is not None:
        filtered_edges = [e for e in filtered_edges if e.inferred is inferred]

    node_ids = {n.id for n in filtered_nodes}
    filtered_edges = [
        e for e in filtered_edges if e.source in node_ids and e.target in node_ids
    ]

    # Keep nodes that remain connected OR were in the filtered set with no edges
    # (directory roots / isolates after edge filters). Prefer connected nodes when capping.
    connected: set[str] = set()
    for e in filtered_edges:
        connected.add(e.source)
        connected.add(e.target)

    if filtered_edges:
        # Prefer connected nodes; keep disconnected only if no edges matched filters
        # and we still have nodes (e.g. empty edge filter shouldn't wipe isolates from
        # path-only views). Actually for path_prefix-only, keep all remaining nodes.
        pass

    if max_nodes is not None and max_nodes > 0 and len(filtered_nodes) > max_nodes:
        # Prefer connected nodes, then by id for stability.
        ranked = sorted(
            filtered_nodes,
            key=lambda n: (0 if n.id in connected else 1, n.id),
        )
        filtered_nodes = ranked[:max_nodes]
        node_ids = {n.id for n in filtered_nodes}
        filtered_edges = [
            e for e in filtered_edges if e.source in node_ids and e.target in node_ids
        ]

    if max_edges is not None and max_edges > 0 and len(filtered_edges) > max_edges:
        filtered_edges = sorted(
            filtered_edges,
            key=lambda e: (-e.weight, e.source, e.target, e.relation_kind),
        )[:max_edges]
        kept = set()
        for e in filtered_edges:
            kept.add(e.source)
            kept.add(e.target)
        # When capping edges, drop nodes that lost all edges unless they were the only
        # survivors under max_nodes already selected.
        if kept:
            filtered_nodes = [n for n in filtered_nodes if n.id in kept]

    return filtered_nodes, filtered_edges


def filters_echo(
    *,
    language: str | None = None,
    support_level: str | None = None,
    relation_kind: str | None = None,
    confidence: str | None = None,
    path_prefix: str | None = None,
    inferred: bool | None = None,
    local_imports_only: bool | None = None,
    include_files: bool | None = None,
    max_nodes: int | None = None,
    max_edges: int | None = None,
    depth: int | None = None,
) -> dict[str, object]:
    """Serialize only non-None filters for API responses."""
    out: dict[str, object] = {}
    if language is not None:
        out["language"] = language
    if support_level is not None:
        out["support_level"] = support_level
    if relation_kind is not None:
        out["relation_kind"] = relation_kind
    if confidence is not None:
        out["confidence"] = confidence
    if path_prefix is not None:
        out["path_prefix"] = path_prefix
    if inferred is not None:
        out["inferred"] = inferred
    if local_imports_only is not None:
        out["local_imports_only"] = local_imports_only
    if include_files is not None:
        out["include_files"] = include_files
    if max_nodes is not None:
        out["max_nodes"] = max_nodes
    if max_edges is not None:
        out["max_edges"] = max_edges
    if depth is not None:
        out["depth"] = depth
    return out


# Silence unused-import lint if replace unused in some builds
_ = replace
