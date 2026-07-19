"""Week 4 Days 3–4: framework metadata and import resolution tests."""

from __future__ import annotations

from app.services.python_ast_parser import parse_python_source
from app.services.python_framework import detect_framework_meta
from app.services.python_imports import (
    is_stdlib_module,
    resolve_import_statement,
    resolve_relative_module,
)


def test_framework_fastapi_flask_celery() -> None:
    assert detect_framework_meta(
        kind="function",
        decorators=('router.get("/users")',),
    ).role == "fastapi_route"
    assert detect_framework_meta(
        kind="function",
        decorators=('app.route("/health")',),
    ).role == "flask_route"
    assert detect_framework_meta(
        kind="function",
        decorators=("shared_task",),
    ).role == "celery_task"


def test_framework_models_and_django() -> None:
    assert detect_framework_meta(
        kind="class",
        decorators=(),
        bases=("BaseModel",),
    ).role == "pydantic_model"
    assert detect_framework_meta(
        kind="class",
        decorators=(),
        bases=("DeclarativeBase",),
    ).role == "sqlalchemy_model"
    assert detect_framework_meta(
        kind="class",
        decorators=(),
        bases=("APIView",),
    ).role == "django_view"


def test_parse_attaches_framework_roles() -> None:
    source = '''\
from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase

router = APIRouter()

class User(BaseModel):
    id: int

class Row(DeclarativeBase):
    pass

@router.post("/items")
def create_item():
    return {}

@shared_task
def ping():
    return 1
'''
    result = parse_python_source(source, relative_path="app/api/routes.py")
    assert result.ok
    by_name = {s.name: s for s in result.symbols}
    assert by_name["create_item"].framework_role == "fastapi_route"
    detail = by_name["create_item"].framework_detail
    assert detail and "POST" in detail
    assert by_name["User"].framework_role == "pydantic_model"
    assert by_name["Row"].framework_role == "sqlalchemy_model"
    assert by_name["ping"].framework_role == "celery_task"


def test_relative_module_resolution() -> None:
    assert (
        resolve_relative_module("app.services.auth", level=1, module="helpers")
        == "app.services.helpers"
    )
    assert (
        resolve_relative_module("app.services.auth", level=2, module="models")
        == "app.models"
    )


def test_import_local_vs_external() -> None:
    known = frozenset({"app.services.auth", "app.services.helpers", "app.models.user"})
    local = resolve_import_statement(
        current_module="app.services.auth",
        imported_name="helpers",
        binding_name="helpers",
        alias=None,
        module=None,
        level=1,
        known_modules=known,
        is_from_import=True,
    )
    assert local.style == "relative"
    assert local.resolved_module == "app.services.helpers"
    assert local.is_local is True

    abs_local = resolve_import_statement(
        current_module="app.api.routes",
        imported_name="auth",
        binding_name="auth",
        alias=None,
        module="app.services",
        level=0,
        known_modules=known,
        is_from_import=True,
    )
    assert abs_local.style == "absolute"
    assert abs_local.resolved_module == "app.services.auth"
    assert abs_local.is_local is True

    external = resolve_import_statement(
        current_module="app.services.auth",
        imported_name="os",
        binding_name="os",
        alias=None,
        module=None,
        level=0,
        known_modules=known,
        is_from_import=False,
    )
    assert external.is_local is False
    assert is_stdlib_module("os") is True

    aliased = resolve_import_statement(
        current_module="app.services.auth",
        imported_name="Path",
        binding_name="P",
        alias="P",
        module="pathlib",
        level=0,
        known_modules=known,
        is_from_import=True,
    )
    assert aliased.resolved_module == "pathlib.Path"
    assert aliased.is_local is False
    assert aliased.alias == "P"


def test_parse_resolves_imports_with_known_modules() -> None:
    source = '''\
import os
from pathlib import Path as P
from .helpers import util
from app.services import auth
'''
    known = frozenset({"app.api.routes", "app.api.helpers", "app.services.auth"})
    result = parse_python_source(
        source,
        relative_path="app/api/routes.py",
        known_modules=known,
    )
    assert result.ok
    imports = [s for s in result.symbols if s.kind == "import"]
    by_name = {s.name: s for s in imports}
    assert by_name["os"].is_local_import is False
    assert by_name["os"].import_style == "absolute"
    assert by_name["P"].import_alias == "P"
    assert by_name["P"].is_local_import is False
    assert by_name["util"].import_style == "relative"
    assert by_name["util"].resolved_module == "app.api.helpers.util"
    # helpers.util may not be a known module file; locality uses prefix rules.
    assert by_name["auth"].resolved_module == "app.services.auth"
    assert by_name["auth"].is_local_import is True
