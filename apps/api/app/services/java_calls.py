"""Java call-site extraction and heuristic resolution (Week 6 Day 6).

Honesty: name / this / field-type / import heuristics — not javac.
Confidence: resolved | ambiguous | unresolved.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

import tree_sitter_java as ts_java
from tree_sitter import Language, Node, Parser

from app.services.java_parser import path_fallback_package


@dataclass(frozen=True, slots=True)
class ExtractedCall:
    caller_qualified_name: str | None
    raw_callee: str
    qualified_expression: str
    line: int
    candidate_qualified_name: str | None
    confidence: str


@dataclass(frozen=True, slots=True)
class SymbolRef:
    kind: str
    name: str
    qualified_name: str
    module: str  # package for Java
    resolved_module: str | None = None
    return_annotation: str | None = None  # field type for injected deps


def module_from_qname(qname: str, kind: str, name: str) -> str:
    if kind == "import":
        if "." in qname:
            return qname.rsplit(".", 1)[0]
        return qname
    if qname.endswith("." + name):
        rest = qname[: -(len(name) + 1)]
        if kind in {"method", "constructor", "field"} and "." in rest:
            # drop class segment for package
            return rest.rsplit(".", 1)[0] if kind != "field" else rest.rsplit(".", 1)[0]
        return rest
    return qname


def build_symbol_index(symbols: list[SymbolRef]) -> dict[str, list[SymbolRef]]:
    by_name: dict[str, list[SymbolRef]] = defaultdict(list)
    for sym in symbols:
        if sym.kind in {"method", "constructor", "class", "interface", "field"}:
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


def _import_aliases(symbols: list[SymbolRef]) -> dict[str, str]:
    aliases: dict[str, str] = {}
    for sym in symbols:
        if sym.kind == "import" and sym.resolved_module and "*" not in sym.name:
            aliases[sym.name] = sym.resolved_module
    return aliases


def _field_types(symbols: list[SymbolRef], enclosing_class: str) -> dict[str, str]:
    """Field simple name → declared type (simple or FQN)."""
    out: dict[str, str] = {}
    prefix = enclosing_class + "."
    for sym in symbols:
        if sym.kind != "field":
            continue
        if not sym.qualified_name.startswith(prefix):
            continue
        if sym.return_annotation:
            out[sym.name] = sym.return_annotation
    return out


def _resolve_method_on_type(
    type_name: str,
    method: str,
    *,
    package: str,
    by_name: dict[str, list[SymbolRef]],
    import_aliases: dict[str, str],
    interface_impls: dict[str, list[str]],
) -> tuple[str | None, str]:
    """Resolve ``Type.method`` / field-typed receiver method."""
    type_fqn = type_name
    if "." not in type_name:
        if type_name in import_aliases:
            type_fqn = import_aliases[type_name]
        else:
            same = f"{package}.{type_name}" if package else type_name
            class_hits = [
                s
                for s in by_name.get(type_name, [])
                if s.kind in {"class", "interface"} and s.qualified_name == same
            ]
            if len(class_hits) == 1:
                type_fqn = class_hits[0].qualified_name
            else:
                all_types = [
                    s
                    for s in by_name.get(type_name, [])
                    if s.kind in {"class", "interface"}
                ]
                if len(all_types) == 1:
                    type_fqn = all_types[0].qualified_name
                elif len(all_types) > 1:
                    return None, "ambiguous"
                else:
                    return None, "unresolved"

    candidate = f"{type_fqn}.{method}"
    exact = [s for s in by_name.get(method, []) if s.qualified_name == candidate]
    if len(exact) == 1:
        return candidate, "resolved"
    if len(exact) > 1:
        return None, "ambiguous"

    # Interface method → unique implementing class method.
    impls = interface_impls.get(type_fqn, [])
    impl_methods = [
        s
        for s in by_name.get(method, [])
        if s.kind == "method"
        and any(s.qualified_name.startswith(impl + ".") for impl in impls)
    ]
    if len(impl_methods) == 1:
        return impl_methods[0].qualified_name, "resolved"
    if len(impl_methods) > 1:
        return None, "ambiguous"

    under = [
        s
        for s in by_name.get(method, [])
        if s.kind == "method" and s.qualified_name.startswith(type_fqn + ".")
    ]
    if len(under) == 1:
        return under[0].qualified_name, "resolved"
    if len(under) > 1:
        return None, "ambiguous"
    return candidate, "unresolved"


def _resolve_simple(
    name: str,
    *,
    package: str,
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
        return target, "unresolved"

    candidates = by_name.get(name, [])
    methods = [c for c in candidates if c.kind in {"method", "constructor"}]
    if enclosing_class:
        same_class = [
            c
            for c in methods
            if c.qualified_name.startswith(enclosing_class + ".")
        ]
        if len(same_class) == 1:
            return same_class[0].qualified_name, "resolved"
        if len(same_class) > 1:
            return None, "ambiguous"

    same_pkg = [c for c in methods if c.module == package]
    pool = same_pkg or methods
    if len(pool) == 1:
        return pool[0].qualified_name, "resolved"
    if len(pool) > 1:
        return None, "ambiguous"
    return None, "unresolved"


def extract_java_calls(
    source: str,
    *,
    relative_path: str,
    symbols: list[SymbolRef],
    import_map: dict[str, str] | None = None,
    interface_impls: dict[str, list[str]] | None = None,
) -> tuple[ExtractedCall, ...]:
    """Extract and resolve call sites from Java source."""
    try:
        raw = source.encode("utf-8")
    except UnicodeEncodeError:
        return ()

    parser = Parser(Language(ts_java.language()))
    try:
        tree = parser.parse(raw)
    except Exception:  # noqa: BLE001
        return ()
    if tree.root_node.has_error:
        return ()

    package = _package_name(raw, tree.root_node) or path_fallback_package(relative_path)
    by_name = build_symbol_index(symbols)
    aliases = dict(import_map or {})
    if not aliases:
        aliases = _import_aliases(symbols)

    calls: list[ExtractedCall] = []
    _walk(
        raw,
        tree.root_node,
        package=package,
        by_name=by_name,
        import_aliases=aliases,
        interface_impls=interface_impls or {},
        symbols=symbols,
        caller_stack=[],
        class_stack=[],
        calls=calls,
    )
    calls.sort(
        key=lambda c: (c.line, c.qualified_expression, c.caller_qualified_name or "")
    )
    return tuple(calls)


def _package_name(source: bytes, root: Node) -> str | None:
    pkg = _child_by_type(root, "package_declaration")
    if pkg is None:
        return None
    for child in pkg.named_children:
        if child.type in {"scoped_identifier", "identifier"}:
            text = _text(source, child).strip()
            return text or None
    return None


def _qualify(package: str, *parts: str) -> str:
    chunks = [package] if package else []
    chunks.extend(p for p in parts if p)
    return ".".join(chunks)


def _walk(
    source: bytes,
    node: Node,
    *,
    package: str,
    by_name: dict[str, list[SymbolRef]],
    import_aliases: dict[str, str],
    interface_impls: dict[str, list[str]],
    symbols: list[SymbolRef],
    caller_stack: list[str],
    class_stack: list[str],
    calls: list[ExtractedCall],
) -> None:
    ntype = node.type

    if ntype in {
        "class_declaration",
        "interface_declaration",
        "enum_declaration",
        "record_declaration",
    }:
        name_n = _child_by_type(node, "identifier")
        name = _text(source, name_n) if name_n else None
        if name:
            nested = [*class_stack, name]
            for child in node.children:
                _walk(
                    source,
                    child,
                    package=package,
                    by_name=by_name,
                    import_aliases=import_aliases,
                    interface_impls=interface_impls,
                    symbols=symbols,
                    caller_stack=caller_stack,
                    class_stack=nested,
                    calls=calls,
                )
            return

    if ntype in {"method_declaration", "constructor_declaration"}:
        name_n = _child_by_type(node, "identifier")
        name = _text(source, name_n) if name_n else None
        if name:
            qname = _qualify(package, *class_stack, name)
            for child in node.children:
                _walk(
                    source,
                    child,
                    package=package,
                    by_name=by_name,
                    import_aliases=import_aliases,
                    interface_impls=interface_impls,
                    symbols=symbols,
                    caller_stack=[*caller_stack, qname],
                    class_stack=class_stack,
                    calls=calls,
                )
            return

    if ntype == "method_invocation":
        _record_call(
            source,
            node,
            package=package,
            by_name=by_name,
            import_aliases=import_aliases,
            interface_impls=interface_impls,
            symbols=symbols,
            caller_stack=caller_stack,
            class_stack=class_stack,
            calls=calls,
        )
        args = _child_by_type(node, "argument_list")
        if args is not None:
            for child in args.children:
                _walk(
                    source,
                    child,
                    package=package,
                    by_name=by_name,
                    import_aliases=import_aliases,
                    interface_impls=interface_impls,
                    symbols=symbols,
                    caller_stack=caller_stack,
                    class_stack=class_stack,
                    calls=calls,
                )
        return

    for child in node.children:
        _walk(
            source,
            child,
            package=package,
            by_name=by_name,
            import_aliases=import_aliases,
            interface_impls=interface_impls,
            symbols=symbols,
            caller_stack=caller_stack,
            class_stack=class_stack,
            calls=calls,
        )


def _record_call(
    source: bytes,
    node: Node,
    *,
    package: str,
    by_name: dict[str, list[SymbolRef]],
    import_aliases: dict[str, str],
    interface_impls: dict[str, list[str]],
    symbols: list[SymbolRef],
    caller_stack: list[str],
    class_stack: list[str],
    calls: list[ExtractedCall],
) -> None:
    if not caller_stack:
        return

    line = node.start_point[0] + 1
    caller = caller_stack[-1]
    enclosing_class = _qualify(package, *class_stack) if class_stack else None
    expr = _text(source, node).split("(")[0].strip()

    parts = [
        c
        for c in node.named_children
        if c.type in {"identifier", "this", "field_access", "type_identifier"}
    ]
    if not parts:
        return

    if len(parts) == 1 and parts[0].type == "identifier":
        name = _text(source, parts[0])
        candidate, confidence = _resolve_simple(
            name,
            package=package,
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

    obj, meth = parts[0], parts[-1]
    if meth.type in {"identifier", "type_identifier"}:
        method_name = _text(source, meth)
    else:
        method_name = expr.rsplit(".", 1)[-1]
    raw = expr

    if obj.type == "this" and enclosing_class:
        candidate, confidence = _resolve_simple(
            method_name,
            package=package,
            enclosing_class=enclosing_class,
            by_name=by_name,
            import_aliases=import_aliases,
        )
        calls.append(
            ExtractedCall(
                caller_qualified_name=caller,
                raw_callee=raw,
                qualified_expression=raw,
                line=line,
                candidate_qualified_name=candidate,
                confidence=confidence,
            )
        )
        return

    if obj.type in {"identifier", "type_identifier"}:
        obj_name = _text(source, obj)
        looks_like_type = obj_name[:1].isupper() or any(
            s.kind in {"class", "interface"} for s in by_name.get(obj_name, [])
        )
        if looks_like_type:
            candidate, confidence = _resolve_method_on_type(
                obj_name,
                method_name,
                package=package,
                by_name=by_name,
                import_aliases=import_aliases,
                interface_impls=interface_impls,
            )
            calls.append(
                ExtractedCall(
                    caller_qualified_name=caller,
                    raw_callee=raw,
                    qualified_expression=raw,
                    line=line,
                    candidate_qualified_name=candidate,
                    confidence=confidence,
                )
            )
            return

        if enclosing_class:
            fields = _field_types(symbols, enclosing_class)
            if obj_name in fields:
                candidate, confidence = _resolve_method_on_type(
                    fields[obj_name],
                    method_name,
                    package=package,
                    by_name=by_name,
                    import_aliases=import_aliases,
                    interface_impls=interface_impls,
                )
                calls.append(
                    ExtractedCall(
                        caller_qualified_name=caller,
                        raw_callee=raw,
                        qualified_expression=raw,
                        line=line,
                        candidate_qualified_name=candidate,
                        confidence=confidence,
                    )
                )
                return

    calls.append(
        ExtractedCall(
            caller_qualified_name=caller,
            raw_callee=raw,
            qualified_expression=raw,
            line=line,
            candidate_qualified_name=None,
            confidence="unresolved",
        )
    )
