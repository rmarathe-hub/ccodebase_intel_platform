"""Spring / Java annotation + architecture heuristics (Week 6 Days 3 + 5).

Honesty: annotation-name and naming heuristics — not classpath-aware Spring Boot.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_ANNOTATION_LEAF = re.compile(r"^@?(?:[\w.]+\.)?(\w+)")

_CLASS_ROLES: dict[str, str] = {
    "RestController": "spring_rest_controller",
    "Controller": "spring_controller",
    "Service": "spring_service",
    "Repository": "spring_repository",
    "Component": "spring_component",
    "Configuration": "spring_configuration",
    "SpringBootApplication": "spring_configuration",
    "Entity": "spring_entity",
}

_ROUTE_ANNOTATIONS = frozenset(
    {
        "GetMapping",
        "PostMapping",
        "PutMapping",
        "PatchMapping",
        "DeleteMapping",
        "RequestMapping",
    }
)

_BEAN_ROLES = frozenset(
    {
        "spring_rest_controller",
        "spring_controller",
        "spring_service",
        "spring_repository",
        "spring_component",
        "spring_configuration",
        "spring_entity",
        "spring_implementation",
    }
)

_ROLE_PRIORITY = (
    "spring_rest_controller",
    "spring_controller",
    "spring_service",
    "spring_repository",
    "spring_configuration",
    "spring_entity",
    "spring_component",
    "spring_implementation",
    "spring_interface",
    "spring_route",
)


@dataclass(frozen=True, slots=True)
class FrameworkMeta:
    role: str
    detail: str | None = None


@dataclass(frozen=True, slots=True)
class ArchitectureSymbol:
    kind: str
    name: str
    qualified_name: str
    framework_role: str | None
    framework_detail: str | None


def annotation_leaf(decorator: str) -> str:
    """``@org.springframework.stereotype.Service`` → ``Service``."""
    text = decorator.strip()
    match = _ANNOTATION_LEAF.match(text)
    return match.group(1) if match else text.lstrip("@").split("(")[0].rsplit(".", 1)[-1]


def detect_java_framework_meta(
    *,
    kind: str,
    decorators: tuple[str, ...],
) -> FrameworkMeta | None:
    """Best-effort Spring role from annotations on a symbol."""
    if not decorators:
        return None

    leaves = [annotation_leaf(d) for d in decorators]
    detail = "; ".join(decorators)

    if kind in {"class", "interface", "enum", "record"}:
        found: list[str] = []
        for leaf in leaves:
            role = _CLASS_ROLES.get(leaf)
            if role and role not in found:
                found.append(role)
        if found:
            found.sort(key=lambda r: _ROLE_PRIORITY.index(r) if r in _ROLE_PRIORITY else 99)
            return FrameworkMeta(role=found[0], detail=detail)
        return None

    if kind in {"method", "constructor"}:
        for leaf in leaves:
            if leaf in _ROUTE_ANNOTATIONS:
                return FrameworkMeta(role="spring_route", detail=detail)
    return None


def _naming_role(kind: str, name: str) -> str | None:
    if kind == "interface":
        if name.endswith(("Api", "Service", "Repository", "Port", "Gateway")):
            return "spring_interface"
        return None
    if kind not in {"class", "record"}:
        return None
    if name.endswith("RestController"):
        return "spring_rest_controller"
    if name.endswith("Controller"):
        return "spring_controller"
    if name.endswith("ServiceImpl") or (
        name.endswith("Impl") and not name.endswith("Controller")
    ):
        return "spring_implementation"
    if name.endswith("Service"):
        return "spring_service"
    if name.endswith("Repository"):
        return "spring_repository"
    if name.endswith(("Configuration", "Config")):
        return "spring_configuration"
    if name.endswith("Entity"):
        return "spring_entity"
    return None


def _merge_detail(existing: str | None, extra: str) -> str:
    if not existing:
        return extra
    if extra in existing:
        return existing
    return f"{existing}; {extra}"


def _current_role(
    qname: str,
    *,
    by_qname: dict[str, ArchitectureSymbol],
    updates: dict[str, FrameworkMeta],
) -> str | None:
    if qname in updates:
        return updates[qname].role
    sym = by_qname.get(qname)
    return sym.framework_role if sym else None


def _current_detail(
    qname: str,
    *,
    by_qname: dict[str, ArchitectureSymbol],
    updates: dict[str, FrameworkMeta],
) -> str | None:
    if qname in updates:
        return updates[qname].detail
    sym = by_qname.get(qname)
    return sym.framework_detail if sym else None


def classify_spring_architecture(
    symbols: list[ArchitectureSymbol],
    *,
    implements_edges: list[tuple[str, str]],
) -> dict[str, FrameworkMeta]:
    """Cross-file Spring architecture pass (Day 5).

    ``implements_edges`` is ``(from_class_qname, interface_qname)`` for resolved
    IMPLEMENTS relations only.
    """
    by_qname = {s.qualified_name: s for s in symbols}
    implementors: dict[str, list[str]] = {}
    for from_q, to_q in implements_edges:
        implementors.setdefault(to_q, []).append(from_q)

    updates: dict[str, FrameworkMeta] = {}

    for sym in symbols:
        if sym.kind not in {"class", "interface", "enum", "record"}:
            continue
        role = sym.framework_role
        detail = sym.framework_detail
        if role is None:
            named = _naming_role(sym.kind, sym.name)
            if named:
                role = named
                detail = _merge_detail(detail, f"naming:{sym.name}")
        if role is not None:
            updates[sym.qualified_name] = FrameworkMeta(role=role, detail=detail)

    for iface_q, from_list in implementors.items():
        iface = by_qname.get(iface_q)
        if iface is None or iface.kind != "interface":
            continue
        role = _current_role(iface_q, by_qname=by_qname, updates=updates)
        if role is None:
            role = "spring_interface"
        detail = _current_detail(iface_q, by_qname=by_qname, updates=updates)
        detail = _merge_detail(
            detail, "implemented_by:" + ",".join(sorted(from_list)[:5])
        )
        updates[iface_q] = FrameworkMeta(role=role, detail=detail)

    for from_q, to_q in implements_edges:
        impl_sym = by_qname.get(from_q)
        if impl_sym is None or impl_sym.kind not in {"class", "record"}:
            continue
        role = _current_role(from_q, by_qname=by_qname, updates=updates)
        detail = _current_detail(from_q, by_qname=by_qname, updates=updates)
        detail = _merge_detail(detail, f"implements:{to_q}")
        if role is None:
            role = "spring_implementation"
        elif role not in _BEAN_ROLES and impl_sym.name.endswith("Impl"):
            role = "spring_implementation"
        updates[from_q] = FrameworkMeta(role=role, detail=detail)

    return updates
