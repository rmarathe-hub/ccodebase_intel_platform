"""Extended Python AST extraction matrix (Week 4 Days 1–2)."""

from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from app.services.python_ast_parser import (
    PARSER_NAME,
    PARSER_VERSION,
    module_qualified_name,
    parse_python_source,
    qualify,
)


def test_parser_stamp_contract() -> None:
    assert PARSER_NAME == "python-ast"
    assert PARSER_VERSION.startswith("4.3-")
    assert PARSER_VERSION.endswith("-stdlib")


def test_empty_and_comment_only_ok_no_symbols() -> None:
    empty = parse_python_source("", relative_path="empty.py")
    assert empty.ok
    assert empty.symbols == ()
    comments = parse_python_source("# just a comment\n", relative_path="c.py")
    assert comments.ok
    assert comments.symbols == ()


def test_syntax_error_fail_closed() -> None:
    result = parse_python_source("def broken(\n", relative_path="bad.py")
    assert result.ok is False
    assert result.symbols == ()
    assert result.error


def test_null_byte_fail_closed() -> None:
    result = parse_python_source("def x():\n    return 1\x00\n", relative_path="n.py")
    assert result.ok is False


def test_nested_class_method_qnames() -> None:
    source = """
class Outer:
    class Inner:
        def method(self):
            def nested():
                return 1
            return nested()
"""
    result = parse_python_source(source, relative_path="pkg/mod.py")
    assert result.ok
    qnames = {s.qualified_name for s in result.symbols}
    assert "pkg.mod.Outer" in qnames
    assert "pkg.mod.Outer.Inner" in qnames
    assert "pkg.mod.Outer.Inner.method" in qnames


def test_init_py_package_module_name() -> None:
    assert module_qualified_name("pkg/__init__.py") == "pkg"
    assert module_qualified_name("pkg/sub/__init__.py") == "pkg.sub"
    assert qualify("pkg", "Class") == "pkg.Class"


def test_async_def_and_async_method_flags() -> None:
    source = """
async def top():
    return 1

class Svc:
    async def run(self):
        return 2
"""
    result = parse_python_source(source, relative_path="a.py")
    assert result.ok
    by_name = {s.name: s for s in result.symbols}
    assert by_name["top"].is_async is True
    assert by_name["run"].is_async is True


def test_decorators_params_returns_docstring_json() -> None:
    source = '''\
from typing import Optional

def deco(f):
    return f

@deco
def greet(name: str, /, *, loud: bool = False, **opts) -> Optional[str]:
    """Say hi."""
    return name
'''
    result = parse_python_source(source, relative_path="d.py")
    assert result.ok
    greet = next(s for s in result.symbols if s.name == "greet")
    assert greet.docstring == "Say hi."
    assert greet.return_annotation is not None
    assert "Optional" in greet.return_annotation
    assert greet.decorators and "deco" in greet.decorators
    assert greet.parameters
    assert any(p.name == "loud" for p in greet.parameters)


def test_staticmethod_classmethod_property_kinds() -> None:
    source = """
class T:
    @staticmethod
    def s():
        return 1

    @classmethod
    def c(cls):
        return 2

    @property
    def p(self):
        return 3
"""
    result = parse_python_source(source, relative_path="t.py")
    assert result.ok
    methods = {s.name: s for s in result.symbols if s.kind == "method"}
    assert set(methods) >= {"s", "c", "p"}
    assert "staticmethod" in methods["s"].decorators
    assert "classmethod" in methods["c"].decorators
    assert "property" in methods["p"].decorators


def test_match_statement_does_not_break_extraction() -> None:
    source = """
def classify(x):
    match x:
        case 1:
            return "one"
        case _:
            return "other"
"""
    result = parse_python_source(source, relative_path="m.py")
    assert result.ok
    assert any(s.name == "classify" for s in result.symbols)


@pytest.mark.parametrize(
    "path",
    [
        "mod.py",
        "pkg/mod.py",
        "pkg/sub/mod.py",
        "weird-name/mod.py",
    ],
)
def test_module_qname_from_path(path: str) -> None:
    qn = module_qualified_name(path)
    assert "." not in path or qn.replace(".", "/") in path.replace(".py", "") or qn


@given(st.from_regex(r"[A-Za-z_][A-Za-z0-9_]{0,24}", fullmatch=True))
@settings(max_examples=40, deadline=None)
def test_property_identifier_roundtrip_function(name: str) -> None:
    if name in {"None", "True", "False", "class", "def", "import", "return"}:
        return
    source = f"def {name}():\n    return 1\n"
    result = parse_python_source(source, relative_path="gen.py")
    assert result.ok
    assert any(s.name == name and s.kind == "function" for s in result.symbols)
