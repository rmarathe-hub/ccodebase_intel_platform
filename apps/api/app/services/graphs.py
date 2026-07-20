"""Module and package graph builders from structural relations + deep files."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import SourceFile, Symbol, SymbolCall, SymbolRelation
from app.models.relation_kinds import RelationKind
from app.services.java_inheritance import package_of_qname
from app.services.python_imports import package_of_module
from app.services.relationships import _module_for_file, _target_module


@dataclass(frozen=True, slots=True)
class GraphNode:
    id: str
    label: str
    node_type: str  # module | package | symbol | directory | file
    language: str | None
    support_level: str
    path: str | None = None
    symbol_count: int = 0
    file_count: int = 0
    symbol_id: UUID | None = None
    kind: str | None = None


@dataclass(frozen=True, slots=True)
class GraphEdge:
    source: str
    target: str
    relation_kind: str
    confidence: str
    language: str | None
    weight: int = 1
    inferred: bool = False
    line: int | None = None


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


def _dir_of(path: str) -> str:
    cleaned = path.replace("\\", "/").strip("/")
    if not cleaned or "/" not in cleaned:
        return "."
    return cleaned.rsplit("/", 1)[0]


def _ancestor_dirs(path: str) -> list[str]:
    """Return directory paths from root to parent of file (inclusive)."""
    d = _dir_of(path)
    if d == ".":
        return ["."]
    parts = d.split("/")
    dirs: list[str] = []
    for i in range(1, len(parts) + 1):
        dirs.append("/".join(parts[:i]))
    return ["."] + dirs if "." not in dirs else dirs


def _merge_dir_support(existing: str, new: str) -> str:
    if existing == new:
        return existing
    if existing == "mixed" or new == "mixed":
        return "mixed"
    if existing == "deep" and new == "generic":
        return "mixed"
    if existing == "generic" and new == "deep":
        return "mixed"
    return new


def build_call_neighborhood_graph(
    session: Session,
    *,
    snapshot_id: UUID,
    center_symbol_id: UUID,
    depth: int = 1,
    confidence: str | None = None,
    language: str | None = None,
) -> tuple[list[GraphNode], list[GraphEdge], Symbol | None]:
    """BFS symbol graph from CALLS (deep languages only)."""
    depth = max(1, min(depth, 3))
    center = session.scalars(
        select(Symbol).where(
            Symbol.snapshot_id == snapshot_id,
            Symbol.id == center_symbol_id,
        )
    ).first()
    if center is None:
        return [], [], None

    sym_filters = [Symbol.snapshot_id == snapshot_id]
    if language:
        sym_filters.append(Symbol.language == language)
    symbols = list(session.scalars(select(Symbol).where(*sym_filters)).all())
    qname_to_sym = {s.qualified_name: s for s in symbols}
    id_to_sym = {s.id: s for s in symbols}

    call_filters = [SymbolCall.snapshot_id == snapshot_id]
    if confidence:
        call_filters.append(SymbolCall.confidence == confidence.lower())
    if language:
        call_filters.append(SymbolCall.language == language)
    calls = list(session.scalars(select(SymbolCall).where(*call_filters)).all())

    file_paths = {
        f.id: f.path
        for f in session.scalars(
            select(SourceFile).where(SourceFile.snapshot_id == snapshot_id)
        ).all()
    }

    def resolve_callee(call: SymbolCall) -> Symbol | None:
        if call.candidate_qualified_name and call.candidate_qualified_name in qname_to_sym:
            return qname_to_sym[call.candidate_qualified_name]
        return None

    def outgoing(from_sym: Symbol) -> list[tuple[Symbol, SymbolCall]]:
        out: list[tuple[Symbol, SymbolCall]] = []
        for call in calls:
            if call.caller_symbol_id != from_sym.id:
                continue
            callee = resolve_callee(call)
            if callee is not None:
                out.append((callee, call))
        return out

    def incoming(to_sym: Symbol) -> list[tuple[Symbol, SymbolCall]]:
        out: list[tuple[Symbol, SymbolCall]] = []
        for call in calls:
            if call.candidate_qualified_name == to_sym.qualified_name:
                if call.caller_symbol_id and call.caller_symbol_id in id_to_sym:
                    out.append((id_to_sym[call.caller_symbol_id], call))
        return out

    visited: set[UUID] = {center.id}
    frontier: set[UUID] = {center.id}
    edge_acc: dict[tuple[str, str, int], GraphEdge] = {}

    for _ in range(depth):
        next_frontier: set[UUID] = set()
        for sid in frontier:
            sym = id_to_sym.get(sid)
            if sym is None:
                continue
            for callee, call in outgoing(sym):
                key = (str(sym.id), str(callee.id), call.line)
                edge_acc[key] = GraphEdge(
                    source=str(sym.id),
                    target=str(callee.id),
                    relation_kind=RelationKind.CALLS.value,
                    confidence=call.confidence,
                    language=call.language,
                    inferred=False,
                    line=call.line,
                )
                if callee.id not in visited:
                    visited.add(callee.id)
                    next_frontier.add(callee.id)
            for caller, call in incoming(sym):
                key = (str(caller.id), str(sym.id), call.line)
                edge_acc[key] = GraphEdge(
                    source=str(caller.id),
                    target=str(sym.id),
                    relation_kind=RelationKind.CALLS.value,
                    confidence=call.confidence,
                    language=call.language,
                    inferred=False,
                    line=call.line,
                )
                if caller.id not in visited:
                    visited.add(caller.id)
                    next_frontier.add(caller.id)
        frontier = next_frontier

    nodes: list[GraphNode] = []
    for sid in sorted(visited, key=lambda x: str(x)):
        sym = id_to_sym.get(sid)
        if sym is None:
            continue
        path = file_paths.get(sym.source_file_id)
        nodes.append(
            GraphNode(
                id=str(sym.id),
                label=sym.qualified_name,
                node_type="symbol",
                language=sym.language,
                support_level="deep",
                path=path,
                symbol_id=sym.id,
                kind=sym.kind,
            )
        )

    edges = sorted(edge_acc.values(), key=lambda e: (e.source, e.target, e.line or 0))
    return nodes, edges, center


def build_directory_graph(
    session: Session,
    *,
    snapshot_id: UUID,
    include_files: bool = False,
) -> tuple[list[GraphNode], list[GraphEdge]]:
    """Directory hierarchy + optional file leaves; inferred cross-dir IMPORTS."""
    files = list(
        session.scalars(
            select(SourceFile).where(
                SourceFile.snapshot_id == snapshot_id,
                SourceFile.support_level != "skip",
            )
        ).all()
    )

    dirs: dict[str, GraphNode] = {}
    file_nodes: dict[str, GraphNode] = {}
    path_to_module: dict[str, str] = {}
    module_to_paths: dict[str, list[str]] = {}

    def ensure_dir(d: str, support: str) -> None:
        existing = dirs.get(d)
        if existing is None:
            dirs[d] = GraphNode(
                id=d,
                label="/" if d == "." else d,
                node_type="directory",
                language=None,
                support_level=support,
                file_count=0,
            )
        else:
            dirs[d] = GraphNode(
                id=existing.id,
                label=existing.label,
                node_type=existing.node_type,
                language=existing.language,
                support_level=_merge_dir_support(existing.support_level, support),
                file_count=existing.file_count,
            )

    for f in files:
        support = f.support_level
        lang = f.language
        if f.support_level == "deep" and f.language:
            mod = _module_for_file(f.path, f.language)
            if mod:
                path_to_module[f.path] = mod
                module_to_paths.setdefault(mod, []).append(f.path)

        parent = _dir_of(f.path)
        for d in _ancestor_dirs(f.path):
            ensure_dir(d, support)
        ensure_dir(parent, support)
        parent_node = dirs[parent]
        dirs[parent] = GraphNode(
            id=parent_node.id,
            label=parent_node.label,
            node_type=parent_node.node_type,
            language=parent_node.language,
            support_level=parent_node.support_level,
            file_count=parent_node.file_count + 1,
        )

        if include_files:
            file_id = f"file:{f.path}"
            file_nodes[file_id] = GraphNode(
                id=file_id,
                label=f.path.rsplit("/", 1)[-1],
                node_type="file",
                language=lang,
                support_level=support,
                path=f.path,
                file_count=1,
            )

    edge_acc: dict[tuple[str, str, str], GraphEdge] = {}

    for d in sorted(dirs):
        if d == ".":
            continue
        parent = _dir_of(d)
        key = (parent, d, RelationKind.CONTAINS.value)
        edge_acc[key] = GraphEdge(
            source=parent,
            target=d,
            relation_kind=RelationKind.CONTAINS.value,
            confidence="resolved",
            language=None,
            inferred=False,
        )

    if include_files:
        for file_id, node in file_nodes.items():
            assert node.path is not None
            parent = _dir_of(node.path)
            key = (parent, file_id, RelationKind.CONTAINS.value)
            edge_acc[key] = GraphEdge(
                source=parent,
                target=file_id,
                relation_kind=RelationKind.CONTAINS.value,
                confidence="resolved",
                language=None,
                inferred=False,
            )

    relations = list(
        session.scalars(
            select(SymbolRelation).where(
                SymbolRelation.snapshot_id == snapshot_id,
                SymbolRelation.relation_kind == RelationKind.IMPORTS.value,
            )
        ).all()
    )
    file_by_id = {f.id: f for f in files}
    known_modules = set(path_to_module.values())
    for rel in relations:
        src_file = file_by_id.get(rel.source_file_id)
        if src_file is None:
            continue
        src_dir = _dir_of(src_file.path)
        tgt_mod = _target_module(rel.candidate_qualified_name, known_modules=known_modules)
        if not tgt_mod or tgt_mod not in module_to_paths:
            continue
        tgt_dir = _dir_of(module_to_paths[tgt_mod][0])
        if src_dir == tgt_dir:
            continue
        key = (src_dir, tgt_dir, RelationKind.IMPORTS.value)
        prev = edge_acc.get(key)
        if prev is None:
            edge_acc[key] = GraphEdge(
                source=src_dir,
                target=tgt_dir,
                relation_kind=RelationKind.IMPORTS.value,
                confidence=rel.confidence,
                language=rel.language,
                weight=1,
                inferred=True,
            )
        else:
            edge_acc[key] = GraphEdge(
                source=prev.source,
                target=prev.target,
                relation_kind=prev.relation_kind,
                confidence=prev.confidence,
                language=prev.language,
                weight=prev.weight + 1,
                inferred=True,
            )

    nodes = sorted(dirs.values(), key=lambda n: n.id)
    if include_files:
        nodes = sorted([*nodes, *file_nodes.values()], key=lambda n: n.id)
    edges = sorted(edge_acc.values(), key=lambda e: (e.source, e.target, e.relation_kind))
    return nodes, edges

