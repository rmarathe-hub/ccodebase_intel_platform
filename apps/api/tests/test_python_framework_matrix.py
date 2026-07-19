"""Framework-role honesty: positives, false-positive near-matches, precedence."""

from __future__ import annotations

import pytest

from app.services.python_ast_parser import parse_python_source
from app.services.python_framework import detect_framework_meta


@pytest.mark.parametrize(
    ("kind", "decorators", "bases", "expected"),
    [
        ("function", ('router.get("/x")',), (), "fastapi_route"),
        ("function", ('app.post("/y")',), (), "fastapi_route"),
        ("function", ('api_router.delete("/z")',), (), "fastapi_route"),
        ("function", ('bp.route("/h")',), (), "flask_route"),
        ("function", ("shared_task",), (), "celery_task"),
        ("function", ("celery.task",), (), "celery_task"),
        ("function", ("task",), (), "celery_task"),
        ("class", (), ("BaseModel",), "pydantic_model"),
        ("class", (), ("pydantic.BaseModel",), "pydantic_model"),
        ("class", (), ("DeclarativeBase",), "sqlalchemy_model"),
        ("class", (), ("sqlalchemy.orm.DeclarativeBase",), "sqlalchemy_model"),
        ("class", (), ("APIView",), "django_view"),
        ("class", (), ("ModelViewSet",), "django_view"),
        ("function", ("rest_framework.decorators.api_view",), (), "django_view"),
    ],
)
def test_framework_positive_matrix(
    kind: str,
    decorators: tuple[str, ...],
    bases: tuple[str, ...],
    expected: str,
) -> None:
    meta = detect_framework_meta(kind=kind, decorators=decorators, bases=bases)
    assert meta is not None
    assert meta.role == expected


@pytest.mark.parametrize(
    ("kind", "decorators", "bases"),
    [
        ("function", (), ()),
        ("function", ("cache",), ()),
        ("function", ("property",), ()),
        ("function", ("staticmethod",), ()),
        ("function", ("classmethod",), ()),
        ("function", ("get",), ()),  # bare HTTP verb without app/router
        ("function", ("post",), ()),
        ("function", ("my_task_helper",), ()),
        ("class", (), ()),
        ("class", (), ("object",)),
        ("class", (), ("Exception",)),
        ("class", (), ("dict",)),
        ("class", (), ("TypedDict",)),
        ("class", (), ("Protocol",)),
        ("class", (), ("Enum",)),
        ("class", ("dataclass",), ()),
    ],
)
def test_framework_no_role_when_evidence_weak(
    kind: str,
    decorators: tuple[str, ...],
    bases: tuple[str, ...],
) -> None:
    assert detect_framework_meta(kind=kind, decorators=decorators, bases=bases) is None


def test_bare_base_heuristic_documents_current_behavior() -> None:
    """Classic SQLAlchemy uses `class User(Base)` — leaf Base alone triggers role.

    Decision-needed: whether bare `Base` / `Model` without sqlalchemy path should
    remain labeled (current) or require stronger evidence.
    """
    meta = detect_framework_meta(kind="class", decorators=(), bases=("Base",))
    assert meta is not None
    assert meta.role == "sqlalchemy_model"


def test_django_model_base_prefers_django_over_sqlalchemy() -> None:
    meta = detect_framework_meta(
        kind="class",
        decorators=(),
        bases=("django.db.models.Model",),
    )
    assert meta is not None
    assert meta.role == "django_view"


def test_fastapi_detail_includes_method_and_path() -> None:
    meta = detect_framework_meta(
        kind="function",
        decorators=('router.patch("/items/{id}")',),
    )
    assert meta is not None
    assert meta.role == "fastapi_route"
    assert meta.detail is not None
    assert "PATCH" in meta.detail
    assert "/items/{id}" in meta.detail


def test_parse_does_not_label_ordinary_helpers() -> None:
    source = '''\
def get(x):
    return x

class Cache:
    pass

def task_runner():
    return 1
'''
    result = parse_python_source(source, relative_path="app/plain.py")
    assert result.ok
    for sym in result.symbols:
        assert sym.framework_role is None
