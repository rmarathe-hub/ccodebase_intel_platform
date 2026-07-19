"""Week 5 Days 1–2: JS/TS tree-sitter parser interfaces and symbol extraction."""

from __future__ import annotations

import pytest

from app.services.js_ts_parser import (
    PARSER_VERSION,
    JavaScriptTreeSitterParser,
    JSXTreeSitterParser,
    TSXTreeSitterParser,
    TypeScriptTreeSitterParser,
    dialect_for_path,
    module_qualified_name,
    parse_js_ts_source,
    parser_for_path,
)


def test_parser_interfaces_and_stamps() -> None:
    assert isinstance(TypeScriptTreeSitterParser(), TypeScriptTreeSitterParser)
    assert TypeScriptTreeSitterParser.parser_name == "typescript-treesitter"
    assert TSXTreeSitterParser.parser_name == "tsx-treesitter"
    assert JavaScriptTreeSitterParser.parser_name == "javascript-treesitter"
    assert JSXTreeSitterParser.parser_name == "jsx-treesitter"
    assert PARSER_VERSION == "5.4-treesitter"


@pytest.mark.parametrize(
    ("path", "dialect", "parser_name"),
    [
        ("a.ts", "typescript", "typescript-treesitter"),
        ("a.tsx", "tsx", "tsx-treesitter"),
        ("a.js", "javascript", "javascript-treesitter"),
        ("a.jsx", "jsx", "jsx-treesitter"),
        ("a.mjs", "javascript", "javascript-treesitter"),
    ],
)
def test_dialect_and_parser_for_path(path: str, dialect: str, parser_name: str) -> None:
    assert dialect_for_path(path) == dialect
    assert parser_for_path(path).parser_name == parser_name


def test_module_qname_strips_index_and_extensions() -> None:
    assert module_qualified_name("src/components/Button.tsx") == "src.components.Button"
    assert module_qualified_name("src/components/index.ts") == "src.components"
    assert module_qualified_name("lib/math.js") == "lib.math"


def test_extract_typescript_symbols() -> None:
    source = """
import { foo as f } from "./foo";
export function greet(name: string): string {
  return name;
}
interface User { id: number }
type Id = string;
class Svc {
  async load(): Promise<number> { return 1; }
}
export { greet };
"""
    result = parse_js_ts_source(source, relative_path="app/demo.ts")
    assert result.ok
    assert result.parser_name == "typescript-treesitter"
    assert result.language == "typescript"
    by_kind = {}
    for s in result.symbols:
        by_kind.setdefault(s.kind, []).append(s)
    assert any(s.name == "f" for s in by_kind["import"])
    assert any(s.name == "greet" for s in by_kind["function"])
    assert any(s.name == "User" for s in by_kind["interface"])
    assert any(s.name == "Id" for s in by_kind["type_alias"])
    assert any(s.name == "Svc" for s in by_kind["class"])
    assert any(s.name == "load" and s.is_async for s in by_kind["method"])
    assert any(s.name == "greet" for s in by_kind["export"])
    load = next(s for s in result.symbols if s.name == "load")
    assert load.qualified_name == "app.demo.Svc.load"


def test_extract_react_components_from_tsx() -> None:
    source = """
export function Hello({ name }: { name: string }) {
  return <div>{name}</div>;
}
export const Box = () => <span />;
const helper = () => 1;
"""
    result = parse_js_ts_source(source, relative_path="ui/Hello.tsx")
    assert result.ok
    assert result.parser_name == "tsx-treesitter"
    by_name = {s.name: s for s in result.symbols if s.kind == "function"}
    assert by_name["Hello"].framework_role == "react_component"
    assert by_name["Box"].framework_role == "react_component"
    assert by_name["helper"].framework_role is None


def test_extract_javascript_arrow_and_class() -> None:
    source = """
function add(a, b) { return a + b; }
const mul = (a, b) => a * b;
class Calc { m() { return 1; } }
import React from "react";
"""
    result = parse_js_ts_source(source, relative_path="lib/math.js")
    assert result.ok
    assert result.parser_name == "javascript-treesitter"
    names = {(s.kind, s.name) for s in result.symbols}
    assert ("function", "add") in names
    assert ("function", "mul") in names
    assert ("class", "Calc") in names
    assert ("method", "m") in names
    assert ("import", "React") in names
    react = next(s for s in result.symbols if s.name == "React")
    assert react.is_local_import is False
    assert react.import_style == "absolute"


def test_jsx_parser_handles_jsx_file() -> None:
    source = """
export default function Widget() {
  return <section />;
}
"""
    result = parse_js_ts_source(source, relative_path="Widget.jsx")
    assert result.ok
    assert result.parser_name == "jsx-treesitter"
    assert result.language == "javascript"
    widget = next(s for s in result.symbols if s.name == "Widget")
    assert widget.framework_role == "react_component"


def test_syntax_error_fail_closed() -> None:
    result = parse_js_ts_source("function (", relative_path="broken.ts")
    assert result.ok is False
    assert result.symbols == ()
    assert result.error


def test_empty_file_ok() -> None:
    result = parse_js_ts_source("", relative_path="empty.js")
    assert result.ok
    assert result.symbols == ()
