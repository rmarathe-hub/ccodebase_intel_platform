"""Persist Java tree-sitter symbols and inheritance edges (Week 6)."""

from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.language_contract import SupportLevel
from app.models.entities import SourceFile, Symbol, SymbolRelation
from app.services.java_inheritance import (
    ExtractedRelation,
    TypeRef,
    package_of_qname,
    resolve_relations,
)
from app.services.java_parser import (
    PARSER_NAME,
    PARSER_VERSION,
    ExtractedSymbol,
    parse_java_source,
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


def replace_java_symbols_for_snapshot(
    session: Session,
    *,
    snapshot_id: UUID,
    repo_root: Path,
) -> tuple[int, int, int]:
    """Parse deep Java files; replace java symbols and inheritance edges.

    Returns ``(parsed_file_count, symbol_count, relation_count)``.
    """
    session.execute(
        delete(SymbolRelation).where(
            SymbolRelation.snapshot_id == snapshot_id,
            SymbolRelation.language == "java",
        )
    )
    session.execute(
        delete(Symbol).where(
            Symbol.snapshot_id == snapshot_id,
            Symbol.language == "java",
        )
    )

    deep_files = list(
        session.scalars(
            select(SourceFile).where(
                SourceFile.snapshot_id == snapshot_id,
                SourceFile.support_level == SupportLevel.DEEP.value,
                SourceFile.language == "java",
            )
        ).all()
    )

    for row in deep_files:
        row.parser_name = None
        row.parser_version = None

    symbol_rows: list[Symbol] = []
    parsed_files = 0
    raw_edges: list[ExtractedRelation] = []
    # from_qname / package → import leaf map
    imports_by_key: dict[str, dict[str, str]] = {}
    type_refs: list[TypeRef] = []
    edge_file_ids: list[tuple[ExtractedRelation, UUID]] = []

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

        result = parse_java_source(text, relative_path=file_row.path)
        if not result.ok or not result.parser_name:
            continue

        parsed_files += 1
        file_row.parser_name = PARSER_NAME
        file_row.parser_version = PARSER_VERSION

        import_map = dict(result.import_map)
        for item in result.symbols:
            symbol_rows.append(
                Symbol(
                    snapshot_id=snapshot_id,
                    source_file_id=file_row.id,
                    kind=item.kind,
                    name=item.name,
                    qualified_name=item.qualified_name,
                    language="java",
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
            if item.kind in {"class", "interface", "enum", "record"}:
                type_refs.append(
                    TypeRef(
                        kind=item.kind,
                        name=item.name,
                        qualified_name=item.qualified_name,
                        package=package_of_qname(item.qualified_name),
                    )
                )
                imports_by_key[item.qualified_name] = import_map
                pkg = package_of_qname(item.qualified_name)
                if pkg:
                    imports_by_key.setdefault(pkg, {}).update(import_map)

        for edge in result.relations:
            raw_edges.append(edge)
            edge_file_ids.append((edge, file_row.id))

    session.add_all(symbol_rows)
    session.flush()

    qname_to_id = {row.qualified_name: row.id for row in symbol_rows}
    resolved = resolve_relations(
        raw_edges, types=type_refs, imports_by_from=imports_by_key
    )
    # Preserve source_file_id by matching edges in order after resolve sort —
    # re-map via (from, kind, raw, line).
    file_lookup = {
        (e.from_qualified_name, e.relation_kind, e.raw_target, e.line): fid
        for e, fid in edge_file_ids
    }

    relation_rows: list[SymbolRelation] = []
    for edge in resolved:
        key = (edge.from_qualified_name, edge.relation_kind, edge.raw_target, edge.line)
        file_id = file_lookup.get(key)
        if file_id is None:
            continue
        to_id = None
        if edge.candidate_qualified_name:
            to_id = qname_to_id.get(edge.candidate_qualified_name)
        relation_rows.append(
            SymbolRelation(
                snapshot_id=snapshot_id,
                source_file_id=file_id,
                from_symbol_id=qname_to_id.get(edge.from_qualified_name),
                from_qualified_name=edge.from_qualified_name,
                relation_kind=edge.relation_kind,
                raw_target=edge.raw_target,
                line=edge.line,
                candidate_qualified_name=edge.candidate_qualified_name,
                to_symbol_id=to_id,
                confidence=edge.confidence,
                language="java",
            )
        )

    session.add_all(relation_rows)
    session.flush()
    return parsed_files, len(symbol_rows), len(relation_rows)
