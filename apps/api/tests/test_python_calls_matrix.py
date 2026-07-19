"""Week 4 call-resolution matrix: resolved / ambiguous / unresolved honesty."""

from __future__ import annotations

import pytest

from app.services.python_ast_parser import module_qualified_name, parse_python_source
from app.services.python_calls import SymbolRef, extract_calls, module_from_qname


def _refs_from_parse(source: str, path: str) -> list[SymbolRef]:
    result = parse_python_source(source, relative_path=path)
    assert result.ok
    module = module_qualified_name(path)
    return [
        SymbolRef(
            kind=s.kind,
            name=s.name,
            qualified_name=s.qualified_name,
            module=module_from_qname(s.qualified_name, s.kind, s.name) or module,
        )
        for s in result.symbols
    ]


def test_ambiguous_when_same_name_exists_in_two_modules() -> None:
    """Bare name with two cross-module function candidates must be ambiguous."""
    path = "app/caller.py"
    source = """
def main():
    return helper(1)
"""
    local = _refs_from_parse(source, path)
    # Inject two foreign helpers that share the leaf name.
    symbols = local + [
        SymbolRef(
            kind="function",
            name="helper",
            qualified_name="pkg.a.helper",
            module="pkg.a",
        ),
        SymbolRef(
            kind="function",
            name="helper",
            qualified_name="pkg.b.helper",
            module="pkg.b",
        ),
    ]
    calls = extract_calls(source, relative_path=path, symbols=symbols)
    assert len(calls) == 1
    assert calls[0].raw_callee == "helper"
    assert calls[0].confidence == "ambiguous"
    assert calls[0].candidate_qualified_name is None


def test_resolved_prefers_same_module_over_foreign_duplicates() -> None:
    path = "app/local.py"
    source = """
def helper():
    return 1

def main():
    return helper()
"""
    local = _refs_from_parse(source, path)
    symbols = local + [
        SymbolRef(
            kind="function",
            name="helper",
            qualified_name="other.helper",
            module="other",
        ),
    ]
    calls = extract_calls(source, relative_path=path, symbols=symbols)
    assert calls[0].confidence == "resolved"
    assert calls[0].candidate_qualified_name == "app.local.helper"


def test_chained_and_nested_calls_preserve_caller() -> None:
    path = "app/chain.py"
    source = """
def inner(x):
    return x

def outer(x):
    return inner(inner(x))
"""
    refs = _refs_from_parse(source, path)
    calls = extract_calls(source, relative_path=path, symbols=refs)
    assert len(calls) >= 2
    assert all(c.caller_qualified_name == "app.chain.outer" for c in calls)
    assert all(c.confidence == "resolved" for c in calls)


def test_awaited_call_extracts_with_caller() -> None:
    path = "app/async_mod.py"
    source = """
async def fetch():
    return 1

async def run():
    return await fetch()
"""
    refs = _refs_from_parse(source, path)
    calls = extract_calls(source, relative_path=path, symbols=refs)
    assert any(c.raw_callee == "fetch" and c.confidence == "resolved" for c in calls)


def test_self_and_cls_method_calls() -> None:
    path = "app/klass.py"
    source = """
class Box:
    @classmethod
    def make(cls):
        return cls()

    def touch(self):
        return self.make()
"""
    refs = _refs_from_parse(source, path)
    calls = extract_calls(source, relative_path=path, symbols=refs)
    self_calls = [c for c in calls if c.raw_callee.startswith("self.")]
    assert self_calls
    assert self_calls[0].confidence == "resolved"


def test_recursive_call_resolved() -> None:
    path = "app/rec.py"
    source = """
def walk(n):
    if n <= 0:
        return 0
    return walk(n - 1)
"""
    refs = _refs_from_parse(source, path)
    calls = extract_calls(source, relative_path=path, symbols=refs)
    assert calls[0].confidence == "resolved"
    assert calls[0].candidate_qualified_name == "app.rec.walk"


def test_constructor_call_class_resolved() -> None:
    path = "app/ctor.py"
    source = """
class Thing:
    pass

def build():
    return Thing()
"""
    refs = _refs_from_parse(source, path)
    calls = extract_calls(source, relative_path=path, symbols=refs)
    assert calls[0].raw_callee == "Thing"
    assert calls[0].confidence == "resolved"
    assert calls[0].candidate_qualified_name == "app.ctor.Thing"


@pytest.mark.parametrize(
    ("source", "path", "expected_conf"),
    [
        ("def main():\n    return len([1])\n", "app/builtin.py", "unresolved"),
        ("def main():\n    return print(1)\n", "app/printy.py", "unresolved"),
        (
            "def main():\n    return getattr(object, 'x')\n",
            "app/dyn.py",
            "unresolved",
        ),
    ],
)
def test_stdlib_like_calls_are_unresolved(
    source: str, path: str, expected_conf: str
) -> None:
    refs = _refs_from_parse(source, path)
    calls = extract_calls(source, relative_path=path, symbols=refs)
    assert calls
    assert calls[0].confidence == expected_conf


def test_attribute_call_without_self_unresolved_or_safe() -> None:
    path = "app/attr.py"
    source = """
def main(obj):
    return obj.do_work()
"""
    refs = _refs_from_parse(source, path)
    calls = extract_calls(source, relative_path=path, symbols=refs)
    assert calls
    # Dynamic receiver — must not falsely claim resolved to a local symbol.
    assert calls[0].confidence in {"unresolved", "ambiguous"}
    assert calls[0].confidence != "resolved" or calls[0].candidate_qualified_name is None


def test_comprehension_and_default_calls() -> None:
    path = "app/comp.py"
    source = """
def seed():
    return 1

def build(xs=None):
    xs = xs or [seed()]
    return [seed() for _ in xs]
"""
    refs = _refs_from_parse(source, path)
    calls = extract_calls(source, relative_path=path, symbols=refs)
    assert len(calls) >= 2
    assert all(c.confidence == "resolved" for c in calls if c.raw_callee == "seed")


def test_deterministic_ordering_across_runs() -> None:
    path = "app/order.py"
    source = """
def a():
    return 1
def b():
    return 2
def main():
    a()
    b()
    a()
"""
    refs = _refs_from_parse(source, path)
    first = extract_calls(source, relative_path=path, symbols=refs)
    second = extract_calls(source, relative_path=path, symbols=refs)
    assert [(c.line, c.raw_callee, c.confidence) for c in first] == [
        (c.line, c.raw_callee, c.confidence) for c in second
    ]
