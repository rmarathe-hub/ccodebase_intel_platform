"""Week 4 Day 5 — call extraction and resolution tests."""

from __future__ import annotations

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


def test_extract_resolved_same_module_call() -> None:
    source = """
def helper(x):
    return x

def main():
    return helper(1)
"""
    path = "app/demo.py"
    refs = _refs_from_parse(source, path)
    calls = extract_calls(source, relative_path=path, symbols=refs)
    assert len(calls) == 1
    call = calls[0]
    assert call.caller_qualified_name == "app.demo.main"
    assert call.raw_callee == "helper"
    assert call.candidate_qualified_name == "app.demo.helper"
    assert call.confidence == "resolved"


def test_extract_self_method_call() -> None:
    source = """
class Greeter:
    def hello(self):
        return 1

    def run(self):
        return self.hello()
"""
    path = "app/svc.py"
    refs = _refs_from_parse(source, path)
    calls = extract_calls(source, relative_path=path, symbols=refs)
    self_calls = [c for c in calls if c.raw_callee.startswith("self.")]
    assert self_calls
    assert self_calls[0].confidence == "resolved"
    assert self_calls[0].candidate_qualified_name == "app.svc.Greeter.hello"


def test_extract_unresolved_external() -> None:
    source = """
def main():
    return unknown_thing(1)
"""
    path = "app/x.py"
    refs = _refs_from_parse(source, path)
    calls = extract_calls(source, relative_path=path, symbols=refs)
    assert calls[0].confidence == "unresolved"
    assert calls[0].candidate_qualified_name is None


def test_extract_ambiguous_duplicate_names() -> None:
    source = """
def helper():
    return 1

class A:
    def helper(self):
        return 2

def main():
    return helper()
"""
    path = "app/amb.py"
    refs = _refs_from_parse(source, path)
    # Both function and method named helper exist in module; same-module function
    # should win as unique function.
    calls = extract_calls(source, relative_path=path, symbols=refs)
    assert calls[0].confidence == "resolved"
    assert calls[0].candidate_qualified_name == "app.amb.helper"
