"""JavaScript / TypeScript call-site extraction (Week 5 Day 5).

Honesty: name / import / this-based heuristics — not a type checker.
Confidence labels: resolved | ambiguous | unresolved.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

import tree_sitter_javascript as ts_javascript
import tree_sitter_typescript as ts_typescript
from tree_sitter import Language, Node, Parser

from app.services.js_ts_parser import dialect_for_path, module_qualified_name


@dataclass(frozen=True, slots=True)
class ExtractedCall:
    caller_qualified_name: str | None
    raw_callee: str
    qualified_expression: str
    line: int
    candidate_qualified_name: str | None
    confidence: str  # resolved | ambiguous | unresolved


@dataclass(frozen=True, slots=True)
class SymbolRef:
    kind: str
    name: str
    qualified_name: str
    module: str
    resolved_module: str | None = None


def module_from_qname(qname: str, kind: str, name: str) -> str:
    if kind == "import":
        if "." in qname:
            return qname.rsplit(".", 1)[0]
        return qname
    if qname.endswith("." + name):
        rest = qname[: -(len(name) + 1)]
        if kind == "method" and "." in rest:
            return rest.rsplit(".", 1)[0]
        return rest
    return qname


def build_symbol_index(symbols: list[SymbolRef]) -> dict[str, list[SymbolRef]]:
    by_name: dict[str, list[SymbolRef]] = defaultdict(list)
    for sym in symbols:
        if sym.kind in {"function", "method", "class"}:
            by_name[sym.name].append(sym)
    return by_name


def _text(source: bytes, node: Node | None) -> str:
    if node is None:
        return ""
    return source[node.start_byte : node.end_byte].decode("utf-8", errors="replace")


def _child_by_type(node: Node, type_name: str) -> Node | None:
    for child in node.children:
        if child.type == type_name:
            return child
    return None


def _language_for_path(relative_path: str) -> Language:
    dialect = dialect_for_path(relative_path)
    if dialect in {"tsx", "jsx"}:
        return Language(ts_typescript.language_tsx())
    if dialect == "typescript":
        return Language(ts_typescript.language_typescript())
    return Language(ts_javascript.language())


def _import_aliases(symbols: list[SymbolRef]) -> dict[str, str]:
    """Map local binding → resolved module / symbol target."""
    aliases: dict[str, str] = {}
    for sym in symbols:
        if sym.kind != "import":
            continue
        target = sym.resolved_module
        if target:
            aliases[sym.name] = target
    return aliases


def _resolve_name(
    name: str,
    *,
    current_module: str,
    enclosing_class: str | None,
    by_name: dict[str, list[SymbolRef]],
    import_aliases: dict[str, str],
) -> tuple[str | None, str]:
    if name in import_aliases:
        target = import_aliases[name]
        leaf = target.rsplit(".", 1)[-1]
        matches = [c for c in by_name.get(leaf, []) if c.qualified_name == target]
        if len(matches) == 1:
            return matches[0].qualified_name, "resolved"
        under = [
            c
            for c in by_name.get(leaf, [])
            if c.qualified_name == target or c.qualified_name.endswith("." + leaf)
        ]
        exact = [c for c in by_name.get(name, []) if c.qualified_name == target]
        if len(exact) == 1:
            return exact[0].qualified_name, "resolved"
        if len(matches) > 1 or len(under) > 1:
            return None, "ambiguous"
        return target, "unresolved"

    candidates = by_name.get(name, [])
    if not candidates:
        return None, "unresolved"

    same_module = [c for c in candidates if c.module == current_module]
    pool = same_module or candidates

    if enclosing_class:
        class_methods = [
            c
            for c in pool
            if c.kind == "method" and c.qualified_name.startswith(enclosing_class + ".")
        ]
        if len(class_methods) == 1:
            return class_methods[0].qualified_name, "resolved"
        if len(class_methods) > 1:
            return None, "ambiguous"

    functions = [c for c in pool if c.kind == "function"]
    if len(functions) == 1:
        return functions[0].qualified_name, "resolved"
    if len(functions) > 1:
        return None, "ambiguous"
    if len(pool) == 1:
        return pool[0].qualified_name, "resolved"
    if len(pool) > 1:
        return None, "ambiguous"
    return None, "unresolved"


def _resolve_member(
    object_text: str,
    attr: str,
    *,
    enclosing_class: str | None,
    current_module: str,
    by_name: dict[str, list[SymbolRef]],
    import_aliases: dict[str, str],
) -> tuple[str | None, str]:
    if object_text in {"this", "self"} and enclosing_class:
        qname = f"{enclosing_class}.{attr}"
        matches = [s for s in by_name.get(attr, []) if s.qualified_name == qname]
        if matches:
            return qname, "resolved"
        prefixed = [
            s
            for s in by_name.get(attr, [])
            if s.kind == "method" and s.qualified_name.startswith(enclosing_class + ".")
        ]
        if len(prefixed) == 1:
            return prefixed[0].qualified_name, "resolved"
        if len(prefixed) > 1:
            return None, "ambiguous"
        return None, "unresolved"

    if object_text in import_aliases:
        base = import_aliases[object_text]
        candidate = f"{base}.{attr}"
        exact = [s for s in by_name.get(attr, []) if s.qualified_name == candidate]
        if len(exact) == 1:
            return candidate, "resolved"
        under = [
            s
            for s in by_name.get(attr, [])
            if s.qualified_name.startswith(base + ".")
        ]
        if len(under) == 1:
            return under[0].qualified_name, "resolved"
        if len(under) > 1:
            return None, "ambiguous"
        return candidate, "unresolved"

    class_hits = [
        s
        for s in by_name.get(object_text, [])
        if s.kind == "class" and s.module == current_module
    ]
    if len(class_hits) == 1:
        candidate = f"{class_hits[0].qualified_name}.{attr}"
        methods = [s for s in by_name.get(attr, []) if s.qualified_name == candidate]
        if methods:
            return candidate, "resolved"
        return candidate, "unresolved"

    return None, "unresolved"


def extract_js_ts_calls(
    source: str,
    *,
    relative_path: str,
    symbols: list[SymbolRef],
) -> tuple[ExtractedCall, ...]:
    """Extract and resolve call sites from JS/TS source."""
    try:
        raw = source.encode("utf-8")
    except UnicodeEncodeError:
        return ()

    parser = Parser(_language_for_path(relative_path))
    try:
        tree = parser.parse(raw)
    except Exception:  # noqa: BLE001
        return ()
    if tree.root_node.has_error:
        return ()

    current_module = module_qualified_name(relative_path)
    by_name = build_symbol_index(symbols)
    aliases = _import_aliases(symbols)
    calls: list[ExtractedCall] = []
    _walk(
        raw,
        tree.root_node,
        current_module=current_module,
        by_name=by_name,
        import_aliases=aliases,
        caller_stack=[],
        class_stack=[],
        calls=calls,
    )
    calls.sort(
        key=lambda c: (c.line, c.qualified_expression, c.caller_qualified_name or "")
    )
    return tuple(calls)


def _walk(
    source: bytes,
    node: Node,
    *,
    current_module: str,
    by_name: dict[str, list[SymbolRef]],
    import_aliases: dict[str, str],
    caller_stack: list[str],
    class_stack: list[str],
    calls: list[ExtractedCall],
) -> None:
    ntype = node.type

    if ntype in {"function_declaration", "generator_function_declaration"}:
        name_n = _child_by_type(node, "identifier")
        name = _text(source, name_n) if name_n else None
        if name:
            qname = (
                f"{current_module}.{'.'.join([*class_stack, name])}"
                if current_module
                else ".".join([*class_stack, name])
            )
            _walk_children(
                source,
                node,
                current_module=current_module,
                by_name=by_name,
                import_aliases=import_aliases,
                caller_stack=[*caller_stack, qname],
                class_stack=class_stack,
                calls=calls,
            )
            return

    if ntype == "method_definition":
        name_n = _child_by_type(node, "property_identifier") or _child_by_type(
            node, "identifier"
        )
        name = _text(source, name_n) if name_n else None
        if name and class_stack:
            class_q = (
                f"{current_module}.{'.'.join(class_stack)}"
                if current_module
                else ".".join(class_stack)
            )
            qname = f"{class_q}.{name}"
            _walk_children(
                source,
                node,
                current_module=current_module,
                by_name=by_name,
                import_aliases=import_aliases,
                caller_stack=[*caller_stack, qname],
                class_stack=class_stack,
                calls=calls,
            )
            return

    if ntype in {"class_declaration", "abstract_class_declaration"}:
        name_n = _child_by_type(node, "type_identifier") or _child_by_type(
            node, "identifier"
        )
        name = _text(source, name_n) if name_n else None
        if name:
            _walk_children(
                source,
                node,
                current_module=current_module,
                by_name=by_name,
                import_aliases=import_aliases,
                caller_stack=caller_stack,
                class_stack=[*class_stack, name],
                calls=calls,
            )
            return

    if ntype == "variable_declarator":
        name_n = _child_by_type(node, "identifier")
        value = None
        for child in node.named_children:
            if child.type in {"arrow_function", "function_expression"}:
                value = child
                break
        if name_n is not None and value is not None:
            name = _text(source, name_n)
            qname = (
                f"{current_module}.{'.'.join([*class_stack, name])}"
                if current_module
                else ".".join([*class_stack, name])
            )
            _walk_children(
                source,
                value,
                current_module=current_module,
                by_name=by_name,
                import_aliases=import_aliases,
                caller_stack=[*caller_stack, qname],
                class_stack=class_stack,
                calls=calls,
            )
            # Still walk non-function siblings if any (rare).
            for child in node.children:
                if child is value or child is name_n:
                    continue
                _walk(
                    source,
                    child,
                    current_module=current_module,
                    by_name=by_name,
                    import_aliases=import_aliases,
                    caller_stack=caller_stack,
                    class_stack=class_stack,
                    calls=calls,
                )
            return

    if ntype == "await_expression":
        for child in node.named_children:
            if child.type == "call_expression":
                _record_call(
                    source,
                    child,
                    current_module=current_module,
                    by_name=by_name,
                    import_aliases=import_aliases,
                    caller_stack=caller_stack,
                    class_stack=class_stack,
                    calls=calls,
                )
            else:
                _walk(
                    source,
                    child,
                    current_module=current_module,
                    by_name=by_name,
                    import_aliases=import_aliases,
                    caller_stack=caller_stack,
                    class_stack=class_stack,
                    calls=calls,
                )
        return

    if ntype == "call_expression":
        _record_call(
            source,
            node,
            current_module=current_module,
            by_name=by_name,
            import_aliases=import_aliases,
            caller_stack=caller_stack,
            class_stack=class_stack,
            calls=calls,
        )
        # Arguments may contain nested calls.
        for child in node.children:
            if child.type == "arguments":
                _walk_children(
                    source,
                    child,
                    current_module=current_module,
                    by_name=by_name,
                    import_aliases=import_aliases,
                    caller_stack=caller_stack,
                    class_stack=class_stack,
                    calls=calls,
                )
        return

    _walk_children(
        source,
        node,
        current_module=current_module,
        by_name=by_name,
        import_aliases=import_aliases,
        caller_stack=caller_stack,
        class_stack=class_stack,
        calls=calls,
    )


def _walk_children(
    source: bytes,
    node: Node,
    *,
    current_module: str,
    by_name: dict[str, list[SymbolRef]],
    import_aliases: dict[str, str],
    caller_stack: list[str],
    class_stack: list[str],
    calls: list[ExtractedCall],
) -> None:
    for child in node.children:
        _walk(
            source,
            child,
            current_module=current_module,
            by_name=by_name,
            import_aliases=import_aliases,
            caller_stack=caller_stack,
            class_stack=class_stack,
            calls=calls,
        )


def _record_call(
    source: bytes,
    node: Node,
    *,
    current_module: str,
    by_name: dict[str, list[SymbolRef]],
    import_aliases: dict[str, str],
    caller_stack: list[str],
    class_stack: list[str],
    calls: list[ExtractedCall],
) -> None:
    # Match Python: only record calls inside a known caller scope.
    if not caller_stack:
        return

    fn = node.named_children[0] if node.named_children else None
    if fn is None:
        return

    line = node.start_point[0] + 1
    caller = caller_stack[-1]
    enclosing_class = (
        f"{current_module}.{'.'.join(class_stack)}"
        if class_stack and current_module
        else (".".join(class_stack) if class_stack else None)
    )
    expr = _text(source, fn)

    if fn.type == "identifier":
        name = expr
        candidate, confidence = _resolve_name(
            name,
            current_module=current_module,
            enclosing_class=enclosing_class,
            by_name=by_name,
            import_aliases=import_aliases,
        )
        calls.append(
            ExtractedCall(
                caller_qualified_name=caller,
                raw_callee=name,
                qualified_expression=name,
                line=line,
                candidate_qualified_name=candidate,
                confidence=confidence,
            )
        )
        return

    if fn.type == "member_expression":
        prop = _child_by_type(fn, "property_identifier") or _child_by_type(
            fn, "private_property_identifier"
        )
        obj = fn.named_children[0] if fn.named_children else None
        attr = _text(source, prop) if prop else expr.rsplit(".", 1)[-1]
        obj_text = _text(source, obj) if obj is not None else ""
        # tree-sitter uses node type `this` for the this keyword.
        if obj is not None and obj.type in {"identifier", "this"}:
            candidate, confidence = _resolve_member(
                obj_text,
                attr,
                enclosing_class=enclosing_class,
                current_module=current_module,
                by_name=by_name,
                import_aliases=import_aliases,
            )
        else:
            candidate, confidence = None, "unresolved"
        calls.append(
            ExtractedCall(
                caller_qualified_name=caller,
                raw_callee=expr,
                qualified_expression=expr,
                line=line,
                candidate_qualified_name=candidate,
                confidence=confidence,
            )
        )
