"""Unit tests for Week 4 Days 1–2 Python AST depth and qualified names."""

from __future__ import annotations

from app.services.python_ast_parser import (
    module_qualified_name,
    parse_python_source,
    qualify,
)


def test_module_qualified_name_rules() -> None:
    assert module_qualified_name("app/services/auth.py") == "app.services.auth"
    assert module_qualified_name("app/services/__init__.py") == "app.services"
    assert module_qualified_name("scripts/load_to_postgres.py") == "scripts.load_to_postgres"
    assert module_qualified_name("__init__.py") == ""
    assert qualify("app.services.auth", "AuthService", "login") == (
        "app.services.auth.AuthService.login"
    )


def test_day1_extracts_decorators_params_returns_docstrings() -> None:
    source = '''\
"""module doc"""
from fastapi import APIRouter

router = APIRouter()

@dataclass
class AuthService:
    """Auth service."""

    @staticmethod
    def login(self, user_id: int, *, force: bool = False) -> str:
        """Log the user in."""
        return str(user_id)

async def fetch_user(uid: str) -> dict:
    """Fetch one user."""
    return {"id": uid}

@router.get("/users")
def list_users() -> list[str]:
    return []
'''
    result = parse_python_source(source, relative_path="app/services/auth.py")
    assert result.ok is True
    by_q = {s.qualified_name: s for s in result.symbols}

    assert "app.services.auth.AuthService" in by_q
    cls = by_q["app.services.auth.AuthService"]
    assert cls.docstring == "Auth service."
    assert "dataclass" in cls.decorators

    login = by_q["app.services.auth.AuthService.login"]
    assert login.kind == "method"
    assert login.docstring == "Log the user in."
    assert "staticmethod" in login.decorators
    assert login.return_annotation == "str"
    param_names = [p.name for p in login.parameters]
    assert param_names == ["self", "user_id", "force"]
    by_name = {p.name: p for p in login.parameters}
    assert by_name["user_id"].annotation == "int"
    assert by_name["force"].kind == "kwonly"
    assert "-> str" in (login.signature or "")

    fetch = by_q["app.services.auth.fetch_user"]
    assert fetch.kind == "function"
    assert fetch.is_async is True
    assert fetch.return_annotation == "dict"
    assert fetch.docstring == "Fetch one user."

    route = by_q["app.services.auth.list_users"]
    assert any("router.get" in d for d in route.decorators)
    assert route.return_annotation == "list[str]"


def test_day2_nested_class_qualified_names() -> None:
    source = """
class Outer:
    class Inner:
        def method(self) -> None:
            return None
"""
    result = parse_python_source(source, relative_path="app/api/users.py")
    assert result.ok
    names = {s.qualified_name for s in result.symbols}
    assert "app.api.users.Outer" in names
    assert "app.api.users.Outer.Inner" in names
    assert "app.api.users.Outer.Inner.method" in names


def test_init_module_qualified_names() -> None:
    source = "def create_user():\n    return 1\n"
    result = parse_python_source(source, relative_path="app/api/__init__.py")
    assert result.ok
    assert result.symbols[0].qualified_name == "app.api.create_user"


def test_syntax_error_still_fails_closed() -> None:
    result = parse_python_source("def broken(:\n", relative_path="bad.py")
    assert result.ok is False
    assert result.symbols == ()
