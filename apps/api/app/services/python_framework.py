"""Common-pattern framework metadata for Python symbols (Week 4 Day 3).

Honesty: heuristic decorator/base matching only — not complete framework support.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_HTTP_METHODS = ("get", "post", "put", "patch", "delete", "options", "head", "websocket")

# app.get("/x"), router.post('/y'), api_router.put(...)
_FASTAPI_ROUTE_RE = re.compile(
    r"""(?P<target>\w+)\.(?P<method>get|post|put|patch|delete|options|head|websocket)\s*\(\s*(?P<path>['\"][^'\"]*['\"])?""",
    re.IGNORECASE,
)
_FLASK_ROUTE_RE = re.compile(
    r"""(?P<target>\w+)\.route\s*\(\s*(?P<path>['\"][^'\"]*['\"])?""",
    re.IGNORECASE,
)
_CELERY_TASK_RE = re.compile(
    r"""(?:shared_task|(?:\w+\.)?task)\s*(?:\(|$)""",
    re.IGNORECASE,
)


@dataclass(frozen=True, slots=True)
class FrameworkMeta:
    role: str
    detail: str | None = None


def _base_leaf(base: str) -> str:
    return base.split(".")[-1].split("[")[0].strip()


def detect_framework_meta(
    *,
    kind: str,
    decorators: tuple[str, ...],
    bases: tuple[str, ...] = (),
) -> FrameworkMeta | None:
    """Return a single best-effort framework role for a class/function/method."""
    joined_deco = " | ".join(decorators)

    if kind in {"function", "method"}:
        for deco in decorators:
            match = _FASTAPI_ROUTE_RE.search(deco)
            if match:
                method = match.group("method").upper()
                path = match.group("path")
                detail = f"{method} {path.strip(chr(39) + chr(34))}" if path else method
                return FrameworkMeta(role="fastapi_route", detail=detail)

            match = _FLASK_ROUTE_RE.search(deco)
            if match:
                path = match.group("path")
                detail = path.strip("'\"") if path else "route"
                return FrameworkMeta(role="flask_route", detail=detail)

            if "api_view" in deco or deco.endswith("api_view") or "APIView" in deco:
                return FrameworkMeta(role="django_view", detail=deco)

            if _CELERY_TASK_RE.search(deco) or deco in {"shared_task", "task"}:
                return FrameworkMeta(role="celery_task", detail=deco)

            # Bare HTTP method decorators sometimes used in examples.
            leaf = deco.split("(")[0].split(".")[-1].lower()
            if leaf in _HTTP_METHODS and ("router" in deco.lower() or "app" in deco.lower()):
                return FrameworkMeta(role="fastapi_route", detail=deco)

        if "django" in joined_deco.lower() and "view" in joined_deco.lower():
            return FrameworkMeta(role="django_view", detail=joined_deco or None)

    if kind == "class":
        leaves = {_base_leaf(b) for b in bases}
        deco_join = " ".join(decorators).lower()

        if leaves & {"BaseModel", "BaseSettings", "BaseModelT"}:
            return FrameworkMeta(role="pydantic_model", detail=", ".join(bases) or None)
        if "pydantic" in deco_join or any("pydantic" in b.lower() for b in bases):
            return FrameworkMeta(role="pydantic_model", detail=", ".join(bases) or None)

        if leaves & {
            "Base",
            "DeclarativeBase",
            "Model",
            "MappedAsDataclass",
        } or any("sqlalchemy" in b.lower() for b in bases):
            # Avoid labeling Django Model as SQLAlchemy when name is just Model + django.db
            if any("django" in b.lower() for b in bases):
                return FrameworkMeta(role="django_view", detail=", ".join(bases))
            return FrameworkMeta(role="sqlalchemy_model", detail=", ".join(bases) or None)

        if leaves & {
            "View",
            "APIView",
            "ViewSet",
            "ModelViewSet",
            "GenericAPIView",
            "TemplateView",
        } or any("django" in b.lower() and "view" in b.lower() for b in bases):
            return FrameworkMeta(role="django_view", detail=", ".join(bases) or None)

        if any("celery" in d.lower() or d.endswith("Task") for d in decorators):
            return FrameworkMeta(role="celery_task", detail=", ".join(decorators) or None)

    return None
