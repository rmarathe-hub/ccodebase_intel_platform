"""Markdown documentation chunks via Mistune AST (no regex headings)."""

from __future__ import annotations

import json
from collections.abc import Sequence
from typing import Any

import mistune

from app.core.language_contract import SupportLevel
from app.services.chunking.types import ExtractedChunk

PARSER_NAME = "mistune-ast"
PARSER_VERSION = "7.4-markdown"


def _heading_text(token: dict[str, Any]) -> str:
    parts: list[str] = []
    children = token.get("children")
    if not isinstance(children, list):
        return ""
    for child in children:
        if not isinstance(child, dict):
            continue
        if child.get("type") == "text":
            parts.append(str(child.get("raw", "")))
        elif child.get("type") == "codespan":
            parts.append(str(child.get("raw", "")))
        elif "children" in child:
            parts.append(_heading_text(child))
    return "".join(parts)


def _collect_headings(tokens: Sequence[Any]) -> list[tuple[int, str]]:
    headings: list[tuple[int, str]] = []
    for tok in tokens:
        if not isinstance(tok, dict):
            continue
        if tok.get("type") == "heading":
            attrs = tok.get("attrs") or {}
            level = int(attrs.get("level", 1)) if isinstance(attrs, dict) else 1
            headings.append((level, _heading_text(tok)))
    return headings


def _locate_atx_heading(lines: list[str], *, level: int, text: str, start_at: int) -> int | None:
    """Find next ATX heading line using string prefix checks (not regex)."""
    prefix = "#" * level + " "
    for i in range(start_at, len(lines)):
        line = lines[i]
        stripped = line.lstrip()
        if stripped.startswith(prefix) and stripped[len(prefix) :].strip() == text:
            return i + 1  # 1-based
        # Also allow closing hashes: "# Title #"
        if stripped.startswith("#" * level) and not stripped.startswith("#" * (level + 1)):
            body = stripped[level:].strip()
            if body.endswith("#"):
                body = body.rstrip("#").strip()
            if body == text:
                return i + 1
    return None


def chunk_markdown_source(*, source: str, path: str) -> list[ExtractedChunk]:
    md = mistune.create_markdown(renderer="ast")
    tokens = md(source)
    if not isinstance(tokens, list):
        return []
    headings = _collect_headings(tokens)
    if not headings:
        # Whole-file documentation chunk when no headings.
        end = max(1, source.count("\n") + (0 if source.endswith("\n") else 1))
        if not source.strip():
            return []
        return [
            ExtractedChunk.make(
                path=path,
                language="documentation",
                support_level=SupportLevel.GENERIC.value,
                chunk_type="documentation_section",
                start_line=1,
                end_line=end,
                content=source.rstrip("\n"),
                parent_context="__document__",
                extraction_method="markdown_ast",
                parser_name=PARSER_NAME,
                parser_version=PARSER_VERSION,
                verified_deep=False,
                metadata_json='{"heading":"__document__","depth":0}',
            )
        ]

    lines = source.splitlines()
    located: list[tuple[int, str, int]] = []  # level, text, start_line
    search_from = 0
    for level, text in headings:
        line_no = _locate_atx_heading(lines, level=level, text=text, start_at=search_from)
        if line_no is None:
            continue
        located.append((level, text, line_no))
        search_from = line_no  # 1-based; next search uses index line_no

    if not located:
        return []

    chunks: list[ExtractedChunk] = []
    path_stack: list[tuple[int, str]] = []
    for idx, (level, text, start) in enumerate(located):
        while path_stack and path_stack[-1][0] >= level:
            path_stack.pop()
        path_stack.append((level, text))
        parent_path = " / ".join(t for _, t in path_stack)
        if idx + 1 < len(located):
            end = located[idx + 1][2] - 1
        else:
            end = len(lines)
        if end < start:
            end = start
        content = "\n".join(lines[start - 1 : end])
        chunks.append(
            ExtractedChunk.make(
                path=path,
                language="documentation",
                support_level=SupportLevel.GENERIC.value,
                chunk_type="documentation_section",
                start_line=start,
                end_line=end,
                content=content,
                parent_context=parent_path,
                extraction_method="markdown_ast",
                parser_name=PARSER_NAME,
                parser_version=PARSER_VERSION,
                verified_deep=False,
                metadata_json=json.dumps(
                    {"heading": text, "depth": level, "path": parent_path}
                ),
            )
        )
    return chunks
