"""Persist JavaScript / TypeScript tree-sitter symbols for a snapshot (Week 5)."""

from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.language_contract import SupportLevel
from app.models.entities import SourceFile, Symbol
from app.services.js_ts_imports import load_tsconfig_paths, path_to_module
from app.services.js_ts_parser import (
    PARSER_VERSION,
    ExtractedSymbol,
    parse_js_ts_source,
)

_JS_TS_LANGUAGES = frozenset({"javascript", "typescript"})


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


def replace_js_ts_symbols_for_snapshot(
    session: Session,
    *,
    snapshot_id: UUID,
    repo_root: Path,
) -> tuple[int, int]:
    """Parse deep JS/TS files; replace only javascript/typescript symbols.

    Day 3: resolves imports against known modules + tsconfig paths.
    Day 4: attaches framework roles.
    Returns ``(parsed_file_count, symbol_count)``.
    """
    session.execute(
        delete(Symbol).where(
            Symbol.snapshot_id == snapshot_id,
            Symbol.language.in_(_JS_TS_LANGUAGES),
        )
    )

    deep_files = list(
        session.scalars(
            select(SourceFile).where(
                SourceFile.snapshot_id == snapshot_id,
                SourceFile.support_level == SupportLevel.DEEP.value,
                SourceFile.language.in_(_JS_TS_LANGUAGES),
            )
        ).all()
    )

    for row in deep_files:
        if row.language in _JS_TS_LANGUAGES:
            row.parser_name = None
            row.parser_version = None

    known_modules = frozenset(path_to_module(row.path) for row in deep_files if row.path)
    path_aliases = load_tsconfig_paths(repo_root)

    symbol_rows: list[Symbol] = []
    parsed_files = 0

    for file_row in deep_files:
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

        result = parse_js_ts_source(
            text,
            relative_path=file_row.path,
            known_modules=known_modules,
            path_aliases=path_aliases,
        )
        if not result.ok or not result.parser_name or not result.language:
            continue

        parsed_files += 1
        file_row.parser_name = result.parser_name
        file_row.parser_version = PARSER_VERSION

        for item in result.symbols:
            symbol_rows.append(
                Symbol(
                    snapshot_id=snapshot_id,
                    source_file_id=file_row.id,
                    kind=item.kind,
                    name=item.name,
                    qualified_name=item.qualified_name,
                    language=result.language,
                    start_line=item.start_line,
                    end_line=item.end_line,
                    signature=item.signature,
                    docstring=item.docstring,
                    decorators_json=_decorators_json(item),
                    parameters_json=_parameters_json(item),
                    return_annotation=item.return_annotation,
                    is_async=item.is_async,
                    framework_role=item.framework_role,
                    framework_detail=item.framework_detail,
                    resolved_module=item.resolved_module,
                    import_style=item.import_style,
                    is_local_import=item.is_local_import,
                    import_alias=item.import_alias,
                )
            )

    session.add_all(symbol_rows)
    session.flush()
    return parsed_files, len(symbol_rows)
