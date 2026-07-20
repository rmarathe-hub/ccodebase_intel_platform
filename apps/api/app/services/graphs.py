"""Module and package graph builders from structural relations + deep files."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import SourceFile, Symbol, SymbolRelation
from app.models.relation_kinds import RelationKind
from app.services.java_inheritance import package_of_qname
from app.services.python_imports import package_of_module
from app.services.relationships import _module_for_file, _target_module


@dataclass(frozen=True, slots=True)
class GraphNode:
    id: str
    label: str
    node_type: str  # module | package
    language: str | None
    support_level: str
    path: str | None = None
    symbol_count: int = 0


@dataclass(frozen=True, slots=True)
class GraphEdge:
    source: str
    target: str
    relation_kind: str
    confidence: str
    language: str | None
    weight: int = 1
    inferred: bool = False


def _package_for_module(module: str, language: str | None) -> str:
    if not module:
        return ""
    if language == "java":
        # Java modules in our graph are often FQN paths; package is parent.
        return package_of_qname(module) if "." in module else module
    if language == "python":
        return package_of_module(module)
    if language in {"javascript", "typescript"}:
        return package_of_module(module)
    return package_of_module(module) if "." in module else module


def build_module_graph(
    session: Session,
    *,
    snapshot_id: UUID,
    language: str | None = None,
    local_imports_only: bool = False,
) -> tuple[list[GraphNode], list[GraphEdge]]:
    """Module nodes + IMPORTS edges between modules (deep languages)."""
    files = list(
        session.scalars(
            select(SourceFile).where(
                SourceFile.snapshot_id == snapshot_id,
                SourceFile.support_level == "deep",
            )
        ).all()
    )
    if language:
        files = [f for f in files if f.language == language]

    modules: dict[str, GraphNode] = {}
    known_modules: set[str] = set()
    for f in files:
        if not f.language:
            continue
        mod = _module_for_file(f.path, f.language)
        if not mod:
            continue
        known_modules.add(mod)
        existing = modules.get(mod)
        if existing is None:
            modules[mod] = GraphNode(
                id=mod,
                label=mod,
                node_type="module",
                language=f.language,
                support_level="deep",
                path=f.path,
                symbol_count=0,
            )

    symbols = list(
        session.scalars(select(Symbol).where(Symbol.snapshot_id == snapshot_id)).all()
    )
    if language:
        symbols = [s for s in symbols if s.language == language]
    for s in symbols:
        if s.kind in {"import", "export"}:
            continue
        mod = None
        if s.language == "python":
            from app.services.python_calls import module_from_qname

            mod = module_from_qname(s.qualified_name, s.kind, s.name)
        elif s.language in {"javascript", "typescript"}:
            from app.services.js_ts_calls import module_from_qname as js_mod

            mod = js_mod(s.qualified_name, s.kind, s.name)
        elif s.language == "java":
            mod = package_of_qname(s.qualified_name) or s.qualified_name
        if mod and mod in modules:
            n = modules[mod]
            modules[mod] = GraphNode(
                id=n.id,
                label=n.label,
                node_type=n.node_type,
                language=n.language,
                support_level=n.support_level,
                path=n.path,
                symbol_count=n.symbol_count + 1,
            )
        elif mod and mod not in modules and language is None:
            # Include module-like packages referenced by symbols when filtering off
            pass

    rel_filters = [
        SymbolRelation.snapshot_id == snapshot_id,
        SymbolRelation.relation_kind == RelationKind.IMPORTS.value,
    ]
    if language:
        rel_filters.append(SymbolRelation.language == language)

    relations = list(session.scalars(select(SymbolRelation).where(*rel_filters)).all())

    edge_acc: dict[tuple[str, str, str, str], GraphEdge] = {}
    for rel in relations:
        if local_imports_only and rel.confidence != "resolved":
            continue
        src = rel.from_qualified_name
        tgt = _target_module(rel.candidate_qualified_name, known_modules=known_modules)
        if not src or not tgt or src == tgt:
            continue
        # Ensure nodes exist for external resolved locals
        if src not in modules:
            modules[src] = GraphNode(
                id=src,
                label=src,
                node_type="module",
                language=rel.language,
                support_level="deep",
            )
        if tgt not in modules:
            # External / unresolved target — still show if confidence resolved/ambiguous
            if rel.confidence == "unresolved" and local_imports_only:
                continue
            modules[tgt] = GraphNode(
                id=tgt,
                label=tgt,
                node_type="module",
                language=rel.language,
                support_level="deep" if tgt in known_modules else "generic",
            )
            if modules[tgt].support_level == "generic" and local_imports_only:
                # drop external
                modules.pop(tgt, None)
                continue
        key = (src, tgt, rel.relation_kind, rel.confidence)
        prev = edge_acc.get(key)
        if prev is None:
            edge_acc[key] = GraphEdge(
                source=src,
                target=tgt,
                relation_kind=rel.relation_kind,
                confidence=rel.confidence,
                language=rel.language,
                weight=1,
                inferred=False,
            )
        else:
            edge_acc[key] = GraphEdge(
                source=prev.source,
                target=prev.target,
                relation_kind=prev.relation_kind,
                confidence=prev.confidence,
                language=prev.language,
                weight=prev.weight + 1,
                inferred=prev.inferred,
            )

    nodes = sorted(modules.values(), key=lambda n: n.id)
    edges = sorted(edge_acc.values(), key=lambda e: (e.source, e.target, e.confidence))
    return nodes, edges


def build_package_graph(
    session: Session,
    *,
    snapshot_id: UUID,
    language: str | None = None,
    local_imports_only: bool = True,
) -> tuple[list[GraphNode], list[GraphEdge]]:
    """Package nodes + aggregated IMPORTS between packages."""
    mod_nodes, mod_edges = build_module_graph(
        session,
        snapshot_id=snapshot_id,
        language=language,
        local_imports_only=local_imports_only,
    )
    packages: dict[str, GraphNode] = {}
    module_to_pkg: dict[str, str] = {}

    for n in mod_nodes:
        pkg = _package_for_module(n.id, n.language) or n.id
        module_to_pkg[n.id] = pkg
        existing = packages.get(pkg)
        if existing is None:
            packages[pkg] = GraphNode(
                id=pkg,
                label=pkg,
                node_type="package",
                language=n.language,
                support_level=n.support_level,
                symbol_count=n.symbol_count,
            )
        else:
            packages[pkg] = GraphNode(
                id=existing.id,
                label=existing.label,
                node_type="package",
                language=existing.language or n.language,
                support_level=existing.support_level,
                symbol_count=existing.symbol_count + n.symbol_count,
            )

    edge_acc: dict[tuple[str, str, str, str], GraphEdge] = {}
    for e in mod_edges:
        sp = module_to_pkg.get(e.source) or _package_for_module(e.source, e.language)
        tp = module_to_pkg.get(e.target) or _package_for_module(e.target, e.language)
        if not sp or not tp or sp == tp:
            continue
        if sp not in packages:
            packages[sp] = GraphNode(
                id=sp,
                label=sp,
                node_type="package",
                language=e.language,
                support_level="deep",
            )
        if tp not in packages:
            packages[tp] = GraphNode(
                id=tp,
                label=tp,
                node_type="package",
                language=e.language,
                support_level="deep",
            )
        key = (sp, tp, e.relation_kind, e.confidence)
        prev = edge_acc.get(key)
        if prev is None:
            edge_acc[key] = GraphEdge(
                source=sp,
                target=tp,
                relation_kind=e.relation_kind,
                confidence=e.confidence,
                language=e.language,
                weight=e.weight,
                inferred=True,  # aggregated from module imports
            )
        else:
            edge_acc[key] = GraphEdge(
                source=prev.source,
                target=prev.target,
                relation_kind=prev.relation_kind,
                confidence=prev.confidence,
                language=prev.language,
                weight=prev.weight + e.weight,
                inferred=True,
            )

    nodes = sorted(packages.values(), key=lambda n: n.id)
    edges = sorted(edge_acc.values(), key=lambda e: (e.source, e.target, e.confidence))
    return nodes, edges
