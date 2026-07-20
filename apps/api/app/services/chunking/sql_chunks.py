"""SQL statement chunks via SQLGlot tokenizer (parser-derived line ranges)."""

from __future__ import annotations

from sqlglot.errors import TokenError
from sqlglot.tokens import Tokenizer, TokenType

from app.core.language_contract import SupportLevel
from app.services.chunking.types import ExtractedChunk

PARSER_NAME = "sqlglot"
PARSER_VERSION = "7.2-sqlglot"


def chunk_sql_source(*, source: str, path: str) -> list[ExtractedChunk]:
    try:
        tokens = Tokenizer().tokenize(source)
    except TokenError:
        return []
    if not tokens:
        return []

    chunks: list[ExtractedChunk] = []
    stmt_start_line = tokens[0].line
    stmt_start_idx = 0
    lines = source.splitlines()

    def _flush(end_line: int, end_idx: int) -> None:
        nonlocal stmt_start_line, stmt_start_idx
        if end_line < stmt_start_line:
            return
        content = "\n".join(lines[stmt_start_line - 1 : end_line])
        if content.strip():
            chunks.append(
                ExtractedChunk.make(
                    path=path,
                    language="sql",
                    support_level=SupportLevel.GENERIC.value,
                    chunk_type="heuristic_section",
                    start_line=stmt_start_line,
                    end_line=end_line,
                    content=content,
                    parent_context="sql_statement",
                    extraction_method="sqlglot_tokenizer",
                    parser_name=PARSER_NAME,
                    parser_version=PARSER_VERSION,
                    verified_deep=False,
                    metadata_json='{"construct":"SQL_statement_group"}',
                )
            )
        if end_idx + 1 < len(tokens):
            stmt_start_line = tokens[end_idx + 1].line
            stmt_start_idx = end_idx + 1

    for i, tok in enumerate(tokens):
        if tok.token_type == TokenType.SEMICOLON:
            _flush(tok.line, i)

    # Trailing statement without semicolon.
    if stmt_start_idx < len(tokens):
        last = tokens[-1]
        content = "\n".join(lines[stmt_start_line - 1 : last.line])
        if content.strip() and (
            not chunks
            or chunks[-1].end_line < stmt_start_line
            or chunks[-1].content != content
        ):
            if not chunks or chunks[-1].start_line != stmt_start_line:
                chunks.append(
                    ExtractedChunk.make(
                        path=path,
                        language="sql",
                        support_level=SupportLevel.GENERIC.value,
                        chunk_type="heuristic_section",
                        start_line=stmt_start_line,
                        end_line=last.line,
                        content=content,
                        parent_context="sql_statement",
                        extraction_method="sqlglot_tokenizer",
                        parser_name=PARSER_NAME,
                        parser_version=PARSER_VERSION,
                        verified_deep=False,
                        metadata_json='{"construct":"SQL_statement_group"}',
                    )
                )
    return chunks
