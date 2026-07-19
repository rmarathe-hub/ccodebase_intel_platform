"""Python import resolution helpers (Week 4 Day 4).

Resolves absolute/relative imports to a dotted module path and classifies
local (in-repo) versus external (stdlib / third-party) using known repo modules.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass

_STDLIB_TOP: frozenset[str] = frozenset(getattr(sys, "stdlib_module_names", ()))


@dataclass(frozen=True, slots=True)
class ResolvedImport:
    """One imported binding after resolution."""

    binding_name: str
    imported_name: str
    resolved_module: str
    style: str  # absolute | relative
    is_local: bool
    alias: str | None
    level: int = 0


def package_of_module(module_qname: str) -> str:
    """Parent package of a module (``app.services.auth`` → ``app.services``)."""
    if not module_qname or "." not in module_qname:
        return ""
    return module_qname.rsplit(".", 1)[0]


def resolve_relative_module(
    current_module: str,
    *,
    level: int,
    module: str | None,
) -> str:
    """Resolve a relative ``from`` import target to an absolute dotted module."""
    if level <= 0:
        return module or ""

    package = package_of_module(current_module)
    package_parts = package.split(".") if package else []
    up = level - 1
    if up > len(package_parts):
        base_parts: list[str] = []
    else:
        base_parts = package_parts[: len(package_parts) - up] if up else list(package_parts)

    if module:
        return ".".join([*base_parts, *module.split(".")]) if base_parts else module
    return ".".join(base_parts)


def is_local_module(resolved: str, known_modules: frozenset[str]) -> bool:
    """True when ``resolved`` refers to a module/package present in the repo index."""
    if not resolved:
        return False
    if resolved in known_modules:
        return True
    prefix = resolved + "."
    if any(m.startswith(prefix) for m in known_modules):
        return True
    if any(resolved.startswith(m + ".") for m in known_modules):
        return True
    return False


def is_stdlib_module(resolved: str) -> bool:
    if not resolved:
        return False
    top = resolved.split(".", 1)[0]
    return top in _STDLIB_TOP


def classify_locality(resolved: str, known_modules: frozenset[str]) -> bool:
    """Local if in-repo; otherwise external (stdlib or third-party)."""
    return is_local_module(resolved, known_modules)


def resolve_import_statement(
    *,
    current_module: str,
    imported_name: str,
    binding_name: str,
    alias: str | None,
    module: str | None,
    level: int,
    known_modules: frozenset[str],
    is_from_import: bool,
) -> ResolvedImport:
    """Resolve one alias from ``import`` / ``from … import``."""
    if not is_from_import:
        resolved = imported_name
        style = "absolute"
        level = 0
    elif level > 0:
        base = resolve_relative_module(current_module, level=level, module=module)
        if imported_name == "*":
            resolved = base
        else:
            resolved = f"{base}.{imported_name}" if base else imported_name
        style = "relative"
    else:
        style = "absolute"
        if module:
            resolved = f"{module}.{imported_name}" if imported_name != "*" else module
        else:
            resolved = imported_name

    return ResolvedImport(
        binding_name=binding_name,
        imported_name=imported_name,
        resolved_module=resolved,
        style=style,
        is_local=classify_locality(resolved, known_modules),
        alias=alias,
        level=level,
    )
