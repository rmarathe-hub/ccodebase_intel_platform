"""Persist Python AST symbols for a snapshot and stamp parser metadata."""

from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.language_contract import SupportLevel
from app.models.entities import SourceFile, Symbol
from app.services.python_ast_parser import (
    PARSER_NAME,
    PARSER_VERSION,
    ExtractedSymbol,
    parse_python_source,
)


def _decorators_json(item: ExtractedSymbol) -> str | None:
    if not item.decorators:
        return None
    return json.dumps(list(item.decorators))


def _parameters_json(item: ExtractedSymbol) -> str | None:
    if not item.parameters:
        return None
    return json.dumps(
        [
            {"name": p.name, "annotation": p.annotation, "kind": p.kind}
            for p in item.parameters
        ]
    )


def replace_python_symbols_for_snapshot(
    session: Session,
    *,
    snapshot_id: UUID,
    repo_root: Path,
) -> tuple[int, int]:
    """Parse deep Python source_files under ``repo_root`` and replace symbols.

    Returns ``(parsed_file_count, symbol_count)``.
    Non-Python deep files are left with ``parser_name=None`` (honest gap).
    Syntax errors leave that file's parser fields unset and contribute no symbols.
    """
    session.execute(delete(Symbol).where(Symbol.snapshot_id == snapshot_id))

    deep_python = list(
        session.scalars(
            select(SourceFile).where(
                SourceFile.snapshot_id == snapshot_id,
                SourceFile.support_level == SupportLevel.DEEP.value,
                SourceFile.language == "python",
            )
        ).all()
    )

    # Clear prior parser stamps for this snapshot's Python deep files.
    for row in deep_python:
        row.parser_name = None
        row.parser_version = None

    symbol_rows: list[Symbol] = []
    parsed_files = 0

    for file_row in deep_python:
        absolute = (repo_root / file_row.path).resolve()
        try:
            absolute.relative_to(repo_root.resolve())
        except ValueError:
            continue
        if not absolute.is_file():
            continue
        try:
            text = absolute.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        result = parse_python_source(text, relative_path=file_row.path)
        if not result.ok:
            continue

        parsed_files += 1
        file_row.parser_name = PARSER_NAME
        file_row.parser_version = PARSER_VERSION
        for item in result.symbols:
            symbol_rows.append(
                Symbol(
                    snapshot_id=snapshot_id,
                    source_file_id=file_row.id,
                    kind=item.kind,
                    name=item.name,
                    qualified_name=item.qualified_name,
                    language="python",
                    start_line=item.start_line,
                    end_line=item.end_line,
                    signature=item.signature,
                    docstring=item.docstring,
                    decorators_json=_decorators_json(item),
                    parameters_json=_parameters_json(item),
                    return_annotation=item.return_annotation,
                    is_async=item.is_async,
                )
            )

    session.add_all(symbol_rows)
    session.flush()
    return parsed_files, len(symbol_rows)
