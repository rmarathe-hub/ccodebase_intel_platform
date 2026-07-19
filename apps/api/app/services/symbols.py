"""Persist Python AST symbols and call sites for a snapshot."""

from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.language_contract import SupportLevel
from app.models.entities import SourceFile, Symbol, SymbolCall
from app.services.python_ast_parser import (
    PARSER_NAME,
    PARSER_VERSION,
    ExtractedSymbol,
    module_qualified_name,
    parse_python_source,
)
from app.services.python_calls import SymbolRef, extract_calls, module_from_qname


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
) -> tuple[int, int, int]:
    """Parse deep Python files; replace symbols and call sites.

    Returns ``(parsed_file_count, symbol_count, call_count)``.
    """
    # Language-scoped replace so JS/TS symbols (Week 5+) are preserved.
    session.execute(
        delete(SymbolCall).where(
            SymbolCall.snapshot_id == snapshot_id,
            SymbolCall.language == "python",
        )
    )
    session.execute(
        delete(Symbol).where(
            Symbol.snapshot_id == snapshot_id,
            Symbol.language == "python",
        )
    )

    deep_python = list(
        session.scalars(
            select(SourceFile).where(
                SourceFile.snapshot_id == snapshot_id,
                SourceFile.support_level == SupportLevel.DEEP.value,
                SourceFile.language == "python",
            )
        ).all()
    )

    known_modules = frozenset(
        module_qualified_name(row.path) for row in deep_python if row.path
    )

    for row in deep_python:
        row.parser_name = None
        row.parser_version = None

    symbol_rows: list[Symbol] = []
    parsed_files = 0
    file_sources: dict[UUID, tuple[str, str]] = {}  # file_id -> (path, text)
    extracted_by_file: dict[UUID, tuple[ExtractedSymbol, ...]] = {}

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

        result = parse_python_source(
            text,
            relative_path=file_row.path,
            known_modules=known_modules,
        )
        if not result.ok:
            continue

        parsed_files += 1
        file_row.parser_name = PARSER_NAME
        file_row.parser_version = PARSER_VERSION
        file_sources[file_row.id] = (file_row.path, text)
        extracted_by_file[file_row.id] = result.symbols

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

    qname_to_id = {row.qualified_name: row.id for row in symbol_rows}

    all_refs: list[SymbolRef] = []
    for file_id, items in extracted_by_file.items():
        path, _ = file_sources[file_id]
        module = module_qualified_name(path)
        for item in items:
            all_refs.append(
                SymbolRef(
                    kind=item.kind,
                    name=item.name,
                    qualified_name=item.qualified_name,
                    module=module_from_qname(item.qualified_name, item.kind, item.name)
                    or module,
                )
            )

    call_rows: list[SymbolCall] = []
    for file_id, (path, text) in file_sources.items():
        calls = extract_calls(text, relative_path=path, symbols=all_refs)
        for call in calls:
            caller_id = None
            if call.caller_qualified_name:
                caller_id = qname_to_id.get(call.caller_qualified_name)
            call_rows.append(
                SymbolCall(
                    snapshot_id=snapshot_id,
                    source_file_id=file_id,
                    caller_symbol_id=caller_id,
                    caller_qualified_name=call.caller_qualified_name,
                    raw_callee=call.raw_callee,
                    qualified_expression=call.qualified_expression,
                    line=call.line,
                    candidate_qualified_name=call.candidate_qualified_name,
                    confidence=call.confidence,
                    language="python",
                )
            )

    session.add_all(call_rows)
    session.flush()
    return parsed_files, len(symbol_rows), len(call_rows)
