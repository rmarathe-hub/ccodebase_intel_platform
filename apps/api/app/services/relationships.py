"""Build structural SymbolRelation edges (IMPORTS / EXPORTS / CONTAINS).

Runs after deep language symbol persist. Does not touch EXTENDS / IMPLEMENTS
(owned by the Java inheritance pass) or CALLS (stored in symbol_calls).
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.entities import SourceFile, Symbol, SymbolRelation
from app.models.relation_kinds import STRUCTURAL_RELATION_KINDS, RelationKind
from app.services.java_inheritance import package_of_qname
from app.services.js_ts_parser import module_qualified_name as js_module_qname
from app.services.python_ast_parser import module_qualified_name as py_module_qname

_CONTAINER_KINDS = frozenset({"class", "interface", "enum", "record"})
_MEMBER_KINDS = frozenset({"method", "function", "constructor"})
_EXPORT_KINDS = frozenset({"export"})
_IMPORT_KINDS = frozenset({"import"})


def _module_for_file(path: str, language: str) -> str:
    if language == "python":
        return py_module_qname(path)
    if language in {"javascript", "typescript"}:
        return js_module_qname(path)
    if language == "java":
        # Java file path often mirrors package; fall back to package of first type.
        cleaned = path.replace("\\", "/").removesuffix(".java")
        parts = [p for p in cleaned.split("/") if p and p != "."]
        return ".".join(parts)
    return path.replace("\\", "/").rsplit("/", 1)[-1]


def _target_module(resolved: str | None, *, known_modules: set[str]) -> str | None:
    if not resolved:
        return None
    if resolved in known_modules:
        return resolved
    # Strip trailing symbol leaf when parent module is known.
    if "." in resolved:
        parent = resolved.rsplit(".", 1)[0]
        if parent in known_modules:
            return parent
        # Java FQCN → package when package known as module-like key
        pkg = package_of_qname(resolved)
        if pkg and pkg in known_modules:
            return pkg
        return parent
    return resolved


def _import_confidence(sym: Symbol, *, known_modules: set[str]) -> str:
    resolved = (sym.resolved_module or "").strip()
    if not resolved:
        return "unresolved"
    if sym.is_local_import is True:
        target = _target_module(resolved, known_modules=known_modules)
        if target and target in known_modules:
            return "resolved"
        return "ambiguous" if target else "unresolved"
    if resolved in known_modules:
        return "resolved"
    target = _target_module(resolved, known_modules=known_modules)
    if target and target in known_modules:
        return "resolved"
    # External dependency (fastapi, spring, …)
    return "unresolved"


def replace_structural_relations_for_snapshot(
    session: Session,
    *,
    snapshot_id: UUID,
) -> dict[str, int]:
    """Replace IMPORTS / EXPORTS / CONTAINS for a snapshot; leave inheritance alone."""
    session.execute(
        delete(SymbolRelation).where(
            SymbolRelation.snapshot_id == snapshot_id,
            SymbolRelation.relation_kind.in_(sorted(STRUCTURAL_RELATION_KINDS)),
        )
    )
    session.flush()

    files = list(
        session.scalars(
            select(SourceFile).where(SourceFile.snapshot_id == snapshot_id)
        ).all()
    )
    file_by_id = {f.id: f for f in files}

    symbols = list(
        session.scalars(select(Symbol).where(Symbol.snapshot_id == snapshot_id)).all()
    )
    if not symbols:
        return {"imports": 0, "exports": 0, "contains": 0, "total": 0}

    # Known modules: deep file modules + symbol modules.
    known_modules: set[str] = set()
    for f in files:
        if f.support_level != "deep" or not f.language:
            continue
        mod = _module_for_file(f.path, f.language)
        if mod:
            known_modules.add(mod)

    qname_to_id = {s.qualified_name: s.id for s in symbols}
    # Also index modules that appear as qualified names on non-import symbols.
    for s in symbols:
        if s.kind in _IMPORT_KINDS | _EXPORT_KINDS:
            continue
        if s.language == "java":
            pkg = package_of_qname(s.qualified_name)
            if pkg:
                known_modules.add(pkg)
        elif "." in s.qualified_name:
            # module portion for py/js: drop leaf for members
            if s.kind in _MEMBER_KINDS | _CONTAINER_KINDS:
                parent = s.qualified_name.rsplit(".", 1)[0]
                if parent:
                    known_modules.add(parent)

    rows: list[SymbolRelation] = []
    counts = {"imports": 0, "exports": 0, "contains": 0}

    for sym in symbols:
        file_row = file_by_id.get(sym.source_file_id)
        if file_row is None:
            continue
        language = sym.language or file_row.language or "unknown"
        module = _module_for_file(file_row.path, language)

        if sym.kind in _IMPORT_KINDS:
            resolved = sym.resolved_module or sym.qualified_name
            target_mod = _target_module(resolved, known_modules=known_modules)
            to_id = qname_to_id.get(resolved) if resolved else None
            if to_id is None and target_mod:
                to_id = qname_to_id.get(target_mod)
            rows.append(
                SymbolRelation(
                    snapshot_id=snapshot_id,
                    source_file_id=sym.source_file_id,
                    from_symbol_id=None,
                    from_qualified_name=module or file_row.path,
                    relation_kind=RelationKind.IMPORTS.value,
                    raw_target=sym.name or resolved or "",
                    line=sym.start_line,
                    candidate_qualified_name=resolved,
                    to_symbol_id=to_id,
                    confidence=_import_confidence(sym, known_modules=known_modules),
                    language=language,
                )
            )
            counts["imports"] += 1

        elif sym.kind in _EXPORT_KINDS:
            rows.append(
                SymbolRelation(
                    snapshot_id=snapshot_id,
                    source_file_id=sym.source_file_id,
                    from_symbol_id=None,
                    from_qualified_name=module or file_row.path,
                    relation_kind=RelationKind.EXPORTS.value,
                    raw_target=sym.name or sym.qualified_name,
                    line=sym.start_line,
                    candidate_qualified_name=sym.qualified_name,
                    to_symbol_id=qname_to_id.get(sym.qualified_name),
                    confidence="resolved" if sym.qualified_name in qname_to_id else "unresolved",
                    language=language,
                )
            )
            counts["exports"] += 1

    # CONTAINS: container → member when member qname is nested under container.
    containers = [s for s in symbols if s.kind in _CONTAINER_KINDS]
    members = [s for s in symbols if s.kind in _MEMBER_KINDS]
    for container in containers:
        prefix = container.qualified_name + "."
        for member in members:
            if member.source_file_id != container.source_file_id:
                continue
            if not member.qualified_name.startswith(prefix):
                continue
            # Direct child only (one extra segment).
            rest = member.qualified_name[len(prefix) :]
            if "." in rest:
                continue
            rows.append(
                SymbolRelation(
                    snapshot_id=snapshot_id,
                    source_file_id=container.source_file_id,
                    from_symbol_id=container.id,
                    from_qualified_name=container.qualified_name,
                    relation_kind=RelationKind.CONTAINS.value,
                    raw_target=member.name,
                    line=member.start_line,
                    candidate_qualified_name=member.qualified_name,
                    to_symbol_id=member.id,
                    confidence="resolved",
                    language=container.language,
                )
            )
            counts["contains"] += 1

    session.add_all(rows)
    session.flush()
    counts["total"] = len(rows)
    return counts
