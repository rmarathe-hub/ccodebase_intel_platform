"""Python stdlib AST deep parser (Week 3 Day 7).

Honesty: only Python. No code execution — ``ast.parse`` only. Syntax errors
yield an empty result with ``ok=False`` so callers leave ``parser_name`` unset.
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass

PARSER_NAME = "python-ast"
PARSER_VERSION = f"{sys.version_info.major}.{sys.version_info.minor}-stdlib"


@dataclass(frozen=True, slots=True)
class ExtractedSymbol:
    kind: str
    name: str
    qualified_name: str
    start_line: int
    end_line: int
    signature: str | None


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


def _format_args(args: ast.arguments) -> str:
    parts: list[str] = []
    for arg in args.posonlyargs:
        parts.append(arg.arg)
    if args.posonlyargs:
        parts.append("/")
    for arg in args.args:
        parts.append(arg.arg)
    if args.vararg is not None:
        parts.append(f"*{args.vararg.arg}")
    elif args.kwonlyargs:
        parts.append("*")
    for arg in args.kwonlyargs:
        parts.append(arg.arg)
    if args.kwarg is not None:
        parts.append(f"**{args.kwarg.arg}")
    return ", ".join(parts)


def _function_signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
    return f"{prefix} {node.name}({_format_args(node.args)})"


def _module_prefix(relative_path: str) -> str:
    cleaned = relative_path.replace("\\", "/").removesuffix(".py")
    return cleaned.replace("/", ".")


def parse_python_source(source: str, *, relative_path: str) -> ParseResult:
    """Extract classes, functions/methods, and imports from Python source text."""
    try:
        tree = ast.parse(source, filename=relative_path)
    except SyntaxError as exc:
        return ParseResult(ok=False, symbols=(), error=f"syntax_error:{exc.msg}")

    module = _module_prefix(relative_path)
    found: list[ExtractedSymbol] = []

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            qname = f"{module}.{node.name}" if module else node.name
            found.append(
                ExtractedSymbol(
                    kind="class",
                    name=node.name,
                    qualified_name=qname,
                    start_line=node.lineno,
                    end_line=_end_lineno(node),
                    signature=f"class {node.name}",
                )
            )
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    method_q = f"{qname}.{child.name}"
                    found.append(
                        ExtractedSymbol(
                            kind="method",
                            name=child.name,
                            qualified_name=method_q,
                            start_line=child.lineno,
                            end_line=_end_lineno(child),
                            signature=_function_signature(child),
                        )
                    )
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            qname = f"{module}.{node.name}" if module else node.name
            found.append(
                ExtractedSymbol(
                    kind="function",
                    name=node.name,
                    qualified_name=qname,
                    start_line=node.lineno,
                    end_line=_end_lineno(node),
                    signature=_function_signature(node),
                )
            )
        elif isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.asname or alias.name
                found.append(
                    ExtractedSymbol(
                        kind="import",
                        name=name,
                        qualified_name=alias.name,
                        start_line=node.lineno,
                        end_line=_end_lineno(node),
                        signature=f"import {alias.name}",
                    )
                )
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            for alias in node.names:
                name = alias.asname or alias.name
                qname = f"{mod}.{alias.name}" if mod else alias.name
                found.append(
                    ExtractedSymbol(
                        kind="import",
                        name=name,
                        qualified_name=qname,
                        start_line=node.lineno,
                        end_line=_end_lineno(node),
                        signature=(
                            f"from {'.' * node.level}{mod} import {alias.name}"
                            if node.level
                            else f"from {mod} import {alias.name}"
                        ),
                    )
                )

    found.sort(key=lambda s: (s.start_line, s.kind, s.qualified_name))
    return ParseResult(ok=True, symbols=tuple(found), error=None)
