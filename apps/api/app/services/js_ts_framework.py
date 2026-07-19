"""Common-pattern framework metadata for JS/TS symbols (Week 5 Day 4).

Honesty: heuristic decorator / call / path matching only — not full framework support.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_HTTP = ("get", "post", "put", "patch", "delete", "options", "head", "all", "use")

_EXPRESS_ROUTE_RE = re.compile(
    r"""(?P<target>\w+)\.(?P<method>get|post|put|patch|delete|options|head|all|use)\s*\(\s*(?P<path>['\"][^'\"]*['\"])?""",
    re.IGNORECASE,
)

_NEST_CONTROLLER = re.compile(r"^Controller(?:\s*\(|$)", re.IGNORECASE)
_NEST_INJECTABLE = re.compile(r"^Injectable(?:\s*\(|$)", re.IGNORECASE)
_NEST_ROUTE = re.compile(
    r"^(Get|Post|Put|Patch|Delete|Options|Head|All)(?:\s*\(|$)",
    re.IGNORECASE,
)


@dataclass(frozen=True, slots=True)
class FrameworkMeta:
    role: str
    detail: str | None = None


def _decorator_leaf(deco: str) -> str:
    text = deco.strip().lstrip("@")
    # Controller('users') → Controller
    name = re.split(r"[\s(]", text, maxsplit=1)[0]
    return name


def detect_js_ts_framework_meta(
    *,
    kind: str,
    name: str,
    decorators: tuple[str, ...],
    relative_path: str,
    has_jsx: bool = False,
    export_names: frozenset[str] | None = None,
) -> FrameworkMeta | None:
    """Return a single best-effort framework role for a JS/TS symbol."""
    export_names = export_names or frozenset()

    # NestJS class / method decorators (highest signal).
    if kind == "class":
        for deco in decorators:
            leaf = _decorator_leaf(deco)
            if _NEST_CONTROLLER.match(leaf) or leaf == "Controller":
                return FrameworkMeta(role="nestjs_controller", detail=deco)
            if _NEST_INJECTABLE.match(leaf) or leaf == "Injectable":
                return FrameworkMeta(role="nestjs_service", detail=deco)
    if kind in {"method", "function"}:
        for deco in decorators:
            leaf = _decorator_leaf(deco)
            if _NEST_ROUTE.match(leaf):
                return FrameworkMeta(role="nestjs_route", detail=deco)

    # Express-style decorator strings rarely appear; call-site strings may be
    # passed as synthetic decorators from the parser second pass.
    for deco in decorators:
        match = _EXPRESS_ROUTE_RE.search(deco)
        if match:
            method = match.group("method").upper()
            path = match.group("path")
            detail = f"{method} {path.strip(chr(39) + chr(34))}" if path else method
            return FrameworkMeta(role="express_route", detail=detail)

    # Next.js App Router HTTP handlers.
    if kind == "function" and name.upper() in {m.upper() for m in _HTTP}:
        path = relative_path.replace("\\", "/")
        if "/route." in path or path.startswith("pages/api/") or "/api/" in path:
            return FrameworkMeta(role="nextjs_route", detail=f"{name.upper()} {path}")

    # React component (PascalCase + JSX), unless already Nest/Express.
    if kind in {"function", "class"} and name and name[0].isupper() and has_jsx:
        return FrameworkMeta(role="react_component", detail=name)

    # Default export page components under pages/ or app/**/page.
    if kind in {"function", "class"} and name in export_names:
        path = relative_path.replace("\\", "/")
        if path.endswith("/page.tsx") or path.endswith("/page.jsx") or path.endswith(
            "/page.ts"
        ):
            return FrameworkMeta(role="nextjs_page", detail=path)
        if path.startswith("pages/") and not path.startswith("pages/api/"):
            if name[0].isupper():
                return FrameworkMeta(role="nextjs_page", detail=path)

    return None


def express_route_from_call(callee_text: str, path_literal: str | None) -> FrameworkMeta | None:
    """Build express_route meta from ``app.get('/x', ...)`` call text."""
    match = _EXPRESS_ROUTE_RE.search(callee_text)
    if not match:
        # callee_text may already be "app.get"
        parts = callee_text.split(".")
        if len(parts) == 2 and parts[1].lower() in _HTTP:
            method = parts[1].upper()
            detail = f"{method} {path_literal}" if path_literal else method
            return FrameworkMeta(role="express_route", detail=detail)
        return None
    method = match.group("method").upper()
    path = match.group("path") or (f"'{path_literal}'" if path_literal else None)
    detail = f"{method} {path.strip(chr(39) + chr(34))}" if path else method
    return FrameworkMeta(role="express_route", detail=detail)
