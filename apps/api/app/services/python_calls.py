"""Python call-site extraction and heuristic resolution (Week 4 Day 5).

Honesty: resolution is name/import based — not a full type checker.
Confidence labels: resolved | ambiguous | unresolved.
"""

from __future__ import annotations

import ast
from collections import defaultdict
from dataclasses import dataclass

from app.services.python_ast_parser import module_qualified_name, qualify


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


def _unparse(node: ast.AST | None) -> str:
    if node is None:
        return ""
    try:
        return ast.unparse(node)
    except (TypeError, ValueError, RecursionError):
        return ""


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
        # Imported name may be the leaf itself under the module prefix.
        under = [
            c
            for c in by_name.get(leaf, [])
            if c.qualified_name == target or c.qualified_name.endswith("." + leaf)
        ]
        # Prefer exact module suffix match
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


def _resolve_attribute(
    func: ast.Attribute,
    *,
    current_module: str,
    enclosing_class: str | None,
    by_name: dict[str, list[SymbolRef]],
    import_aliases: dict[str, str],
) -> tuple[str, str | None, str]:
    raw = _unparse(func)
    attr = func.attr
    value = func.value

    if isinstance(value, ast.Name) and value.id == "self" and enclosing_class:
        qname = f"{enclosing_class}.{attr}"
        matches = [s for s in by_name.get(attr, []) if s.qualified_name == qname]
        if matches:
            return raw, qname, "resolved"
        prefixed = [
            s
            for s in by_name.get(attr, [])
            if s.kind == "method" and s.qualified_name.startswith(enclosing_class + ".")
        ]
        if len(prefixed) == 1:
            return raw, prefixed[0].qualified_name, "resolved"
        if len(prefixed) > 1:
            return raw, None, "ambiguous"
        return raw, None, "unresolved"

    if isinstance(value, ast.Name):
        base = value.id
        if base in import_aliases:
            resolved_base = import_aliases[base]
            candidate = f"{resolved_base}.{attr}"
            exact = [s for s in by_name.get(attr, []) if s.qualified_name == candidate]
            if len(exact) == 1:
                return raw, candidate, "resolved"
            under = [
                s
                for s in by_name.get(attr, [])
                if s.qualified_name.startswith(resolved_base + ".")
            ]
            if len(under) == 1:
                return raw, under[0].qualified_name, "resolved"
            if len(under) > 1:
                return raw, None, "ambiguous"
            return raw, candidate, "unresolved"

        class_hits = [
            s
            for s in by_name.get(base, [])
            if s.kind == "class" and s.module == current_module
        ]
        if len(class_hits) == 1:
            candidate = f"{class_hits[0].qualified_name}.{attr}"
            methods = [s for s in by_name.get(attr, []) if s.qualified_name == candidate]
            if methods:
                return raw, candidate, "resolved"
            return raw, candidate, "unresolved"

    return raw, None, "unresolved"


def _collect_import_aliases(
    tree: ast.Module,
    symbol_imports: list[SymbolRef],
    *,
    current_module: str,
) -> dict[str, str]:
    from app.services.python_imports import resolve_relative_module

    aliases: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                binding = alias.asname or alias.name
                aliases[binding] = alias.name
        elif isinstance(node, ast.ImportFrom):
            if node.level > 0:
                base = resolve_relative_module(
                    current_module, level=node.level, module=node.module
                )
            else:
                base = node.module or ""
            for alias in node.names:
                binding = alias.asname or alias.name
                if alias.name == "*":
                    aliases[binding] = base
                elif base:
                    aliases[binding] = f"{base}.{alias.name}"
                else:
                    aliases[binding] = alias.name
    # Prefer parser-resolved import symbols when present.
    for sym in symbol_imports:
        aliases[sym.name] = sym.qualified_name
    return aliases


class _CallVisitor(ast.NodeVisitor):
    def __init__(
        self,
        *,
        current_module: str,
        by_name: dict[str, list[SymbolRef]],
        import_aliases: dict[str, str],
    ) -> None:
        self.current_module = current_module
        self.by_name = by_name
        self.import_aliases = import_aliases
        self.calls: list[ExtractedCall] = []
        self._caller_stack: list[str] = []
        self._class_stack: list[str] = []

    def _class_qname(self) -> str | None:
        if not self._class_stack:
            return None
        return qualify(self.current_module, *self._class_stack)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._class_stack.append(node.name)
        self.generic_visit(node)
        self._class_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_function(node)

    def _visit_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        if self._class_stack:
            qname = qualify(self.current_module, *self._class_stack, node.name)
        else:
            qname = qualify(self.current_module, node.name)
        self._caller_stack.append(qname)
        self.generic_visit(node)
        self._caller_stack.pop()

    def visit_Call(self, node: ast.Call) -> None:
        if not self._caller_stack:
            self.generic_visit(node)
            return

        caller = self._caller_stack[-1]
        enclosing_class = self._class_qname()
        expr = _unparse(node.func)
        candidate: str | None = None
        confidence = "unresolved"
        raw = expr

        if isinstance(node.func, ast.Name):
            raw = node.func.id
            candidate, confidence = _resolve_name(
                node.func.id,
                current_module=self.current_module,
                enclosing_class=enclosing_class,
                by_name=self.by_name,
                import_aliases=self.import_aliases,
            )
        elif isinstance(node.func, ast.Attribute):
            raw, candidate, confidence = _resolve_attribute(
                node.func,
                current_module=self.current_module,
                enclosing_class=enclosing_class,
                by_name=self.by_name,
                import_aliases=self.import_aliases,
            )

        self.calls.append(
            ExtractedCall(
                caller_qualified_name=caller,
                raw_callee=raw,
                qualified_expression=expr,
                line=getattr(node, "lineno", 1) or 1,
                candidate_qualified_name=candidate,
                confidence=confidence,
            )
        )
        self.generic_visit(node)


def extract_calls(
    source: str,
    *,
    relative_path: str,
    symbols: list[SymbolRef],
) -> tuple[ExtractedCall, ...]:
    """Extract and resolve call sites from Python source."""
    try:
        tree = ast.parse(source, filename=relative_path)
    except SyntaxError:
        return ()

    module = module_qualified_name(relative_path)
    refs = [
        SymbolRef(
            kind=s.kind,
            name=s.name,
            qualified_name=s.qualified_name,
            module=s.module or module_from_qname(s.qualified_name, s.kind, s.name),
        )
        for s in symbols
    ]
    by_name = build_symbol_index(refs)
    aliases = _collect_import_aliases(
        tree,
        [s for s in refs if s.kind == "import"],
        current_module=module,
    )
    visitor = _CallVisitor(
        current_module=module,
        by_name=by_name,
        import_aliases=aliases,
    )
    visitor.visit(tree)
    calls = sorted(
        visitor.calls,
        key=lambda c: (c.line, c.qualified_expression, c.caller_qualified_name or ""),
    )
    return tuple(calls)
