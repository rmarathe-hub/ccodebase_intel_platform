"""Tree-sitter deep parsers for JavaScript / TypeScript (Week 5 Days 1–2).

Honesty:
- Structural extraction only — no code execution.
- Days 1–2: parser interfaces + symbol extraction.
- Module aliases, framework depth, and call graphs are later days.
- Parse failures leave ``parser_name`` unset (fail closed).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import tree_sitter_javascript as ts_javascript
import tree_sitter_typescript as ts_typescript
from tree_sitter import Language, Node, Parser

PARSER_VERSION = "5.2-treesitter"

# Node types shared across JS / TS grammars.
_FUNCTION_TYPES = frozenset(
    {
        "function_declaration",
        "generator_function_declaration",
        "function_expression",
    }
)
_CLASS_TYPES = frozenset({"class_declaration", "abstract_class_declaration"})
_METHOD_TYPES = frozenset({"method_definition"})
_INTERFACE_TYPES = frozenset({"interface_declaration"})
_TYPE_ALIAS_TYPES = frozenset({"type_alias_declaration"})
_IMPORT_TYPES = frozenset({"import_statement"})
_EXPORT_TYPES = frozenset({"export_statement"})
_LEXICAL_TYPES = frozenset({"lexical_declaration", "variable_declaration"})
_ARROW_TYPES = frozenset({"arrow_function", "function_expression"})
_JSX_TYPES = frozenset(
    {
        "jsx_element",
        "jsx_self_closing_element",
        "jsx_fragment",
    }
)


@dataclass(frozen=True, slots=True)
class ExtractedParameter:
    name: str
    annotation: str | None
    kind: str


@dataclass(frozen=True, slots=True)
class ExtractedSymbol:
    kind: str
    name: str
    qualified_name: str
    start_line: int
    end_line: int
    signature: str | None
    docstring: str | None = None
    decorators: tuple[str, ...] = ()
    parameters: tuple[ExtractedParameter, ...] = ()
    return_annotation: str | None = None
    is_async: bool = False
    framework_role: str | None = None
    framework_detail: str | None = None
    resolved_module: str | None = None
    import_style: str | None = None
    is_local_import: bool | None = None
    import_alias: str | None = None


@dataclass(frozen=True, slots=True)
class ParseResult:
    ok: bool
    symbols: tuple[ExtractedSymbol, ...]
    error: str | None = None
    parser_name: str | None = None
    language: str | None = None


class JsTsTreeSitterParser(Protocol):
    """Day 1 interface for JS/TS deep parsers."""

    parser_name: str
    language_name: str  # javascript | typescript

    def parse(self, source: str, *, relative_path: str) -> ParseResult: ...


def module_qualified_name(relative_path: str) -> str:
    """Map a repo-relative JS/TS path to a dotted module-like name."""
    cleaned = relative_path.replace("\\", "/").strip().lstrip("/")
    if not cleaned:
        return ""
    for ext in (".tsx", ".ts", ".jsx", ".js", ".mjs", ".cjs"):
        if cleaned.endswith(ext):
            cleaned = cleaned[: -len(ext)]
            break
    parts = [p for p in cleaned.split("/") if p and p != "."]
    if parts and parts[-1] == "index":
        parts = parts[:-1]
    return ".".join(parts)


def qualify(module: str, *parts: str) -> str:
    chunks = [module] if module else []
    chunks.extend(p for p in parts if p)
    return ".".join(chunks)


def dialect_for_path(relative_path: str) -> str:
    """Return one of: typescript | tsx | javascript | jsx."""
    lower = relative_path.replace("\\", "/").lower()
    if lower.endswith(".tsx"):
        return "tsx"
    if lower.endswith(".ts"):
        return "typescript"
    if lower.endswith(".jsx"):
        return "jsx"
    return "javascript"


def parser_for_path(relative_path: str) -> JsTsTreeSitterParser:
    dialect = dialect_for_path(relative_path)
    if dialect == "tsx":
        return TSXTreeSitterParser()
    if dialect == "typescript":
        return TypeScriptTreeSitterParser()
    if dialect == "jsx":
        return JSXTreeSitterParser()
    return JavaScriptTreeSitterParser()


def parse_js_ts_source(source: str, *, relative_path: str) -> ParseResult:
    """Convenience entry: pick dialect from path and parse."""
    return parser_for_path(relative_path).parse(source, relative_path=relative_path)


def _text(source: bytes, node: Node | None) -> str:
    if node is None:
        return ""
    return source[node.start_byte : node.end_byte].decode("utf-8", errors="replace")


def _line_span(node: Node) -> tuple[int, int]:
    # tree-sitter points are 0-based; product uses 1-based lines.
    return node.start_point[0] + 1, node.end_point[0] + 1


def _child_by_type(node: Node, type_name: str) -> Node | None:
    for child in node.children:
        if child.type == type_name:
            return child
    return None


def _children_by_type(node: Node, type_name: str) -> list[Node]:
    return [c for c in node.children if c.type == type_name]


def _name_node(node: Node) -> Node | None:
    for type_name in (
        "type_identifier",
        "identifier",
        "property_identifier",
    ):
        found = _child_by_type(node, type_name)
        if found is not None:
            return found
    return None


def _has_jsx(node: Node) -> bool:
    stack = [node]
    while stack:
        cur = stack.pop()
        if cur.type in _JSX_TYPES:
            return True
        stack.extend(cur.children)
    return False


def _is_async(node: Node) -> bool:
    return any(c.type == "async" for c in node.children)


def _extract_parameters(source: bytes, params_node: Node | None) -> tuple[ExtractedParameter, ...]:
    if params_node is None:
        return ()
    out: list[ExtractedParameter] = []
    for child in params_node.named_children:
        if child.type in {
            "required_parameter",
            "optional_parameter",
            "rest_parameter",
            "assignment_pattern",
        }:
            name_n = _name_node(child) or _child_by_type(child, "object_pattern")
            if name_n is None:
                # Destructured / complex — keep a placeholder.
                name = _text(source, child).split(":")[0].strip()[:80] or "param"
            else:
                name = _text(source, name_n)
            ann = _child_by_type(child, "type_annotation")
            kind = "vararg" if child.type == "rest_parameter" else "positional"
            out.append(
                ExtractedParameter(
                    name=name,
                    annotation=_text(source, ann).lstrip(": ").strip() if ann else None,
                    kind=kind,
                )
            )
        elif child.type == "identifier":
            out.append(
                ExtractedParameter(
                    name=_text(source, child),
                    annotation=None,
                    kind="positional",
                )
            )
    return tuple(out)


def _return_annotation(source: bytes, node: Node) -> str | None:
    ann = _child_by_type(node, "type_annotation")
    if ann is None:
        return None
    return _text(source, ann).lstrip(": ").strip() or None


def _react_role(name: str, body: Node | None) -> tuple[str | None, str | None]:
    """Day 2: mark PascalCase + JSX as react_component (heuristic)."""
    if not name or not name[0].isupper():
        return None, None
    if body is not None and _has_jsx(body):
        return "react_component", name
    return None, None


class _BaseTreeSitterParser:
    parser_name: str
    language_name: str
    _language: Language

    def __init__(self) -> None:
        self._parser = Parser(self._language)

    def parse(self, source: str, *, relative_path: str) -> ParseResult:
        try:
            raw = source.encode("utf-8")
        except UnicodeEncodeError as exc:
            return ParseResult(ok=False, symbols=(), error=str(exc))

        try:
            tree = self._parser.parse(raw)
        except Exception as exc:  # noqa: BLE001 — fail closed
            return ParseResult(ok=False, symbols=(), error=str(exc))

        if tree.root_node.has_error:
            # Still attempt extraction from partial trees, but mark not-ok if
            # the root reports error — honesty: fail closed for stamp.
            return ParseResult(
                ok=False,
                symbols=(),
                error="syntax_error",
                parser_name=self.parser_name,
                language=self.language_name,
            )

        module = module_qualified_name(relative_path)
        symbols = self._extract(raw, tree.root_node, module)
        return ParseResult(
            ok=True,
            symbols=tuple(symbols),
            parser_name=self.parser_name,
            language=self.language_name,
        )

    def _extract(self, source: bytes, root: Node, module: str) -> list[ExtractedSymbol]:
        symbols: list[ExtractedSymbol] = []
        self._walk(source, root, module, class_stack=[], symbols=symbols, skip_export_wrapper=False)
        return symbols

    def _walk(
        self,
        source: bytes,
        node: Node,
        module: str,
        *,
        class_stack: list[str],
        symbols: list[ExtractedSymbol],
        skip_export_wrapper: bool,
    ) -> None:
        ntype = node.type

        if ntype in _IMPORT_TYPES:
            symbols.extend(self._imports(source, node, module))
            return

        if ntype in _EXPORT_TYPES:
            symbols.extend(self._exports(source, node, module, class_stack))
            # Continue into nested declaration so function/class still extracted.
            for child in node.named_children:
                if child.type in {
                    "function_declaration",
                    "generator_function_declaration",
                    "class_declaration",
                    "abstract_class_declaration",
                    "lexical_declaration",
                    "variable_declaration",
                    "interface_declaration",
                    "type_alias_declaration",
                }:
                    self._walk(
                        source,
                        child,
                        module,
                        class_stack=class_stack,
                        symbols=symbols,
                        skip_export_wrapper=True,
                    )
            return

        if ntype in _FUNCTION_TYPES and _name_node(node) is not None:
            symbols.append(self._function(source, node, module, class_stack))
            return

        if ntype in _CLASS_TYPES and _name_node(node) is not None:
            class_sym = self._class(source, node, module, class_stack)
            symbols.append(class_sym)
            body = _child_by_type(node, "class_body")
            if body is not None:
                nested_stack = [*class_stack, class_sym.name]
                for child in body.named_children:
                    self._walk(
                        source,
                        child,
                        module,
                        class_stack=nested_stack,
                        symbols=symbols,
                        skip_export_wrapper=False,
                    )
            return

        if ntype in _METHOD_TYPES and class_stack:
            symbols.append(self._method(source, node, module, class_stack))
            return

        if ntype in _INTERFACE_TYPES and self.language_name == "typescript":
            symbols.append(self._interface(source, node, module))
            return

        if ntype in _TYPE_ALIAS_TYPES and self.language_name == "typescript":
            symbols.append(self._type_alias(source, node, module))
            return

        if ntype in _LEXICAL_TYPES:
            for decl in _children_by_type(node, "variable_declarator"):
                value = None
                for child in decl.named_children:
                    if child.type in _ARROW_TYPES:
                        value = child
                        break
                name_n = _name_node(decl)
                if value is None or name_n is None:
                    continue
                symbols.append(
                    self._arrow(
                        source,
                        decl,
                        value,
                        module,
                        class_stack,
                        name=_text(source, name_n),
                    )
                )
            return

        for child in node.named_children:
            self._walk(
                source,
                child,
                module,
                class_stack=class_stack,
                symbols=symbols,
                skip_export_wrapper=skip_export_wrapper,
            )

    def _function(
        self,
        source: bytes,
        node: Node,
        module: str,
        class_stack: list[str],
    ) -> ExtractedSymbol:
        name = _text(source, _name_node(node))
        start, end = _line_span(node)
        params = _extract_parameters(source, _child_by_type(node, "formal_parameters"))
        body = _child_by_type(node, "statement_block")
        role, detail = _react_role(name, body)
        qparts = [*class_stack, name]
        prefix = "async function" if _is_async(node) else "function"
        return ExtractedSymbol(
            kind="function",
            name=name,
            qualified_name=qualify(module, *qparts),
            start_line=start,
            end_line=end,
            signature=f"{prefix} {name}(...)",
            parameters=params,
            return_annotation=_return_annotation(source, node),
            is_async=_is_async(node),
            framework_role=role,
            framework_detail=detail,
        )

    def _arrow(
        self,
        source: bytes,
        decl: Node,
        value: Node,
        module: str,
        class_stack: list[str],
        *,
        name: str,
    ) -> ExtractedSymbol:
        start, end = _line_span(decl)
        params_node = _child_by_type(value, "formal_parameters")
        params: tuple[ExtractedParameter, ...]
        if params_node is None:
            # Single-param arrow without parens: x => ...
            params = ()
            for child in value.named_children:
                if child.type == "identifier":
                    params = (
                        ExtractedParameter(
                            name=_text(source, child),
                            annotation=None,
                            kind="positional",
                        ),
                    )
                    break
        else:
            params = _extract_parameters(source, params_node)
        body = None
        for child in value.named_children:
            if child.type in _JSX_TYPES or child.type == "statement_block":
                body = child
                break
        role, detail = _react_role(name, body if body is not None else value)
        return ExtractedSymbol(
            kind="function",
            name=name,
            qualified_name=qualify(module, *[*class_stack, name]),
            start_line=start,
            end_line=end,
            signature=f"{'async ' if _is_async(value) else ''}{name} =>",
            parameters=params,
            return_annotation=_return_annotation(source, value),
            is_async=_is_async(value),
            framework_role=role,
            framework_detail=detail,
        )

    def _class(
        self,
        source: bytes,
        node: Node,
        module: str,
        class_stack: list[str],
    ) -> ExtractedSymbol:
        name = _text(source, _name_node(node))
        start, end = _line_span(node)
        body = _child_by_type(node, "class_body")
        role, detail = _react_role(name, body)
        return ExtractedSymbol(
            kind="class",
            name=name,
            qualified_name=qualify(module, *[*class_stack, name]),
            start_line=start,
            end_line=end,
            signature=f"class {name}",
            framework_role=role,
            framework_detail=detail,
        )

    def _method(
        self,
        source: bytes,
        node: Node,
        module: str,
        class_stack: list[str],
    ) -> ExtractedSymbol:
        name_n = _name_node(node)
        name = _text(source, name_n) if name_n else "method"
        start, end = _line_span(node)
        params = _extract_parameters(source, _child_by_type(node, "formal_parameters"))
        return ExtractedSymbol(
            kind="method",
            name=name,
            qualified_name=qualify(module, *[*class_stack, name]),
            start_line=start,
            end_line=end,
            signature=f"{'async ' if _is_async(node) else ''}{name}(...)",
            parameters=params,
            return_annotation=_return_annotation(source, node),
            is_async=_is_async(node),
        )

    def _interface(self, source: bytes, node: Node, module: str) -> ExtractedSymbol:
        name = _text(source, _name_node(node))
        start, end = _line_span(node)
        return ExtractedSymbol(
            kind="interface",
            name=name,
            qualified_name=qualify(module, name),
            start_line=start,
            end_line=end,
            signature=f"interface {name}",
        )

    def _type_alias(self, source: bytes, node: Node, module: str) -> ExtractedSymbol:
        name = _text(source, _name_node(node))
        start, end = _line_span(node)
        return ExtractedSymbol(
            kind="type_alias",
            name=name,
            qualified_name=qualify(module, name),
            start_line=start,
            end_line=end,
            signature=f"type {name}",
        )

    def _imports(self, source: bytes, node: Node, module: str) -> list[ExtractedSymbol]:
        start, end = _line_span(node)
        source_mod = None
        string_node = _child_by_type(node, "string")
        if string_node is not None:
            source_mod = _text(source, string_node).strip("'\"")

        style = "relative" if source_mod and source_mod.startswith(".") else "absolute"
        is_local = bool(source_mod and source_mod.startswith("."))
        out: list[ExtractedSymbol] = []

        clause = _child_by_type(node, "import_clause")
        if clause is None:
            # side-effect import: import "./x"
            out.append(
                ExtractedSymbol(
                    kind="import",
                    name=source_mod or "import",
                    qualified_name=qualify(module, source_mod or "import"),
                    start_line=start,
                    end_line=end,
                    signature=_text(source, node).strip()[:200],
                    resolved_module=source_mod,
                    import_style=style,
                    is_local_import=is_local,
                )
            )
            return out

        # default import
        for child in clause.named_children:
            if child.type == "identifier":
                name = _text(source, child)
                out.append(
                    ExtractedSymbol(
                        kind="import",
                        name=name,
                        qualified_name=qualify(module, name),
                        start_line=start,
                        end_line=end,
                        signature=_text(source, node).strip()[:200],
                        resolved_module=source_mod,
                        import_style=style,
                        is_local_import=is_local,
                    )
                )
            elif child.type == "named_imports":
                for spec in _children_by_type(child, "import_specifier"):
                    ids = [c for c in spec.named_children if c.type == "identifier"]
                    if not ids:
                        continue
                    imported = _text(source, ids[0])
                    alias = _text(source, ids[1]) if len(ids) > 1 else None
                    binding = alias or imported
                    out.append(
                        ExtractedSymbol(
                            kind="import",
                            name=binding,
                            qualified_name=qualify(module, binding),
                            start_line=start,
                            end_line=end,
                            signature=_text(source, node).strip()[:200],
                            resolved_module=f"{source_mod}.{imported}" if source_mod else imported,
                            import_style=style,
                            is_local_import=is_local,
                            import_alias=alias,
                        )
                    )
            elif child.type == "namespace_import":
                ident = _child_by_type(child, "identifier")
                name = _text(source, ident) if ident else "*"
                out.append(
                    ExtractedSymbol(
                        kind="import",
                        name=name,
                        qualified_name=qualify(module, name),
                        start_line=start,
                        end_line=end,
                        signature=_text(source, node).strip()[:200],
                        resolved_module=source_mod,
                        import_style=style,
                        is_local_import=is_local,
                    )
                )
        return out

    def _exports(
        self,
        source: bytes,
        node: Node,
        module: str,
        class_stack: list[str],
    ) -> list[ExtractedSymbol]:
        """Named re-exports only — declarations are extracted when walking children."""
        clause = _child_by_type(node, "export_clause")
        if clause is None:
            return []
        start, end = _line_span(node)
        out: list[ExtractedSymbol] = []
        for spec in _children_by_type(clause, "export_specifier"):
            ids = [c for c in spec.named_children if c.type == "identifier"]
            if not ids:
                continue
            name = _text(source, ids[-1])
            out.append(
                ExtractedSymbol(
                    kind="export",
                    name=name,
                    qualified_name=qualify(module, *[*class_stack, name]),
                    start_line=start,
                    end_line=end,
                    signature=_text(source, node).strip()[:200],
                )
            )
        return out


class TypeScriptTreeSitterParser(_BaseTreeSitterParser):
    parser_name = "typescript-treesitter"
    language_name = "typescript"
    _language = Language(ts_typescript.language_typescript())


class TSXTreeSitterParser(_BaseTreeSitterParser):
    parser_name = "tsx-treesitter"
    language_name = "typescript"
    _language = Language(ts_typescript.language_tsx())


class JavaScriptTreeSitterParser(_BaseTreeSitterParser):
    parser_name = "javascript-treesitter"
    language_name = "javascript"
    _language = Language(ts_javascript.language())


class JSXTreeSitterParser(_BaseTreeSitterParser):
    parser_name = "jsx-treesitter"
    language_name = "javascript"
    # JSX uses the TSX grammar (superset) for reliable JSX node types.
    _language = Language(ts_typescript.language_tsx())
