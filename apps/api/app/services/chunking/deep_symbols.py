"""Deep symbol-aware chunks from existing Python / Java / JS-TS symbols."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.language_contract import SupportLevel
from app.models import SourceFile, Symbol
from app.services.chunking.types import ExtractedChunk
from app.services.java_parser import PARSER_NAME as JAVA_PARSER
from app.services.java_parser import PARSER_VERSION as JAVA_VERSION
from app.services.js_ts_parser import PARSER_VERSION as JS_VERSION
from app.services.python_ast_parser import PARSER_NAME as PY_PARSER
from app.services.python_ast_parser import PARSER_VERSION as PY_VERSION

DEEP_CHUNK_KINDS = frozenset(
    {
        "function",
        "method",
        "class",
        "interface",
        "enum",
        "record",
        "type_alias",
        "constructor",
    }
)

_PARSER_BY_LANG = {
    "python": (PY_PARSER, PY_VERSION),
    "java": (JAVA_PARSER, JAVA_VERSION),
    "javascript": ("javascript-treesitter", JS_VERSION),
    "typescript": ("typescript-treesitter", JS_VERSION),
}


def deep_chunks_from_symbols(
    session: Session,
    *,
    snapshot_id,
    repo_root: Path,
) -> list[ExtractedChunk]:
    """Build symbol-aware chunks; never re-route deep langs through generic Tree-sitter."""
    symbols = list(
        session.scalars(
            select(Symbol).where(
                Symbol.snapshot_id == snapshot_id,
                Symbol.language.in_(tuple(_PARSER_BY_LANG.keys())),
                Symbol.kind.in_(tuple(DEEP_CHUNK_KINDS)),
            )
        ).all()
    )
    files = {
        f.id: f
        for f in session.scalars(
            select(SourceFile).where(SourceFile.snapshot_id == snapshot_id)
        ).all()
    }
    out: list[ExtractedChunk] = []
    chunked_paths: set[str] = set()
    for sym in symbols:
        file_row = files.get(sym.source_file_id)
        if file_row is None or file_row.support_level != SupportLevel.DEEP.value:
            continue
        abs_path = repo_root / file_row.path
        try:
            text = abs_path.read_text(encoding="utf-8")
        except OSError:
            continue
        lines = text.splitlines()
        if sym.start_line < 1 or sym.end_line > len(lines) or sym.start_line > sym.end_line:
            continue
        content = "\n".join(lines[sym.start_line - 1 : sym.end_line])
        parser_name, parser_version = _PARSER_BY_LANG.get(
            sym.language, ("unknown", "0")
        )
        # Prefer stamped file parser when present.
        if file_row.parser_name:
            parser_name = file_row.parser_name
        if file_row.parser_version:
            parser_version = file_row.parser_version
        out.append(
            ExtractedChunk.make(
                path=file_row.path,
                language=sym.language,
                support_level=SupportLevel.DEEP.value,
                chunk_type="symbol",
                start_line=sym.start_line,
                end_line=sym.end_line,
                content=content,
                parent_context=sym.qualified_name,
                extraction_method="deep_symbol",
                parser_name=parser_name,
                parser_version=parser_version,
                verified_deep=True,
                symbol_id=sym.id,
            )
        )
        chunked_paths.add(file_row.path)

    # Whole-file fallback for deep files with no extractable symbols
    # (e.g. vite.config.ts with only a default export expression).
    for file_row in files.values():
        if file_row.support_level != SupportLevel.DEEP.value:
            continue
        if file_row.path in chunked_paths:
            continue
        if not file_row.language or file_row.language not in _PARSER_BY_LANG:
            continue
        abs_path = repo_root / file_row.path
        try:
            text = abs_path.read_text(encoding="utf-8")
        except OSError:
            continue
        if not text.strip():
            continue
        # Match discovery line counts (do not use splitlines — drops trailing blank).
        end_line = max(
            1,
            text.count("\n") + (0 if text.endswith("\n") else 1),
        )
        parser_name, parser_version = _PARSER_BY_LANG[file_row.language]
        if file_row.parser_name:
            parser_name = file_row.parser_name
        if file_row.parser_version:
            parser_version = file_row.parser_version
        out.append(
            ExtractedChunk.make(
                path=file_row.path,
                language=file_row.language,
                support_level=SupportLevel.DEEP.value,
                chunk_type="file",
                start_line=1,
                end_line=end_line,
                content=text,
                parent_context=file_row.path,
                extraction_method="deep_file_fallback",
                parser_name=parser_name,
                parser_version=parser_version,
                verified_deep=False,
                symbol_id=None,
            )
        )
    return out
