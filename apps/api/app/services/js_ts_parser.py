"""Tree-sitter deep parsers for JavaScript / TypeScript (Week 5 Days 1–4).

Honesty:
- Structural extraction only — no code execution.
- Days 1–2: parser interfaces + symbol extraction.
- Day 3: relative / index / alias module resolution against known modules.
- Day 4: common-pattern framework roles (Express / Nest / Next / React).
- Call graphs are Day 5+.
- Parse failures leave ``parser_name`` unset (fail closed).
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Protocol

import tree_sitter_javascript as ts_javascript
import tree_sitter_typescript as ts_typescript
from tree_sitter import Language, Node, Parser

from app.services.js_ts_framework import (
    FrameworkMeta,
    detect_js_ts_framework_meta,
    express_route_from_call,
)
from app.services.js_ts_imports import (
    PathAlias,
    nextjs_path_role,
    path_to_module,
    resolve_import_specifier,
)

PARSER_VERSION = "5.4-treesitter"

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
_JSX_TYPES = frozenset({"jsx_element", "jsx_self_closing_element", "jsx_fragment"})
_HTTP_HANDLER_NAMES = frozenset(
    {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}
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


@dataclass(frozen=True, slots=True)
class _ParseContext:
    relative_path: str
    module: str
    known_modules: frozenset[str]
    path_aliases: tuple[PathAlias, ...]


class JsTsTreeSitterParser(Protocol):
    parser_name: str
    language_name: str

    def parse(
        self,
        source: str,
        *,
        relative_path: str,
        known_modules: frozenset[str] = frozenset(),
        path_aliases: tuple[PathAlias, ...] = (),
    ) -> ParseResult: ...


def module_qualified_name(relative_path: str) -> str:
    return path_to_module(relative_path)


def qualify(module: str, *parts: str) -> str:
    chunks = [module] if module else []
    chunks.extend(p for p in parts if p)
    return ".".join(chunks)


def dialect_for_path(relative_path: str) -> str:
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


def parse_js_ts_source(
    source: str,
    *,
    relative_path: str,
    known_modules: frozenset[str] = frozenset(),
    path_aliases: tuple[PathAlias, ...] = (),
) -> ParseResult:
    return parser_for_path(relative_path).parse(
        source,
        relative_path=relative_path,
        known_modules=known_modules,
        path_aliases=path_aliases,
    )


def _text(source: bytes, node: Node | None) -> str:
    if node is None:
        return ""
    return source[node.start_byte : node.end_byte].decode("utf-8", errors="replace")


def _line_span(node: Node) -> tuple[int, int]:
    return node.start_point[0] + 1, node.end_point[0] + 1


def _child_by_type(node: Node, type_name: str) -> Node | None:
    for child in node.children:
        if child.type == type_name:
            return child
    return None


def _children_by_type(node: Node, type_name: str) -> list[Node]:
    return [c for c in node.children if c.type == type_name]


def _name_node(node: Node) -> Node | None:
    for type_name in ("type_identifier", "identifier", "property_identifier"):
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


def _decorators(source: bytes, node: Node) -> tuple[str, ...]:
    out: list[str] = []
    for child in node.children:
        if child.type == "decorator":
            text = _text(source, child).strip()
            if text:
                out.append(text)
    return tuple(out)


def _extract_parameters(
    source: bytes, params_node: Node | None
) -> tuple[ExtractedParameter, ...]:
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


class _BaseTreeSitterParser:
    parser_name: str
    language_name: str
    _language: Language

    def __init__(self) -> None:
        self._parser = Parser(self._language)

    def parse(
        self,
        source: str,
        *,
        relative_path: str,
        known_modules: frozenset[str] = frozenset(),
        path_aliases: tuple[PathAlias, ...] = (),
    ) -> ParseResult:
        try:
            raw = source.encode("utf-8")
        except UnicodeEncodeError as exc:
            return ParseResult(ok=False, symbols=(), error=str(exc))

        try:
            tree = self._parser.parse(raw)
        except Exception as exc:  # noqa: BLE001
            return ParseResult(ok=False, symbols=(), error=str(exc))

        if tree.root_node.has_error:
            return ParseResult(
                ok=False,
                symbols=(),
                error="syntax_error",
                parser_name=self.parser_name,
                language=self.language_name,
            )

        ctx = _ParseContext(
            relative_path=relative_path.replace("\\", "/"),
            module=module_qualified_name(relative_path),
            known_modules=known_modules,
            path_aliases=path_aliases,
        )
        symbols = self._extract(raw, tree.root_node, ctx)
        symbols = self._apply_framework(raw, tree.root_node, symbols, ctx)
        return ParseResult(
            ok=True,
            symbols=tuple(symbols),
            parser_name=self.parser_name,
            language=self.language_name,
        )

    def _extract(
        self, source: bytes, root: Node, ctx: _ParseContext
    ) -> list[ExtractedSymbol]:
        symbols: list[ExtractedSymbol] = []
        self._walk(source, root, ctx, class_stack=[], symbols=symbols)
        return symbols

    def _walk(
        self,
        source: bytes,
        node: Node,
        ctx: _ParseContext,
        *,
        class_stack: list[str],
        symbols: list[ExtractedSymbol],
        inherited_decorators: tuple[str, ...] = (),
    ) -> None:
        ntype = node.type

        if ntype in _IMPORT_TYPES:
            symbols.extend(self._imports(source, node, ctx))
            return

        if ntype in _EXPORT_TYPES:
            symbols.extend(self._exports(source, node, ctx, class_stack))
            export_decos = _decorators(source, node)
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
                        ctx,
                        class_stack=class_stack,
                        symbols=symbols,
                        inherited_decorators=export_decos,
                    )
            return

        if ntype in _FUNCTION_TYPES and _name_node(node) is not None:
            symbols.append(
                self._function(
                    source,
                    node,
                    ctx,
                    class_stack,
                    extra_decorators=inherited_decorators,
                )
            )
            return

        if ntype in _CLASS_TYPES and _name_node(node) is not None:
            class_sym = self._class(
                source,
                node,
                ctx,
                class_stack,
                extra_decorators=inherited_decorators,
            )
            symbols.append(class_sym)
            body = _child_by_type(node, "class_body")
            if body is not None:
                nested = [*class_stack, class_sym.name]
                self._walk_class_body(source, body, ctx, class_stack=nested, symbols=symbols)
            return

        if ntype in _METHOD_TYPES and class_stack:
            symbols.append(
                self._method(
                    source,
                    node,
                    ctx,
                    class_stack,
                    extra_decorators=inherited_decorators,
                )
            )
            return

        if ntype in _INTERFACE_TYPES and self.language_name == "typescript":
            symbols.append(self._interface(source, node, ctx))
            return

        if ntype in _TYPE_ALIAS_TYPES and self.language_name == "typescript":
            symbols.append(self._type_alias(source, node, ctx))
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
                        ctx,
                        class_stack,
                        name=_text(source, name_n),
                    )
                )
            return

        for child in node.named_children:
            self._walk(
                source,
                child,
                ctx,
                class_stack=class_stack,
                symbols=symbols,
                inherited_decorators=(),
            )

    def _walk_class_body(
        self,
        source: bytes,
        body: Node,
        ctx: _ParseContext,
        *,
        class_stack: list[str],
        symbols: list[ExtractedSymbol],
    ) -> None:
        pending: list[str] = []
        for child in body.children:
            if child.type == "decorator":
                text = _text(source, child).strip()
                if text:
                    pending.append(text)
                continue
            if not child.is_named:
                continue
            extras = tuple(pending)
            pending = []
            self._walk(
                source,
                child,
                ctx,
                class_stack=class_stack,
                symbols=symbols,
                inherited_decorators=extras,
            )

    def _function(
        self,
        source: bytes,
        node: Node,
        ctx: _ParseContext,
        class_stack: list[str],
        *,
        extra_decorators: tuple[str, ...] = (),
    ) -> ExtractedSymbol:
        name = _text(source, _name_node(node))
        start, end = _line_span(node)
        body = _child_by_type(node, "statement_block")
        is_react = bool(name and name[0].isupper() and body is not None and _has_jsx(body))
        decos = tuple([*_decorators(source, node), *extra_decorators])
        return ExtractedSymbol(
            kind="function",
            name=name,
            qualified_name=qualify(ctx.module, *[*class_stack, name]),
            start_line=start,
            end_line=end,
            signature=(
                f"{'async function' if _is_async(node) else 'function'} {name}(...)"
            ),
            decorators=decos,
            parameters=_extract_parameters(
                source, _child_by_type(node, "formal_parameters")
            ),
            return_annotation=_return_annotation(source, node),
            is_async=_is_async(node),
            framework_role="react_component" if is_react else None,
            framework_detail=name if is_react else None,
        )

    def _arrow(
        self,
        source: bytes,
        decl: Node,
        value: Node,
        ctx: _ParseContext,
        class_stack: list[str],
        *,
        name: str,
    ) -> ExtractedSymbol:
        start, end = _line_span(decl)
        params_node = _child_by_type(value, "formal_parameters")
        params: tuple[ExtractedParameter, ...]
        if params_node is None:
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
        body: Node | None = None
        for child in value.named_children:
            if child.type in _JSX_TYPES or child.type == "statement_block":
                body = child
                break
        jsx = _has_jsx(body if body is not None else value)
        is_react = bool(name and name[0].isupper() and jsx)
        return ExtractedSymbol(
            kind="function",
            name=name,
            qualified_name=qualify(ctx.module, *[*class_stack, name]),
            start_line=start,
            end_line=end,
            signature=f"{'async ' if _is_async(value) else ''}{name} =>",
            parameters=params,
            return_annotation=_return_annotation(source, value),
            is_async=_is_async(value),
            framework_role="react_component" if is_react else None,
            framework_detail=name if is_react else None,
        )

    def _class(
        self,
        source: bytes,
        node: Node,
        ctx: _ParseContext,
        class_stack: list[str],
        *,
        extra_decorators: tuple[str, ...] = (),
    ) -> ExtractedSymbol:
        name = _text(source, _name_node(node))
        start, end = _line_span(node)
        body = _child_by_type(node, "class_body")
        is_react = bool(name and name[0].isupper() and body is not None and _has_jsx(body))
        decos = tuple([*_decorators(source, node), *extra_decorators])
        return ExtractedSymbol(
            kind="class",
            name=name,
            qualified_name=qualify(ctx.module, *[*class_stack, name]),
            start_line=start,
            end_line=end,
            signature=f"class {name}",
            decorators=decos,
            framework_role="react_component" if is_react else None,
            framework_detail=name if is_react else None,
        )

    def _method(
        self,
        source: bytes,
        node: Node,
        ctx: _ParseContext,
        class_stack: list[str],
        *,
        extra_decorators: tuple[str, ...] = (),
    ) -> ExtractedSymbol:
        name_n = _name_node(node)
        name = _text(source, name_n) if name_n else "method"
        start, end = _line_span(node)
        decos = tuple([*_decorators(source, node), *extra_decorators])
        return ExtractedSymbol(
            kind="method",
            name=name,
            qualified_name=qualify(ctx.module, *[*class_stack, name]),
            start_line=start,
            end_line=end,
            signature=f"{'async ' if _is_async(node) else ''}{name}(...)",
            decorators=decos,
            parameters=_extract_parameters(
                source, _child_by_type(node, "formal_parameters")
            ),
            return_annotation=_return_annotation(source, node),
            is_async=_is_async(node),
        )

    def _interface(
        self, source: bytes, node: Node, ctx: _ParseContext
    ) -> ExtractedSymbol:
        name = _text(source, _name_node(node))
        start, end = _line_span(node)
        return ExtractedSymbol(
            kind="interface",
            name=name,
            qualified_name=qualify(ctx.module, name),
            start_line=start,
            end_line=end,
            signature=f"interface {name}",
        )

    def _type_alias(
        self, source: bytes, node: Node, ctx: _ParseContext
    ) -> ExtractedSymbol:
        name = _text(source, _name_node(node))
        start, end = _line_span(node)
        return ExtractedSymbol(
            kind="type_alias",
            name=name,
            qualified_name=qualify(ctx.module, name),
            start_line=start,
            end_line=end,
            signature=f"type {name}",
        )

    def _resolve(
        self, specifier: str | None, ctx: _ParseContext
    ) -> tuple[str | None, str | None, bool | None]:
        if not specifier:
            return None, None, None
        resolved = resolve_import_specifier(
            specifier,
            current_path=ctx.relative_path,
            known_modules=ctx.known_modules,
            path_aliases=ctx.path_aliases,
        )
        return resolved.resolved_module, resolved.style, resolved.is_local

    def _imports(
        self, source: bytes, node: Node, ctx: _ParseContext
    ) -> list[ExtractedSymbol]:
        start, end = _line_span(node)
        string_node = _child_by_type(node, "string")
        source_mod = _text(source, string_node).strip("'\"") if string_node else None
        resolved_mod, style, is_local = self._resolve(source_mod, ctx)
        out: list[ExtractedSymbol] = []

        clause = _child_by_type(node, "import_clause")
        if clause is None:
            out.append(
                ExtractedSymbol(
                    kind="import",
                    name=source_mod or "import",
                    qualified_name=qualify(ctx.module, source_mod or "import"),
                    start_line=start,
                    end_line=end,
                    signature=_text(source, node).strip()[:200],
                    resolved_module=resolved_mod,
                    import_style=style,
                    is_local_import=is_local,
                )
            )
            return out

        for child in clause.named_children:
            if child.type == "identifier":
                name = _text(source, child)
                out.append(
                    ExtractedSymbol(
                        kind="import",
                        name=name,
                        qualified_name=qualify(ctx.module, name),
                        start_line=start,
                        end_line=end,
                        signature=_text(source, node).strip()[:200],
                        resolved_module=resolved_mod,
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
                    detail_mod = (
                        f"{resolved_mod}.{imported}"
                        if resolved_mod and not resolved_mod.endswith("." + imported)
                        else resolved_mod
                    )
                    out.append(
                        ExtractedSymbol(
                            kind="import",
                            name=binding,
                            qualified_name=qualify(ctx.module, binding),
                            start_line=start,
                            end_line=end,
                            signature=_text(source, node).strip()[:200],
                            resolved_module=detail_mod,
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
                        qualified_name=qualify(ctx.module, name),
                        start_line=start,
                        end_line=end,
                        signature=_text(source, node).strip()[:200],
                        resolved_module=resolved_mod,
                        import_style=style,
                        is_local_import=is_local,
                    )
                )
        return out

    def _exports(
        self,
        source: bytes,
        node: Node,
        ctx: _ParseContext,
        class_stack: list[str],
    ) -> list[ExtractedSymbol]:
        clause = _child_by_type(node, "export_clause")
        if clause is None:
            return []
        start, end = _line_span(node)
        string_node = _child_by_type(node, "string")
        source_mod = _text(source, string_node).strip("'\"") if string_node else None
        resolved_mod, style, is_local = self._resolve(source_mod, ctx)
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
                    qualified_name=qualify(ctx.module, *[*class_stack, name]),
                    start_line=start,
                    end_line=end,
                    signature=_text(source, node).strip()[:200],
                    resolved_module=resolved_mod,
                    import_style=style if source_mod else None,
                    is_local_import=is_local if source_mod else None,
                )
            )
        return out

    def _apply_framework(
        self,
        source: bytes,
        root: Node,
        symbols: list[ExtractedSymbol],
        ctx: _ParseContext,
    ) -> list[ExtractedSymbol]:
        export_names = frozenset(
            s.name for s in symbols if s.kind in {"export", "function", "class"}
        )
        path_role = nextjs_path_role(ctx.relative_path)
        updated = list(symbols)

        for idx, sym in enumerate(symbols):
            has_jsx = sym.framework_role == "react_component"
            meta = detect_js_ts_framework_meta(
                kind=sym.kind,
                name=sym.name,
                decorators=sym.decorators,
                relative_path=ctx.relative_path,
                has_jsx=has_jsx,
                export_names=export_names,
            )
            if meta is None and path_role is not None:
                role, detail = path_role
                if role == "nextjs_route" and sym.name.upper() in _HTTP_HANDLER_NAMES:
                    meta = FrameworkMeta(role=role, detail=detail)
                elif (
                    role == "nextjs_page"
                    and sym.kind in {"function", "class"}
                    and sym.name[:1].isupper()
                ):
                    meta = FrameworkMeta(role=role, detail=detail)

            if meta is None:
                continue
            # Prefer Nest/Express over generic React if both match.
            if sym.framework_role == "react_component" and meta.role == "react_component":
                continue
            updated[idx] = replace(
                sym,
                framework_role=meta.role,
                framework_detail=meta.detail,
            )

        by_name: dict[str, list[int]] = {}
        for idx, sym in enumerate(updated):
            by_name.setdefault(sym.name, []).append(idx)
        self._attach_express_handlers(source, root, updated, by_name)
        return updated

    def _attach_express_handlers(
        self,
        source: bytes,
        root: Node,
        symbols: list[ExtractedSymbol],
        by_name: dict[str, list[int]],
    ) -> None:
        stack = [root]
        while stack:
            node = stack.pop()
            stack.extend(node.children)
            if node.type != "call_expression":
                continue
            fn = node.named_children[0] if node.named_children else None
            if fn is None or fn.type != "member_expression":
                continue
            callee = _text(source, fn)
            target, _, method = callee.rpartition(".")
            if method.lower() not in {
                "get",
                "post",
                "put",
                "patch",
                "delete",
                "options",
                "head",
                "all",
                "use",
            }:
                continue
            if not any(tok in target.lower() for tok in ("app", "router", "server")):
                continue
            args = _child_by_type(node, "arguments")
            if args is None:
                continue
            named = list(args.named_children)
            path_lit = None
            if named and named[0].type == "string":
                path_lit = _text(source, named[0]).strip("'\"")
            handler_name = None
            for arg in named[1:] if len(named) > 1 else []:
                if arg.type == "identifier":
                    handler_name = _text(source, arg)
                    break
            if not handler_name:
                continue
            meta = express_route_from_call(callee, path_lit)
            if meta is None:
                continue
            for idx in by_name.get(handler_name, []):
                current = symbols[idx].framework_role
                if current and current != "react_component":
                    continue
                symbols[idx] = replace(
                    symbols[idx],
                    framework_role=meta.role,
                    framework_detail=meta.detail,
                )


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
    _language = Language(ts_typescript.language_tsx())
