"""Tree-sitter deep parser for Java (Week 6 Days 1–4).

Honesty:
- Structural extraction only — no code execution, no classpath resolution.
- Day 1–2: symbols + package-qualified names.
- Day 3: annotation capture + Spring stereotype / mapping heuristics.
- Day 4: EXTENDS / IMPLEMENTS edges (resolution during persist).
- Day 5: Spring architecture classification (naming + implements pairing).
- Day 6: call graphs (heuristic).
- Parse failures leave ``parser_name`` unset (fail closed).
"""

from __future__ import annotations

from dataclasses import dataclass, replace

import tree_sitter_java as ts_java
from tree_sitter import Language, Node, Parser

from app.services.java_framework import detect_java_framework_meta
from app.services.java_inheritance import ExtractedRelation

PARSER_NAME = "java-treesitter"
PARSER_VERSION = "6.6-treesitter"


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
    relations: tuple[ExtractedRelation, ...] = ()
    import_map: tuple[tuple[str, str], ...] = ()  # leaf → FQN


def path_fallback_package(relative_path: str) -> str:
    """Path → dotted package when ``package`` declaration is absent."""
    cleaned = relative_path.replace("\\", "/").strip().lstrip("/")
    if cleaned.endswith(".java"):
        cleaned = cleaned[: -len(".java")]
    parts = [p for p in cleaned.split("/") if p and p != "."]
    if parts:
        parts = parts[:-1]  # drop file stem
    return ".".join(parts)


def qualify(package: str, *parts: str) -> str:
    chunks = [package] if package else []
    chunks.extend(p for p in parts if p)
    return ".".join(chunks)


def parse_java_source(
    source: str,
    *,
    relative_path: str,
    known_modules: frozenset[str] = frozenset(),
) -> ParseResult:
    """Parse Java source; fail closed on syntax / encode errors."""
    del known_modules  # reserved for richer resolution later
    try:
        raw = source.encode("utf-8")
    except UnicodeEncodeError as exc:
        return ParseResult(ok=False, symbols=(), error=str(exc))

    parser = Parser(Language(ts_java.language()))
    try:
        tree = parser.parse(raw)
    except Exception as exc:  # noqa: BLE001
        return ParseResult(ok=False, symbols=(), error=str(exc))
    if tree.root_node.has_error:
        return ParseResult(ok=False, symbols=(), error="syntax_error")

    symbols, relations, import_map = _extract(
        raw, tree.root_node, relative_path=relative_path
    )
    symbols = _apply_framework(symbols)
    return ParseResult(
        ok=True,
        symbols=tuple(symbols),
        parser_name=PARSER_NAME,
        language="java",
        relations=tuple(relations),
        import_map=tuple(import_map.items()),
    )


def _apply_framework(symbols: list[ExtractedSymbol]) -> list[ExtractedSymbol]:
    updated: list[ExtractedSymbol] = []
    for sym in symbols:
        meta = detect_java_framework_meta(kind=sym.kind, decorators=sym.decorators)
        if meta is None:
            updated.append(sym)
            continue
        updated.append(
            replace(
                sym,
                framework_role=meta.role,
                framework_detail=meta.detail,
            )
        )
    return updated


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


def _identifier(source: bytes, node: Node) -> str | None:
    for type_name in ("identifier", "type_identifier"):
        found = _child_by_type(node, type_name)
        if found is not None:
            return _text(source, found)
    return None


def _type_text(source: bytes, node: Node | None) -> str | None:
    if node is None:
        return None
    text = _text(source, node).strip()
    return text or None


def _modifiers(source: bytes, node: Node) -> tuple[str, ...]:
    mods = _child_by_type(node, "modifiers")
    if mods is None:
        return ()
    out: list[str] = []
    for child in mods.children:
        if child.type in {"marker_annotation", "annotation"}:
            text = _text(source, child).strip()
            if text:
                out.append(text)
    return tuple(out)


def _type_parameters(source: bytes, node: Node) -> str | None:
    params = _child_by_type(node, "type_parameters")
    if params is None:
        return None
    return _text(source, params).strip() or None


def _formal_parameters(source: bytes, node: Node) -> tuple[ExtractedParameter, ...]:
    params_node = _child_by_type(node, "formal_parameters")
    if params_node is None:
        params_node = node
    out: list[ExtractedParameter] = []
    for param in _children_by_type(params_node, "formal_parameter"):
        type_n = None
        name_n = None
        for child in param.named_children:
            if child.type in {
                "type_identifier",
                "generic_type",
                "array_type",
                "integral_type",
                "floating_point_type",
                "boolean_type",
                "void_type",
                "scoped_type_identifier",
            }:
                type_n = child
            elif child.type == "identifier":
                name_n = child
        name = _text(source, name_n) if name_n else ""
        if not name:
            continue
        out.append(
            ExtractedParameter(
                name=name,
                annotation=_type_text(source, type_n),
                kind="positional",
            )
        )
    return tuple(out)


def _return_type(source: bytes, node: Node) -> str | None:
    for child in node.named_children:
        if child.type in {
            "type_identifier",
            "generic_type",
            "array_type",
            "integral_type",
            "floating_point_type",
            "boolean_type",
            "void_type",
            "scoped_type_identifier",
        }:
            return _type_text(source, child)
    return None


def _package_name(source: bytes, root: Node) -> str | None:
    pkg = _child_by_type(root, "package_declaration")
    if pkg is None:
        return None
    for child in pkg.named_children:
        if child.type in {"scoped_identifier", "identifier"}:
            return _text(source, child).strip() or None
    return None


def _type_name_from_node(source: bytes, node: Node | None) -> str | None:
    if node is None:
        return None
    if node.type in {"type_identifier", "identifier", "scoped_type_identifier"}:
        return _text(source, node).strip() or None
    # generic_type / etc.
    inner = _child_by_type(node, "type_identifier") or _child_by_type(
        node, "scoped_type_identifier"
    )
    if inner is not None:
        return _text(source, inner).strip() or None
    return _text(source, node).strip() or None


def _extract(
    source: bytes, root: Node, *, relative_path: str
) -> tuple[list[ExtractedSymbol], list[ExtractedRelation], dict[str, str]]:
    package = _package_name(source, root) or path_fallback_package(relative_path)
    symbols: list[ExtractedSymbol] = []
    relations: list[ExtractedRelation] = []
    import_map: dict[str, str] = {}

    pkg_node = _child_by_type(root, "package_declaration")
    if pkg_node is not None and package:
        start, end = _line_span(pkg_node)
        leaf = package.rsplit(".", 1)[-1]
        symbols.append(
            ExtractedSymbol(
                kind="package",
                name=leaf,
                qualified_name=package,
                start_line=start,
                end_line=end,
                signature=f"package {package}",
            )
        )

    for node in root.named_children:
        if node.type == "import_declaration":
            for item in _extract_import(source, node, package=package):
                symbols.append(item)
                if item.resolved_module and "*" not in (item.name or ""):
                    import_map[item.name] = item.resolved_module
        elif node.type == "class_declaration":
            syms, rels = _extract_type(
                source, node, package=package, kind="class", type_stack=[]
            )
            symbols.extend(syms)
            relations.extend(rels)
        elif node.type == "interface_declaration":
            syms, rels = _extract_type(
                source, node, package=package, kind="interface", type_stack=[]
            )
            symbols.extend(syms)
            relations.extend(rels)
        elif node.type == "enum_declaration":
            syms, rels = _extract_type(
                source, node, package=package, kind="enum", type_stack=[]
            )
            symbols.extend(syms)
            relations.extend(rels)
        elif node.type == "record_declaration":
            syms, rels = _extract_type(
                source, node, package=package, kind="record", type_stack=[]
            )
            symbols.extend(syms)
            relations.extend(rels)

    symbols.sort(key=lambda s: (s.start_line, s.qualified_name, s.kind))
    relations.sort(key=lambda r: (r.line, r.relation_kind, r.raw_target))
    return symbols, relations, import_map


def _extract_import(
    source: bytes, node: Node, *, package: str
) -> list[ExtractedSymbol]:
    del package
    start, end = _line_span(node)
    text = _text(source, node).strip()
    target = None
    for child in node.named_children:
        if child.type in {"scoped_identifier", "identifier", "asterisk"}:
            target = _text(source, child).strip()
            break
    if not target:
        return []
    is_static = "static" in text.split()
    is_star = target.endswith("*") or text.rstrip().endswith("*;")
    leaf = target.rstrip(".*").rsplit(".", 1)[-1] if target else "import"
    if is_star:
        leaf = target
    return [
        ExtractedSymbol(
            kind="import",
            name=leaf,
            qualified_name=target,
            start_line=start,
            end_line=end,
            signature=text[:200],
            resolved_module=target,
            import_style="static" if is_static else "absolute",
            is_local_import=None,
        )
    ]


def _extract_inheritance(
    source: bytes,
    node: Node,
    *,
    from_qname: str,
    package: str,
    kind: str,
) -> list[ExtractedRelation]:
    """Extract EXTENDS / IMPLEMENTS edges for a type declaration.

    Tree-sitter-java may expose an interface ``extends`` clause under both
    ``superclass`` and ``extends_interfaces``; reading both produced duplicate
    EXTENDS rows for the same type (seen on awesome-compose Spring samples).
    """
    out: list[ExtractedRelation] = []
    if kind == "interface":
        extends_ifaces = _child_by_type(node, "extends_interfaces")
        # Some grammar versions model interface extends as ``superclass``.
        if extends_ifaces is None:
            extends_ifaces = _child_by_type(node, "superclass")
        if extends_ifaces is not None:
            type_list = _child_by_type(extends_ifaces, "type_list")
            if type_list is not None:
                type_nodes = [
                    n
                    for n in type_list.named_children
                    if n.type
                    in {
                        "type_identifier",
                        "scoped_type_identifier",
                        "generic_type",
                    }
                ]
            else:
                type_nodes = []
                if extends_ifaces.named_children:
                    child = extends_ifaces.named_children[0]
                    if child.type in {
                        "type_identifier",
                        "scoped_type_identifier",
                        "generic_type",
                    }:
                        type_nodes = [child]
            for type_n in type_nodes:
                raw = _type_name_from_node(source, type_n)
                if raw:
                    out.append(
                        ExtractedRelation(
                            from_qualified_name=from_qname,
                            relation_kind="extends",
                            raw_target=raw,
                            line=type_n.start_point[0] + 1,
                            package=package,
                        )
                    )
    else:
        superclass = _child_by_type(node, "superclass")
        if superclass is not None:
            extends_type = (
                superclass.named_children[0] if superclass.named_children else None
            )
            raw = _type_name_from_node(source, extends_type)
            if raw:
                out.append(
                    ExtractedRelation(
                        from_qualified_name=from_qname,
                        relation_kind="extends",
                        raw_target=raw,
                        line=superclass.start_point[0] + 1,
                        package=package,
                    )
                )
        interfaces = _child_by_type(node, "super_interfaces")
        if interfaces is not None:
            type_list = _child_by_type(interfaces, "type_list") or interfaces
            for type_n in type_list.named_children:
                if type_n.type not in {
                    "type_identifier",
                    "scoped_type_identifier",
                    "generic_type",
                }:
                    continue
                raw = _type_name_from_node(source, type_n)
                if raw:
                    out.append(
                        ExtractedRelation(
                            from_qualified_name=from_qname,
                            relation_kind="implements",
                            raw_target=raw,
                            line=type_n.start_point[0] + 1,
                            package=package,
                        )
                    )

    # Deduplicate identical edges (defense in depth).
    seen: set[tuple[str, str, str, int]] = set()
    unique: list[ExtractedRelation] = []
    for edge in out:
        key = (edge.from_qualified_name, edge.relation_kind, edge.raw_target, edge.line)
        if key in seen:
            continue
        seen.add(key)
        unique.append(edge)
    return unique


def _extract_type(
    source: bytes,
    node: Node,
    *,
    package: str,
    kind: str,
    type_stack: list[str],
) -> tuple[list[ExtractedSymbol], list[ExtractedRelation]]:
    name = _identifier(source, node)
    if not name:
        return [], []
    start, end = _line_span(node)
    nested = [*type_stack, name]
    qname = qualify(package, *nested)
    type_params = _type_parameters(source, node)
    decorators = _modifiers(source, node)
    params: tuple[ExtractedParameter, ...] = ()
    if kind == "record":
        params = _formal_parameters(source, node)

    sig_bits = [kind, name]
    if type_params:
        sig_bits.append(type_params)
    signature = " ".join(sig_bits)

    out: list[ExtractedSymbol] = [
        ExtractedSymbol(
            kind=kind,
            name=name,
            qualified_name=qname,
            start_line=start,
            end_line=end,
            signature=signature,
            decorators=decorators,
            parameters=params,
        )
    ]
    relations = _extract_inheritance(
        source, node, from_qname=qname, package=package, kind=kind
    )

    body = (
        _child_by_type(node, "class_body")
        or _child_by_type(node, "interface_body")
        or _child_by_type(node, "enum_body")
        or _child_by_type(node, "record_body")
    )
    if body is None:
        return out, relations

    for child in body.named_children:
        if child.type == "field_declaration":
            out.extend(_extract_fields(source, child, package=package, type_stack=nested))
        elif child.type == "method_declaration":
            out.extend(
                _extract_method(source, child, package=package, type_stack=nested)
            )
        elif child.type == "constructor_declaration":
            out.extend(
                _extract_constructor(source, child, package=package, type_stack=nested)
            )
        elif child.type == "enum_constant":
            const_name = _identifier(source, child)
            if const_name:
                c_start, c_end = _line_span(child)
                out.append(
                    ExtractedSymbol(
                        kind="enum_constant",
                        name=const_name,
                        qualified_name=qualify(package, *nested, const_name),
                        start_line=c_start,
                        end_line=c_end,
                        signature=const_name,
                    )
                )
        elif child.type == "class_declaration":
            syms, rels = _extract_type(
                source, child, package=package, kind="class", type_stack=nested
            )
            out.extend(syms)
            relations.extend(rels)
        elif child.type == "interface_declaration":
            syms, rels = _extract_type(
                source,
                child,
                package=package,
                kind="interface",
                type_stack=nested,
            )
            out.extend(syms)
            relations.extend(rels)
        elif child.type == "enum_declaration":
            syms, rels = _extract_type(
                source, child, package=package, kind="enum", type_stack=nested
            )
            out.extend(syms)
            relations.extend(rels)
        elif child.type == "record_declaration":
            syms, rels = _extract_type(
                source, child, package=package, kind="record", type_stack=nested
            )
            out.extend(syms)
            relations.extend(rels)
    return out, relations


def _extract_fields(
    source: bytes,
    node: Node,
    *,
    package: str,
    type_stack: list[str],
) -> list[ExtractedSymbol]:
    start, end = _line_span(node)
    decorators = _modifiers(source, node)
    type_n = None
    for child in node.named_children:
        if child.type in {
            "type_identifier",
            "generic_type",
            "array_type",
            "integral_type",
            "floating_point_type",
            "boolean_type",
            "scoped_type_identifier",
        }:
            type_n = child
            break
    type_ann = _type_text(source, type_n)
    out: list[ExtractedSymbol] = []
    for decl in _children_by_type(node, "variable_declarator"):
        name = _identifier(source, decl)
        if not name:
            continue
        out.append(
            ExtractedSymbol(
                kind="field",
                name=name,
                qualified_name=qualify(package, *type_stack, name),
                start_line=start,
                end_line=end,
                signature=f"{type_ann} {name}".strip() if type_ann else name,
                decorators=decorators,
                return_annotation=type_ann,
            )
        )
    return out


def _extract_method(
    source: bytes,
    node: Node,
    *,
    package: str,
    type_stack: list[str],
) -> list[ExtractedSymbol]:
    name = _identifier(source, node)
    if not name:
        return []
    start, end = _line_span(node)
    params = _formal_parameters(source, node)
    ret = _return_type(source, node)
    type_params = _type_parameters(source, node)
    decorators = _modifiers(source, node)
    param_sig = ", ".join(
        f"{p.annotation} {p.name}".strip() if p.annotation else p.name for p in params
    )
    sig = f"{name}{type_params or ''}({param_sig})"
    if ret:
        sig = f"{ret} {sig}"
    return [
        ExtractedSymbol(
            kind="method",
            name=name,
            qualified_name=qualify(package, *type_stack, name),
            start_line=start,
            end_line=end,
            signature=sig,
            decorators=decorators,
            parameters=params,
            return_annotation=ret,
        )
    ]


def _extract_constructor(
    source: bytes,
    node: Node,
    *,
    package: str,
    type_stack: list[str],
) -> list[ExtractedSymbol]:
    name = _identifier(source, node)
    if not name:
        return []
    start, end = _line_span(node)
    params = _formal_parameters(source, node)
    decorators = _modifiers(source, node)
    param_sig = ", ".join(
        f"{p.annotation} {p.name}".strip() if p.annotation else p.name for p in params
    )
    return [
        ExtractedSymbol(
            kind="constructor",
            name=name,
            qualified_name=qualify(package, *type_stack, name),
            start_line=start,
            end_line=end,
            signature=f"{name}({param_sig})",
            decorators=decorators,
            parameters=params,
        )
    ]
