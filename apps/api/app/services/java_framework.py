"""Spring / Java annotation heuristics (Week 6 Day 3).

Honesty: annotation-name matching only — not classpath-aware Spring Boot analysis.
Day 5 may refine architecture classification further.
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

# Prefer more specific class roles when multiple stereotype annotations appear.
_ROLE_PRIORITY = (
    "spring_rest_controller",
    "spring_controller",
    "spring_service",
    "spring_repository",
    "spring_configuration",
    "spring_entity",
    "spring_component",
    "spring_route",
)


@dataclass(frozen=True, slots=True)
class FrameworkMeta:
    role: str
    detail: str | None = None


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
