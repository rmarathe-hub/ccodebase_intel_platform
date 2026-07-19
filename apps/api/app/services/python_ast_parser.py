"""Python stdlib AST deep parser (Week 4 Days 1–4).

Honesty: only Python. No code execution — ``ast.parse`` only. Syntax errors
yield an empty result with ``ok=False`` so callers leave ``parser_name`` unset.

Day 3: common-pattern framework metadata.
Day 4: import resolution (absolute/relative, local vs external).
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass

from app.services.python_framework import detect_framework_meta
from app.services.python_imports import resolve_import_statement

PARSER_NAME = "python-ast"
PARSER_VERSION = f"4.2-{sys.version_info.major}.{sys.version_info.minor}-stdlib"


@dataclass(frozen=True, slots=True)
class ExtractedParameter:
    name: str
    annotation: str | None
    kind: str  # positional | vararg | kwonly | kwarg | posonly


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


def _end_lineno(node: ast.AST) -> int:
    end = getattr(node, "end_lineno", None)
    if isinstance(end, int):
        return end
    lineno = getattr(node, "lineno", None)
    return int(lineno) if isinstance(lineno, int) else 1


def _unparse(node: ast.AST | None) -> str | None:
    if node is None:
        return None
    try:
        return ast.unparse(node)
    except (TypeError, ValueError, RecursionError):
        return None


def module_qualified_name(relative_path: str) -> str:
    """Map a repo-relative Python path to a dotted module name."""
    cleaned = relative_path.replace("\\", "/").strip().lstrip("/")
    if not cleaned:
        return ""
    if cleaned.endswith(".py"):
        cleaned = cleaned[: -len(".py")]
    parts = [p for p in cleaned.split("/") if p and p != "."]
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def qualify(module: str, *parts: str) -> str:
    """Join module + symbol parts into a stable qualified name."""
    chunks = [module] if module else []
    chunks.extend(p for p in parts if p)
    return ".".join(chunks)


def _decorators(node: ast.AST) -> tuple[str, ...]:
    decorator_list = getattr(node, "decorator_list", None)
    if not decorator_list:
        return ()
    out: list[str] = []
    for deco in decorator_list:
        rendered = _unparse(deco)
        if rendered:
            out.append(rendered)
    return tuple(out)


def _bases(node: ast.ClassDef) -> tuple[str, ...]:
    out: list[str] = []
    for base in node.bases:
        rendered = _unparse(base)
        if rendered:
            out.append(rendered)
    return tuple(out)


def _extract_parameters(args: ast.arguments) -> tuple[ExtractedParameter, ...]:
    params: list[ExtractedParameter] = []
    for arg in args.posonlyargs:
        params.append(
            ExtractedParameter(
                name=arg.arg,
                annotation=_unparse(arg.annotation),
                kind="posonly",
            )
        )
    for arg in args.args:
        params.append(
            ExtractedParameter(
                name=arg.arg,
                annotation=_unparse(arg.annotation),
                kind="positional",
            )
        )
    if args.vararg is not None:
        params.append(
            ExtractedParameter(
                name=args.vararg.arg,
                annotation=_unparse(args.vararg.annotation),
                kind="vararg",
            )
        )
    for arg in args.kwonlyargs:
        params.append(
            ExtractedParameter(
                name=arg.arg,
                annotation=_unparse(arg.annotation),
                kind="kwonly",
            )
        )
    if args.kwarg is not None:
        params.append(
            ExtractedParameter(
                name=args.kwarg.arg,
                annotation=_unparse(args.kwarg.annotation),
                kind="kwarg",
            )
        )
    return tuple(params)


def _format_args(args: ast.arguments) -> str:
    parts: list[str] = []
    for arg in args.posonlyargs:
        ann = _unparse(arg.annotation)
        parts.append(f"{arg.arg}: {ann}" if ann else arg.arg)
    if args.posonlyargs:
        parts.append("/")
    for arg in args.args:
        ann = _unparse(arg.annotation)
        parts.append(f"{arg.arg}: {ann}" if ann else arg.arg)
    if args.vararg is not None:
        ann = _unparse(args.vararg.annotation)
        rendered = f"*{args.vararg.arg}"
        parts.append(f"{rendered}: {ann}" if ann else rendered)
    elif args.kwonlyargs:
        parts.append("*")
    for arg in args.kwonlyargs:
        ann = _unparse(arg.annotation)
        parts.append(f"{arg.arg}: {ann}" if ann else arg.arg)
    if args.kwarg is not None:
        ann = _unparse(args.kwarg.annotation)
        rendered = f"**{args.kwarg.arg}"
        parts.append(f"{rendered}: {ann}" if ann else rendered)
    return ", ".join(parts)


def _function_signature(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    *,
    return_annotation: str | None,
) -> str:
    prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
    sig = f"{prefix} {node.name}({_format_args(node.args)})"
    if return_annotation:
        sig = f"{sig} -> {return_annotation}"
    return sig


def _class_signature(node: ast.ClassDef) -> str:
    bases = [_unparse(base) for base in node.bases]
    base_names = [b for b in bases if b]
    if base_names:
        return f"class {node.name}({', '.join(base_names)})"
    return f"class {node.name}"


def _with_framework(
    symbol: ExtractedSymbol,
    *,
    bases: tuple[str, ...] = (),
) -> ExtractedSymbol:
    meta = detect_framework_meta(
        kind=symbol.kind,
        decorators=symbol.decorators,
        bases=bases,
    )
    if meta is None:
        return symbol
    return ExtractedSymbol(
        kind=symbol.kind,
        name=symbol.name,
        qualified_name=symbol.qualified_name,
        start_line=symbol.start_line,
        end_line=symbol.end_line,
        signature=symbol.signature,
        docstring=symbol.docstring,
        decorators=symbol.decorators,
        parameters=symbol.parameters,
        return_annotation=symbol.return_annotation,
        is_async=symbol.is_async,
        framework_role=meta.role,
        framework_detail=meta.detail,
        resolved_module=symbol.resolved_module,
        import_style=symbol.import_style,
        is_local_import=symbol.is_local_import,
        import_alias=symbol.import_alias,
    )


def _append_function(
    found: list[ExtractedSymbol],
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    *,
    kind: str,
    qname: str,
) -> None:
    return_ann = _unparse(node.returns)
    symbol = ExtractedSymbol(
        kind=kind,
        name=node.name,
        qualified_name=qname,
        start_line=node.lineno,
        end_line=_end_lineno(node),
        signature=_function_signature(node, return_annotation=return_ann),
        docstring=ast.get_docstring(node),
        decorators=_decorators(node),
        parameters=_extract_parameters(node.args),
        return_annotation=return_ann,
        is_async=isinstance(node, ast.AsyncFunctionDef),
    )
    found.append(_with_framework(symbol))


def _walk_class_body(
    found: list[ExtractedSymbol],
    node: ast.ClassDef,
    *,
    class_qname: str,
) -> None:
    for child in node.body:
        if isinstance(child, ast.ClassDef):
            nested_q = qualify(class_qname, child.name)
            bases = _bases(child)
            symbol = ExtractedSymbol(
                kind="class",
                name=child.name,
                qualified_name=nested_q,
                start_line=child.lineno,
                end_line=_end_lineno(child),
                signature=_class_signature(child),
                docstring=ast.get_docstring(child),
                decorators=_decorators(child),
            )
            found.append(_with_framework(symbol, bases=bases))
            _walk_class_body(found, child, class_qname=nested_q)
        elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            _append_function(
                found,
                child,
                kind="method",
                qname=qualify(class_qname, child.name),
            )


def parse_python_source(
    source: str,
    *,
    relative_path: str,
    known_modules: frozenset[str] | None = None,
) -> ParseResult:
    """Extract symbols with Days 1–4 metadata (framework + import resolution)."""
    try:
        tree = ast.parse(source, filename=relative_path)
    except SyntaxError as exc:
        return ParseResult(ok=False, symbols=(), error=f"syntax_error:{exc.msg}")

    module = module_qualified_name(relative_path)
    known = known_modules if known_modules is not None else frozenset()
    found: list[ExtractedSymbol] = []

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            qname = qualify(module, node.name)
            bases = _bases(node)
            symbol = ExtractedSymbol(
                kind="class",
                name=node.name,
                qualified_name=qname,
                start_line=node.lineno,
                end_line=_end_lineno(node),
                signature=_class_signature(node),
                docstring=ast.get_docstring(node),
                decorators=_decorators(node),
            )
            found.append(_with_framework(symbol, bases=bases))
            _walk_class_body(found, node, class_qname=qname)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            _append_function(
                found,
                node,
                kind="function",
                qname=qualify(module, node.name),
            )
        elif isinstance(node, ast.Import):
            for alias in node.names:
                binding = alias.asname or alias.name
                resolved = resolve_import_statement(
                    current_module=module,
                    imported_name=alias.name,
                    binding_name=binding,
                    alias=alias.asname,
                    module=None,
                    level=0,
                    known_modules=known,
                    is_from_import=False,
                )
                found.append(
                    ExtractedSymbol(
                        kind="import",
                        name=binding,
                        qualified_name=resolved.resolved_module,
                        start_line=node.lineno,
                        end_line=_end_lineno(node),
                        signature=f"import {alias.name}"
                        + (f" as {alias.asname}" if alias.asname else ""),
                        resolved_module=resolved.resolved_module,
                        import_style=resolved.style,
                        is_local_import=resolved.is_local,
                        import_alias=resolved.alias,
                    )
                )
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                binding = alias.asname or alias.name
                resolved = resolve_import_statement(
                    current_module=module,
                    imported_name=alias.name,
                    binding_name=binding,
                    alias=alias.asname,
                    module=node.module,
                    level=node.level,
                    known_modules=known,
                    is_from_import=True,
                )
                dots = "." * node.level
                mod = node.module or ""
                sig = (
                    f"from {dots}{mod} import {alias.name}"
                    if node.level
                    else f"from {mod} import {alias.name}"
                )
                if alias.asname:
                    sig = f"{sig} as {alias.asname}"
                found.append(
                    ExtractedSymbol(
                        kind="import",
                        name=binding,
                        qualified_name=resolved.resolved_module,
                        start_line=node.lineno,
                        end_line=_end_lineno(node),
                        signature=sig,
                        resolved_module=resolved.resolved_module,
                        import_style=resolved.style,
                        is_local_import=resolved.is_local,
                        import_alias=resolved.alias,
                    )
                )

    found.sort(key=lambda s: (s.start_line, s.kind, s.qualified_name))
    return ParseResult(ok=True, symbols=tuple(found), error=None)
