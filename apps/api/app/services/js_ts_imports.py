"""JavaScript / TypeScript module resolution (Week 5 Day 3).

Honesty: path-alias + relative resolution against discovered modules only.
No Node module resolution, no package.json exports map, no runtime.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

_EXT_SUFFIXES = (".tsx", ".ts", ".jsx", ".js", ".mjs", ".cjs")


@dataclass(frozen=True, slots=True)
class PathAlias:
    """One tsconfig-style alias: pattern ``@/*`` → target ``src/*``."""

    pattern: str
    target: str


@dataclass(frozen=True, slots=True)
class ResolvedJsTsImport:
    resolved_module: str
    style: str  # relative | absolute | alias
    is_local: bool


def strip_extension(path: str) -> str:
    cleaned = path.replace("\\", "/").strip().lstrip("/")
    for ext in _EXT_SUFFIXES:
        if cleaned.endswith(ext):
            return cleaned[: -len(ext)]
    return cleaned


def path_to_module(relative_path: str) -> str:
    """Repo-relative path → dotted module (index segments dropped)."""
    cleaned = strip_extension(relative_path)
    parts = [p for p in cleaned.split("/") if p and p != "."]
    if parts and parts[-1] == "index":
        parts = parts[:-1]
    return ".".join(parts)


def module_to_path_candidates(module: str) -> tuple[str, ...]:
    """Dotted module → plausible repo-relative stems (no extension)."""
    if not module:
        return ()
    base = module.replace(".", "/")
    return (base, f"{base}/index")


def load_tsconfig_paths(repo_root: Path) -> tuple[PathAlias, ...]:
    """Best-effort read of ``compilerOptions.paths`` from tsconfig*.json."""
    aliases: list[PathAlias] = []
    for name in ("tsconfig.json", "tsconfig.app.json", "tsconfig.base.json"):
        path = repo_root / name
        if not path.is_file():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            continue
        compiler = data.get("compilerOptions") if isinstance(data, dict) else None
        if not isinstance(compiler, dict):
            continue
        paths = compiler.get("paths")
        if not isinstance(paths, dict):
            continue
        for pattern, targets in paths.items():
            if not isinstance(pattern, str):
                continue
            if isinstance(targets, list) and targets:
                target = targets[0]
            elif isinstance(targets, str):
                target = targets
            else:
                continue
            if isinstance(target, str) and target:
                aliases.append(PathAlias(pattern=pattern, target=target.replace("\\", "/")))
    # Longer patterns first for greedy match.
    aliases.sort(key=lambda a: len(a.pattern), reverse=True)
    return tuple(aliases)


def apply_path_alias(specifier: str, aliases: tuple[PathAlias, ...]) -> str | None:
    """Map ``@/components/Button`` through tsconfig paths → ``src/components/Button``."""
    spec = specifier.strip()
    for alias in aliases:
        pattern = alias.pattern
        target = alias.target
        if "*" in pattern:
            prefix, _, suffix = pattern.partition("*")
            if not spec.startswith(prefix):
                continue
            rest = spec[len(prefix) :]
            if suffix and not rest.endswith(suffix):
                continue
            if suffix:
                rest = rest[: -len(suffix)]
            t_prefix, _, t_suffix = target.partition("*")
            mapped = f"{t_prefix}{rest}{t_suffix}"
            return mapped.lstrip("./")
        if spec == pattern:
            return target.lstrip("./")
    return None


def _normalize_rel(current_dir: str, specifier: str) -> str:
    """Resolve ``./`` / ``../`` against the importing file directory."""
    parts = [p for p in current_dir.split("/") if p] if current_dir else []
    for segment in specifier.replace("\\", "/").split("/"):
        if segment in ("", "."):
            continue
        if segment == "..":
            if parts:
                parts.pop()
            continue
        parts.append(segment)
    return "/".join(parts)


def resolve_candidates_against_known(
    stem: str,
    known_modules: frozenset[str],
) -> str | None:
    """Pick the best known module for a path stem (with optional /index)."""
    module = path_to_module(stem)
    candidates = [
        module,
        f"{module}.index" if module else "index",
        *module_to_path_candidates(module),
    ]
    # Also try path_to_module on stem/index explicitly.
    index_mod = path_to_module(f"{stem}/index")
    candidates.append(index_mod)

    seen: set[str] = set()
    ordered: list[str] = []
    for c in candidates:
        if not c or c in seen:
            continue
        seen.add(c)
        ordered.append(c)

    for c in ordered:
        if c in known_modules:
            return c
    # Prefix package match: importing ``src/utils`` when only ``src.utils.helpers`` exists.
    for c in ordered:
        prefix = c + "."
        if any(m.startswith(prefix) for m in known_modules):
            return c
    return ordered[0] if ordered else None


def resolve_import_specifier(
    specifier: str,
    *,
    current_path: str,
    known_modules: frozenset[str],
    path_aliases: tuple[PathAlias, ...] = (),
) -> ResolvedJsTsImport:
    """Resolve an import/export-from specifier to a module-like name."""
    raw = specifier.strip().strip("'\"")
    if not raw:
        return ResolvedJsTsImport(resolved_module="", style="absolute", is_local=False)

    current = current_path.replace("\\", "/").lstrip("/")
    current_dir = "/".join(strip_extension(current).split("/")[:-1])

    if raw.startswith("."):
        stem = _normalize_rel(current_dir, raw)
        resolved = resolve_candidates_against_known(stem, known_modules) or path_to_module(stem)
        is_local = resolved in known_modules or any(
            m.startswith(resolved + ".") for m in known_modules
        )
        return ResolvedJsTsImport(
            resolved_module=resolved,
            style="relative",
            is_local=is_local or raw.startswith("."),
        )

    aliased = apply_path_alias(raw, path_aliases)
    if aliased is not None:
        resolved = resolve_candidates_against_known(aliased, known_modules) or path_to_module(
            aliased
        )
        is_local = resolved in known_modules or any(
            m.startswith(resolved + ".") for m in known_modules
        )
        return ResolvedJsTsImport(
            resolved_module=resolved,
            style="alias",
            is_local=is_local,
        )

    # Bare package / absolute path-like without alias.
    if "/" in raw and not raw.startswith("@"):
        # Treat as path-like absolute from repo root (rare).
        resolved = resolve_candidates_against_known(raw, known_modules) or path_to_module(raw)
        is_local = resolved in known_modules
        return ResolvedJsTsImport(
            resolved_module=resolved if is_local else raw,
            style="absolute",
            is_local=is_local,
        )

    # Scoped or package import (react, @nestjs/common) — external unless known.
    top = raw.split("/", 1)[0]
    is_local = raw in known_modules or any(
        m == raw or m.startswith(raw + ".") for m in known_modules
    )
    return ResolvedJsTsImport(
        resolved_module=raw if not is_local else (raw if raw in known_modules else top),
        style="absolute",
        is_local=is_local,
    )


_NEXT_APP_ROUTE = re.compile(r"(^|/)app/.+/route\.(t|j)sx?$")
_NEXT_APP_PAGE = re.compile(r"(^|/)app/.+/page\.(t|j)sx?$")
_NEXT_PAGES_API = re.compile(r"(^|/)pages/api/.+\.(t|j)sx?$")
_NEXT_PAGES_PAGE = re.compile(r"(^|/)pages/.+\.(t|j)sx?$")


def nextjs_path_role(relative_path: str) -> tuple[str, str] | None:
    """Path-based Next.js role hint: (role, detail) or None."""
    path = relative_path.replace("\\", "/")
    if _NEXT_APP_ROUTE.search(path) or _NEXT_PAGES_API.search(path):
        return "nextjs_route", path
    if _NEXT_APP_PAGE.search(path):
        return "nextjs_page", path
    if path.startswith("pages/") and not path.startswith("pages/api/"):
        if _NEXT_PAGES_PAGE.search(path):
            return "nextjs_page", path
    return None
