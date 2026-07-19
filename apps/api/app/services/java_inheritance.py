"""Java EXTENDS / IMPLEMENTS extraction and resolution (Week 6 Day 4).

Honesty: name / import / same-package / unique-project heuristics — not javac.
Confidence: resolved | ambiguous | unresolved.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ExtractedRelation:
    from_qualified_name: str
    relation_kind: str  # extends | implements
    raw_target: str
    line: int
    package: str
    candidate_qualified_name: str | None = None
    confidence: str = "unresolved"


@dataclass(frozen=True, slots=True)
class TypeRef:
    kind: str
    name: str
    qualified_name: str
    package: str


_TYPE_KINDS = frozenset({"class", "interface", "enum", "record"})


def package_of_qname(qname: str) -> str:
    if "." not in qname:
        return ""
    return qname.rsplit(".", 1)[0]


def build_type_indexes(
    types: list[TypeRef],
) -> tuple[dict[str, TypeRef], dict[str, list[TypeRef]]]:
    by_qname = {t.qualified_name: t for t in types}
    by_simple: dict[str, list[TypeRef]] = defaultdict(list)
    for t in types:
        by_simple[t.name].append(t)
    return by_qname, by_simple


def import_leaf_map(import_symbols: list[tuple[str, str | None]]) -> dict[str, str]:
    """``(name, resolved_module)`` → simple binding → FQN."""
    out: dict[str, str] = {}
    for name, resolved in import_symbols:
        if not name or not resolved:
            continue
        if "*" in name or resolved.endswith(".*"):
            continue
        out[name] = resolved
    return out


def resolve_type_name(
    raw: str,
    *,
    package: str,
    imports: dict[str, str],
    by_qname: dict[str, TypeRef],
    by_simple: dict[str, list[TypeRef]],
) -> tuple[str | None, str]:
    """Resolve a Java type reference to a project qualified name when possible."""
    target = raw.strip()
    if not target:
        return None, "unresolved"

    # Strip generics: List<Foo> is not an inheritance target we emit, but be safe.
    if "<" in target:
        target = target.split("<", 1)[0].strip()

    if "." in target:
        if target in by_qname:
            return target, "resolved"
        return target, "unresolved"

    if target in imports:
        fqn = imports[target]
        if fqn in by_qname:
            return fqn, "resolved"
        return fqn, "unresolved"

    same = f"{package}.{target}" if package else target
    if same in by_qname:
        return same, "resolved"

    hits = by_simple.get(target, [])
    if len(hits) == 1:
        return hits[0].qualified_name, "resolved"
    if len(hits) > 1:
        return None, "ambiguous"
    return None, "unresolved"


def resolve_relations(
    edges: list[ExtractedRelation],
    *,
    types: list[TypeRef],
    imports_by_from: dict[str, dict[str, str]],
) -> tuple[ExtractedRelation, ...]:
    """Attach confidence + candidate to raw inheritance edges."""
    by_qname, by_simple = build_type_indexes(
        [t for t in types if t.kind in _TYPE_KINDS]
    )
    out: list[ExtractedRelation] = []
    for edge in edges:
        imports = imports_by_from.get(edge.from_qualified_name, {})
        # Also allow file-level imports keyed by package for types in that package.
        package_imports = imports_by_from.get(edge.package, {})
        merged = {**package_imports, **imports}
        candidate, confidence = resolve_type_name(
            edge.raw_target,
            package=edge.package,
            imports=merged,
            by_qname=by_qname,
            by_simple=by_simple,
        )
        out.append(
            ExtractedRelation(
                from_qualified_name=edge.from_qualified_name,
                relation_kind=edge.relation_kind,
                raw_target=edge.raw_target,
                line=edge.line,
                package=edge.package,
                candidate_qualified_name=candidate,
                confidence=confidence,
            )
        )
    out.sort(
        key=lambda e: (
            e.line,
            e.relation_kind,
            e.from_qualified_name,
            e.raw_target,
        )
    )
    return tuple(out)
