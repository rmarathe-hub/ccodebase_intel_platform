"""Unit tests for the Python AST deep parser."""

from __future__ import annotations

from app.services.python_ast_parser import PARSER_NAME, parse_python_source


def test_parser_extracts_class_function_method_import() -> None:
    source = '''\
import os
from pathlib import Path

class Greeter:
    def hello(self, name: str) -> str:
        return f"hi {name}"

async def fetch():
    return 1

def top_level(x):
    return x
'''
    result = parse_python_source(source, relative_path="pkg/mod.py")
    assert result.ok is True
    assert PARSER_NAME == "python-ast"
    kinds = {s.kind for s in result.symbols}
    assert kinds == {"import", "class", "method", "function"}
    by_q = {s.qualified_name: s for s in result.symbols}
    assert "pkg.mod.Greeter" in by_q
    assert by_q["pkg.mod.Greeter"].kind == "class"
    assert by_q["pkg.mod.Greeter.hello"].kind == "method"
    assert "self, name" in (by_q["pkg.mod.Greeter.hello"].signature or "")
    assert by_q["pkg.mod.top_level"].kind == "function"
    assert by_q["pkg.mod.fetch"].kind == "function"
    assert by_q["os"].kind == "import"
    assert by_q["pathlib.Path"].kind == "import"


def test_syntax_error_is_not_ok() -> None:
    result = parse_python_source("def broken(:\n", relative_path="bad.py")
    assert result.ok is False
    assert result.symbols == ()
    assert result.error is not None


def test_empty_module() -> None:
    result = parse_python_source("", relative_path="empty.py")
    assert result.ok is True
    assert result.symbols == ()
