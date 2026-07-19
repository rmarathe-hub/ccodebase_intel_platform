"""Week 5 Day 5 — JS/TS call extraction and resolution tests."""

from __future__ import annotations

from app.services.js_ts_calls import SymbolRef, extract_js_ts_calls, module_from_qname
from app.services.js_ts_parser import module_qualified_name, parse_js_ts_source


def _refs_from_parse(
    source: str,
    path: str,
    *,
    known_modules: frozenset[str] | None = None,
) -> list[SymbolRef]:
    result = parse_js_ts_source(
        source, relative_path=path, known_modules=known_modules or frozenset()
    )
    assert result.ok
    module = module_qualified_name(path)
    return [
        SymbolRef(
            kind=s.kind,
            name=s.name,
            qualified_name=s.qualified_name,
            module=module_from_qname(s.qualified_name, s.kind, s.name) or module,
            resolved_module=s.resolved_module,
        )
        for s in result.symbols
    ]


def test_extract_resolved_same_module_call() -> None:
    source = """
function helper(x) {
  return x;
}
function main() {
  return helper(1);
}
"""
    path = "app/demo.ts"
    refs = _refs_from_parse(source, path)
    calls = extract_js_ts_calls(source, relative_path=path, symbols=refs)
    assert len(calls) == 1
    call = calls[0]
    assert call.caller_qualified_name == "app.demo.main"
    assert call.raw_callee == "helper"
    assert call.candidate_qualified_name == "app.demo.helper"
    assert call.confidence == "resolved"


def test_extract_this_method_call() -> None:
    source = """
class Greeter {
  hello() {
    return 1;
  }
  run() {
    return this.hello();
  }
}
"""
    path = "app/svc.ts"
    refs = _refs_from_parse(source, path)
    calls = extract_js_ts_calls(source, relative_path=path, symbols=refs)
    this_calls = [c for c in calls if c.raw_callee.startswith("this.")]
    assert this_calls
    assert this_calls[0].confidence == "resolved"
    assert this_calls[0].candidate_qualified_name == "app.svc.Greeter.hello"


def test_extract_unresolved_external() -> None:
    source = """
function main() {
  return unknownThing(1);
}
"""
    path = "app/x.ts"
    refs = _refs_from_parse(source, path)
    calls = extract_js_ts_calls(source, relative_path=path, symbols=refs)
    assert calls[0].confidence == "unresolved"
    assert calls[0].candidate_qualified_name is None


def test_extract_await_and_arrow_caller() -> None:
    source = """
async function fetch() {
  return 1;
}
const load = async () => {
  return await fetch();
};
"""
    path = "app/async_mod.ts"
    refs = _refs_from_parse(source, path)
    calls = extract_js_ts_calls(source, relative_path=path, symbols=refs)
    assert len(calls) == 1
    assert calls[0].caller_qualified_name == "app.async_mod.load"
    assert calls[0].raw_callee == "fetch"
    assert calls[0].confidence == "resolved"


def test_ambiguous_when_same_name_exists_in_two_modules() -> None:
    path = "app/caller.ts"
    source = """
function main() {
  return helper(1);
}
"""
    local = _refs_from_parse(source, path)
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
    calls = extract_js_ts_calls(source, relative_path=path, symbols=symbols)
    assert len(calls) == 1
    assert calls[0].confidence == "ambiguous"
    assert calls[0].candidate_qualified_name is None


def test_resolved_prefers_same_module_over_foreign_duplicates() -> None:
    path = "app/local.ts"
    source = """
function helper() {
  return 1;
}
function main() {
  return helper();
}
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
    calls = extract_js_ts_calls(source, relative_path=path, symbols=symbols)
    assert calls[0].confidence == "resolved"
    assert calls[0].candidate_qualified_name == "app.local.helper"


def test_import_alias_resolves_named_import() -> None:
    helpers = """
export function util(n) { return n; }
"""
    service = """
import { util } from "./helpers";
function main() {
  return util(1);
}
"""
    known = frozenset({"pkg.helpers", "pkg.service"})
    refs = _refs_from_parse(helpers, "pkg/helpers.ts", known_modules=known)
    refs += _refs_from_parse(service, "pkg/service.ts", known_modules=known)
    calls = extract_js_ts_calls(service, relative_path="pkg/service.ts", symbols=refs)
    assert calls[0].raw_callee == "util"
    assert calls[0].candidate_qualified_name == "pkg.helpers.util"
    assert calls[0].confidence == "resolved"


def test_object_method_call_on_imported_default() -> None:
    greeter = """
export default class Greeter {
  hello() { return "hi"; }
}
"""
    service = """
import Greeter from "./greeter";
function main() {
  return Greeter.hello();
}
"""
    known = frozenset({"pkg.greeter", "pkg.service"})
    refs = _refs_from_parse(greeter, "pkg/greeter.ts", known_modules=known)
    refs += _refs_from_parse(service, "pkg/service.ts", known_modules=known)
    calls = extract_js_ts_calls(service, relative_path="pkg/service.ts", symbols=refs)
    assert calls[0].raw_callee == "Greeter.hello"
    assert calls[0].candidate_qualified_name == "pkg.greeter.Greeter.hello"
    assert calls[0].confidence == "resolved"


def test_nested_calls_preserve_caller() -> None:
    source = """
function inner(x) { return x; }
function outer(x) { return inner(inner(x)); }
"""
    path = "app/chain.ts"
    refs = _refs_from_parse(source, path)
    calls = extract_js_ts_calls(source, relative_path=path, symbols=refs)
    assert len(calls) >= 2
    assert all(c.caller_qualified_name == "app.chain.outer" for c in calls)
    assert all(c.confidence == "resolved" for c in calls)
