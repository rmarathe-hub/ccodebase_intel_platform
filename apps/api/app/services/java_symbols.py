"""Persist Java tree-sitter symbols, inheritance edges, and calls (Week 6)."""

from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.language_contract import SupportLevel
from app.models.entities import SourceFile, Symbol, SymbolCall, SymbolRelation
from app.services.java_calls import SymbolRef, extract_java_calls, module_from_qname
from app.services.java_framework import ArchitectureSymbol, classify_spring_architecture
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
) -> tuple[int, int, int, int]:
    """Parse deep Java files; replace symbols, relations, and call sites.

    Returns ``(parsed_file_count, symbol_count, relation_count, call_count)``.
    """
    session.execute(
        delete(SymbolCall).where(
            SymbolCall.snapshot_id == snapshot_id,
            SymbolCall.language == "java",
        )
    )
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

    parsed_files = 0
    raw_edges: list[ExtractedRelation] = []
    imports_by_key: dict[str, dict[str, str]] = {}
    type_refs: list[TypeRef] = []
    edge_file_ids: list[tuple[ExtractedRelation, UUID]] = []
    extracted_by_file: dict[UUID, tuple[ExtractedSymbol, ...]] = {}
    file_sources: dict[UUID, tuple[str, str, dict[str, str]]] = {}
    # file_id -> (path, text, import_map)

    pending_symbols: list[ExtractedSymbol] = []
    pending_file_ids: list[UUID] = []

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
        extracted_by_file[file_row.id] = result.symbols
        file_sources[file_row.id] = (file_row.path, text, import_map)

        for item in result.symbols:
            pending_symbols.append(item)
            pending_file_ids.append(file_row.id)
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

    resolved = resolve_relations(
        raw_edges, types=type_refs, imports_by_from=imports_by_key
    )
    implements_edges = [
        (e.from_qualified_name, e.candidate_qualified_name)
        for e in resolved
        if e.relation_kind == "implements"
        and e.confidence == "resolved"
        and e.candidate_qualified_name
    ]
    arch_updates = classify_spring_architecture(
        [
            ArchitectureSymbol(
                kind=s.kind,
                name=s.name,
                qualified_name=s.qualified_name,
                framework_role=s.framework_role,
                framework_detail=s.framework_detail,
            )
            for s in pending_symbols
        ],
        implements_edges=implements_edges,
    )

    symbol_rows: list[Symbol] = []
    for item, file_id in zip(pending_symbols, pending_file_ids, strict=True):
        role = item.framework_role
        detail = item.framework_detail
        update = arch_updates.get(item.qualified_name)
        if update is not None:
            role = update.role
            detail = update.detail
        symbol_rows.append(
            Symbol(
                snapshot_id=snapshot_id,
                source_file_id=file_id,
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
                framework_role=role,
                framework_detail=detail,
                resolved_module=item.resolved_module,
                import_style=item.import_style,
                is_local_import=item.is_local_import,
                import_alias=item.import_alias,
            )
        )

    session.add_all(symbol_rows)
    session.flush()

    # Prefer per-file symbol ids when sample apps reuse the same FQCN.
    file_qname_to_id = {
        (row.source_file_id, row.qualified_name): row.id for row in symbol_rows
    }
    qname_to_id = {row.qualified_name: row.id for row in symbol_rows}

    relation_rows: list[SymbolRelation] = []
    seen_relation_keys: set[tuple[UUID, str, str, str, int]] = set()
    for raw_edge, source_file_id in edge_file_ids:
        # Resolve one edge at a time so provenance stays bound to its file.
        edge = resolve_relations(
            [raw_edge], types=type_refs, imports_by_from=imports_by_key
        )[0]
        key = (
            source_file_id,
            edge.from_qualified_name,
            edge.relation_kind,
            edge.raw_target,
            edge.line,
        )
        if key in seen_relation_keys:
            continue
        seen_relation_keys.add(key)
        from_id = file_qname_to_id.get(
            (source_file_id, edge.from_qualified_name)
        ) or qname_to_id.get(edge.from_qualified_name)
        to_id = (
            qname_to_id.get(edge.candidate_qualified_name)
            if edge.candidate_qualified_name
            else None
        )
        relation_rows.append(
            SymbolRelation(
                snapshot_id=snapshot_id,
                source_file_id=source_file_id,
                from_symbol_id=from_id,
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

    interface_impls: dict[str, list[str]] = {}
    for from_q, to_q in implements_edges:
        interface_impls.setdefault(to_q, []).append(from_q)

    all_refs: list[SymbolRef] = []
    for file_id, items in extracted_by_file.items():
        path, _text, _imap = file_sources[file_id]
        for item in items:
            all_refs.append(
                SymbolRef(
                    kind=item.kind,
                    name=item.name,
                    qualified_name=item.qualified_name,
                    module=module_from_qname(item.qualified_name, item.kind, item.name)
                    or package_of_qname(item.qualified_name),
                    resolved_module=item.resolved_module,
                    return_annotation=item.return_annotation,
                )
            )

    call_rows: list[SymbolCall] = []
    for file_id, (path, text, import_map) in file_sources.items():
        calls = extract_java_calls(
            text,
            relative_path=path,
            symbols=all_refs,
            import_map=import_map,
            interface_impls=interface_impls,
        )
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
                    language="java",
                )
            )

    session.add_all(call_rows)
    session.flush()
    return parsed_files, len(symbol_rows), len(relation_rows), len(call_rows)
