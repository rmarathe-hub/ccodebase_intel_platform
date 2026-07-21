from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.models.entities import IndexingJob, Repository, Symbol, SymbolCall, SymbolRelation
from app.models.relation_kinds import ALL_RELATION_KINDS, RELATION_CONFIDENCES
from app.schemas.calls import (
    SymbolCallListResponse,
    SymbolCallRead,
    SymbolNeighborsResponse,
)
from app.schemas.ask import (
    AskAnalysisEcho,
    AskCitation,
    AskEvidenceItem,
    AskRequest,
    AskResponse,
    AskValidationEcho,
)
from app.schemas.chunks import (
    ChunkSearchHit,
    ChunkSearchResponse,
    DeterministicSummary,
    EvidenceRef,
    RepositorySummaryResponse,
)
from app.schemas.files import RepositoryListItem, SourceFileListResponse, SourceFileRead
from app.schemas.graphs import GraphEdgeRead, GraphNodeRead, RepositoryGraphResponse
from app.schemas.implementations import SymbolImplementationRead, SymbolImplementationsResponse
from app.schemas.jobs import IndexingJobRead
from app.schemas.relations import SymbolRelationListResponse, SymbolRelationRead
from app.schemas.repositories import RepositoryImportRequest, RepositoryRead
from app.schemas.snapshots import RepositoryImportResponse
from app.schemas.symbols import SymbolListResponse, SymbolRead
from app.services.calls_query import (
    get_symbol_in_snapshot,
    list_callees_for_symbol,
    list_callers_for_symbol,
    list_implementations_for_symbol,
    list_symbol_calls,
)
from app.services.chunks_query import VALID_SEARCH_MODES, search_chunks_ranked
from app.services.files_query import (
    latest_ready_snapshot,
    list_repositories,
    list_source_files,
)
from app.services.rag.answer import run_ask
from app.services.rag.citations import citation_key
from app.services.github_url import GitHubURLValidationError
from app.services.graph_filters import apply_graph_filters, filters_echo
from app.services.graphs import (
    build_call_neighborhood_graph,
    build_directory_graph,
    build_module_graph,
    build_package_graph,
)
from app.services.import_repository import (
    RepositoryImportError,
    import_repository,
    retry_indexing_job,
)
from app.services.relations_query import list_symbol_relations
from app.services.repository_summary import build_repository_summary
from app.services.symbols_query import list_symbols

router = APIRouter(prefix="/api/v1")


def _call_read(call: SymbolCall, path: str) -> SymbolCallRead:
    return SymbolCallRead(
        id=call.id,
        snapshot_id=call.snapshot_id,
        source_file_id=call.source_file_id,
        path=path,
        caller_symbol_id=call.caller_symbol_id,
        caller_qualified_name=call.caller_qualified_name,
        raw_callee=call.raw_callee,
        qualified_expression=call.qualified_expression,
        line=call.line,
        candidate_qualified_name=call.candidate_qualified_name,
        confidence=call.confidence,
        language=call.language,
        created_at=call.created_at,
    )


def _symbol_read(sym: Symbol, path: str) -> SymbolRead:
    """Build SymbolRead, letting validators parse JSON metadata columns."""
    return SymbolRead.model_validate(
        {
            "id": sym.id,
            "snapshot_id": sym.snapshot_id,
            "source_file_id": sym.source_file_id,
            "path": path,
            "kind": sym.kind,
            "name": sym.name,
            "qualified_name": sym.qualified_name,
            "language": sym.language,
            "start_line": sym.start_line,
            "end_line": sym.end_line,
            "signature": sym.signature,
            "docstring": sym.docstring,
            "decorators": sym.decorators_json,
            "parameters": sym.parameters_json,
            "return_annotation": sym.return_annotation,
            "is_async": sym.is_async,
            "framework_role": sym.framework_role,
            "framework_detail": sym.framework_detail,
            "resolved_module": sym.resolved_module,
            "import_style": sym.import_style,
            "is_local_import": sym.is_local_import,
            "import_alias": sym.import_alias,
            "created_at": sym.created_at,
        }
    )


@router.post(
    "/repositories/import",
    response_model=RepositoryImportResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def import_github_repository(
    body: RepositoryImportRequest,
    db: Session = Depends(get_db),
) -> RepositoryImportResponse:
    try:
        repo, job, created = import_repository(db, body.url)
    except GitHubURLValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": exc.code, "message": str(exc)},
        ) from exc
    return RepositoryImportResponse(
        repository=RepositoryRead.model_validate(repo),
        job=IndexingJobRead.model_validate(job),
        created_new_job=created,
    )


@router.get("/repositories", response_model=list[RepositoryListItem])
def get_repositories(
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[RepositoryListItem]:
    repos = list_repositories(db, limit=limit)
    return [RepositoryListItem.model_validate(repo) for repo in repos]


@router.get(
    "/repositories/{repository_id}/files",
    response_model=SourceFileListResponse,
)
def get_repository_files(
    repository_id: UUID,
    support_level: str | None = Query(default=None),
    path_prefix: str | None = Query(default=None),
    include_skipped: bool = Query(default=True),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> SourceFileListResponse:
    repo = db.get(Repository, repository_id)
    if repo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found",
        )

    if support_level is not None and support_level.lower() not in {
        "deep",
        "generic",
        "skip",
    }:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "invalid_support_level",
                "message": "support_level must be deep, generic, or skip",
            },
        )

    snapshot = latest_ready_snapshot(db, repository_id)
    if snapshot is None:
        return SourceFileListResponse(
            repository_id=repository_id,
            snapshot_id=None,
            total=0,
            limit=limit,
            offset=offset,
            files=[],
        )

    rows, total = list_source_files(
        db,
        snapshot_id=snapshot.id,
        support_level=support_level,
        path_prefix=path_prefix,
        include_skipped=include_skipped,
        limit=limit,
        offset=offset,
    )
    return SourceFileListResponse(
        repository_id=repository_id,
        snapshot_id=snapshot.id,
        total=total,
        limit=limit,
        offset=offset,
        files=[SourceFileRead.model_validate(row) for row in rows],
    )


@router.get(
    "/repositories/{repository_id}/symbols",
    response_model=SymbolListResponse,
)
def get_repository_symbols(
    repository_id: UUID,
    kind: str | None = Query(default=None),
    path_prefix: str | None = Query(default=None),
    name_contains: str | None = Query(default=None),
    framework_role: str | None = Query(default=None),
    is_local_import: bool | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> SymbolListResponse:
    repo = db.get(Repository, repository_id)
    if repo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found",
        )

    if kind is not None and kind.lower() not in {
        "class",
        "function",
        "method",
        "import",
        "export",
        "interface",
        "type_alias",
        "package",
        "enum",
        "enum_constant",
        "record",
        "field",
        "constructor",
    }:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "invalid_symbol_kind",
                "message": (
                    "kind must be class, function, method, import, export, "
                    "interface, type_alias, package, enum, enum_constant, "
                    "record, field, or constructor"
                ),
            },
        )

    allowed_roles = {
        "fastapi_route",
        "flask_route",
        "django_view",
        "sqlalchemy_model",
        "celery_task",
        "pydantic_model",
        "react_component",
        "express_route",
        "nestjs_controller",
        "nestjs_service",
        "nestjs_route",
        "nextjs_page",
        "nextjs_route",
        "spring_rest_controller",
        "spring_controller",
        "spring_service",
        "spring_repository",
        "spring_component",
        "spring_configuration",
        "spring_entity",
        "spring_route",
        "spring_interface",
        "spring_implementation",
    }
    if framework_role is not None and framework_role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "invalid_framework_role",
                "message": f"framework_role must be one of: {', '.join(sorted(allowed_roles))}",
            },
        )

    snapshot = latest_ready_snapshot(db, repository_id)
    if snapshot is None:
        return SymbolListResponse(
            repository_id=repository_id,
            snapshot_id=None,
            total=0,
            limit=limit,
            offset=offset,
            symbols=[],
        )

    rows, total = list_symbols(
        db,
        snapshot_id=snapshot.id,
        kind=kind,
        path_prefix=path_prefix,
        name_contains=name_contains,
        framework_role=framework_role,
        is_local_import=is_local_import,
        limit=limit,
        offset=offset,
    )
    symbols = [_symbol_read(sym, path) for sym, path in rows]
    return SymbolListResponse(
        repository_id=repository_id,
        snapshot_id=snapshot.id,
        total=total,
        limit=limit,
        offset=offset,
        symbols=symbols,
    )


def _relation_read(rel: SymbolRelation, path: str) -> SymbolRelationRead:
    return SymbolRelationRead(
        id=rel.id,
        snapshot_id=rel.snapshot_id,
        source_file_id=rel.source_file_id,
        path=path,
        from_symbol_id=rel.from_symbol_id,
        from_qualified_name=rel.from_qualified_name,
        relation_kind=rel.relation_kind,
        raw_target=rel.raw_target,
        line=rel.line,
        candidate_qualified_name=rel.candidate_qualified_name,
        to_symbol_id=rel.to_symbol_id,
        confidence=rel.confidence,
        language=rel.language,
        created_at=rel.created_at,
    )


@router.get(
    "/repositories/{repository_id}/relations",
    response_model=SymbolRelationListResponse,
)
def get_repository_relations(
    repository_id: UUID,
    relation_kind: str | None = Query(default=None),
    confidence: str | None = Query(default=None),
    path_prefix: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> SymbolRelationListResponse:
    repo = db.get(Repository, repository_id)
    if repo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found",
        )

    if relation_kind is not None and relation_kind.lower() not in ALL_RELATION_KINDS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "invalid_relation_kind",
                "message": (
                    "relation_kind must be one of: "
                    + ", ".join(sorted(ALL_RELATION_KINDS))
                ),
            },
        )

    if confidence is not None and confidence.lower() not in RELATION_CONFIDENCES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "invalid_confidence",
                "message": "confidence must be resolved, ambiguous, or unresolved",
            },
        )

    snapshot = latest_ready_snapshot(db, repository_id)
    if snapshot is None:
        return SymbolRelationListResponse(
            repository_id=repository_id,
            snapshot_id=None,
            total=0,
            limit=limit,
            offset=offset,
            relations=[],
        )

    rows, total = list_symbol_relations(
        db,
        snapshot_id=snapshot.id,
        relation_kind=relation_kind,
        confidence=confidence,
        path_prefix=path_prefix,
        limit=limit,
        offset=offset,
    )
    relations = [_relation_read(rel, path) for rel, path in rows]
    return SymbolRelationListResponse(
        repository_id=repository_id,
        snapshot_id=snapshot.id,
        total=total,
        limit=limit,
        offset=offset,
        relations=relations,
    )


def _graph_response(
    *,
    repository_id: UUID,
    snapshot_id: UUID | None,
    graph_type: str,
    nodes,
    edges,
    center_symbol_id: UUID | None = None,
    depth: int | None = None,
    filters: dict[str, object] | None = None,
) -> RepositoryGraphResponse:
    return RepositoryGraphResponse(
        repository_id=repository_id,
        snapshot_id=snapshot_id,
        graph_type=graph_type,
        node_count=len(nodes),
        edge_count=len(edges),
        center_symbol_id=center_symbol_id,
        depth=depth,
        filters=filters or {},
        nodes=[
            GraphNodeRead(
                id=n.id,
                label=n.label,
                node_type=n.node_type,
                language=n.language,
                support_level=n.support_level,
                path=n.path,
                symbol_count=n.symbol_count,
                file_count=n.file_count,
                symbol_id=n.symbol_id,
                kind=n.kind,
            )
            for n in nodes
        ],
        edges=[
            GraphEdgeRead(
                source=e.source,
                target=e.target,
                relation_kind=e.relation_kind,
                confidence=e.confidence,
                language=e.language,
                weight=e.weight,
                inferred=e.inferred,
                line=e.line,
            )
            for e in edges
        ],
    )


def _validate_graph_filter_params(
    *,
    support_level: str | None,
    relation_kind: str | None,
    confidence: str | None,
) -> None:
    if support_level is not None and support_level.lower() not in {
        "deep",
        "generic",
        "mixed",
        "skip",
    }:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "invalid_support_level",
                "message": "support_level must be deep, generic, mixed, or skip",
            },
        )
    if relation_kind is not None and relation_kind.lower() not in ALL_RELATION_KINDS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "invalid_relation_kind",
                "message": (
                    "relation_kind must be one of: "
                    + ", ".join(sorted(ALL_RELATION_KINDS))
                ),
            },
        )
    if confidence is not None and confidence.lower() not in RELATION_CONFIDENCES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "invalid_confidence",
                "message": "confidence must be resolved, ambiguous, or unresolved",
            },
        )


@router.get(
    "/repositories/{repository_id}/graph/modules",
    response_model=RepositoryGraphResponse,
)
def get_repository_module_graph(
    repository_id: UUID,
    language: str | None = Query(default=None),
    support_level: str | None = Query(default=None),
    relation_kind: str | None = Query(default=None),
    confidence: str | None = Query(default=None),
    path_prefix: str | None = Query(default=None),
    local_imports_only: bool = Query(default=False),
    max_nodes: int | None = Query(default=None, ge=1, le=2000),
    max_edges: int | None = Query(default=None, ge=1, le=5000),
    db: Session = Depends(get_db),
) -> RepositoryGraphResponse:
    """Module-level graph from IMPORTS relations (deep languages)."""
    repo = db.get(Repository, repository_id)
    if repo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found")
    _validate_graph_filter_params(
        support_level=support_level,
        relation_kind=relation_kind,
        confidence=confidence,
    )
    applied = filters_echo(
        language=language,
        support_level=support_level,
        relation_kind=relation_kind,
        confidence=confidence,
        path_prefix=path_prefix,
        local_imports_only=local_imports_only,
        max_nodes=max_nodes,
        max_edges=max_edges,
    )
    snapshot = latest_ready_snapshot(db, repository_id)
    if snapshot is None:
        return _graph_response(
            repository_id=repository_id,
            snapshot_id=None,
            graph_type="modules",
            nodes=[],
            edges=[],
            filters=applied,
        )
    nodes, edges = build_module_graph(
        db,
        snapshot_id=snapshot.id,
        language=language,
        local_imports_only=local_imports_only,
    )
    nodes, edges = apply_graph_filters(
        nodes,
        edges,
        language=None,  # already applied in builder
        support_level=support_level,
        relation_kind=relation_kind,
        confidence=confidence,
        path_prefix=path_prefix,
        max_nodes=max_nodes,
        max_edges=max_edges,
    )
    return _graph_response(
        repository_id=repository_id,
        snapshot_id=snapshot.id,
        graph_type="modules",
        nodes=nodes,
        edges=edges,
        filters=applied,
    )


@router.get(
    "/repositories/{repository_id}/graph/packages",
    response_model=RepositoryGraphResponse,
)
def get_repository_package_graph(
    repository_id: UUID,
    language: str | None = Query(default=None),
    support_level: str | None = Query(default=None),
    relation_kind: str | None = Query(default=None),
    confidence: str | None = Query(default=None),
    path_prefix: str | None = Query(default=None),
    local_imports_only: bool = Query(default=True),
    max_nodes: int | None = Query(default=None, ge=1, le=2000),
    max_edges: int | None = Query(default=None, ge=1, le=5000),
    db: Session = Depends(get_db),
) -> RepositoryGraphResponse:
    """Package-level graph aggregated from module IMPORTS (deep languages)."""
    repo = db.get(Repository, repository_id)
    if repo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found")
    _validate_graph_filter_params(
        support_level=support_level,
        relation_kind=relation_kind,
        confidence=confidence,
    )
    applied = filters_echo(
        language=language,
        support_level=support_level,
        relation_kind=relation_kind,
        confidence=confidence,
        path_prefix=path_prefix,
        local_imports_only=local_imports_only,
        max_nodes=max_nodes,
        max_edges=max_edges,
    )
    snapshot = latest_ready_snapshot(db, repository_id)
    if snapshot is None:
        return _graph_response(
            repository_id=repository_id,
            snapshot_id=None,
            graph_type="packages",
            nodes=[],
            edges=[],
            filters=applied,
        )
    nodes, edges = build_package_graph(
        db,
        snapshot_id=snapshot.id,
        language=language,
        local_imports_only=local_imports_only,
    )
    nodes, edges = apply_graph_filters(
        nodes,
        edges,
        support_level=support_level,
        relation_kind=relation_kind,
        confidence=confidence,
        path_prefix=path_prefix,
        max_nodes=max_nodes,
        max_edges=max_edges,
    )
    return _graph_response(
        repository_id=repository_id,
        snapshot_id=snapshot.id,
        graph_type="packages",
        nodes=nodes,
        edges=edges,
        filters=applied,
    )


@router.get(
    "/repositories/{repository_id}/graph/calls",
    response_model=RepositoryGraphResponse,
)
def get_repository_call_graph(
    repository_id: UUID,
    symbol_id: UUID = Query(..., description="Center symbol for neighborhood BFS"),
    depth: int = Query(default=1, ge=1, le=3),
    confidence: str | None = Query(default=None),
    language: str | None = Query(default=None),
    support_level: str | None = Query(default=None),
    path_prefix: str | None = Query(default=None),
    max_nodes: int | None = Query(default=None, ge=1, le=2000),
    max_edges: int | None = Query(default=None, ge=1, le=5000),
    db: Session = Depends(get_db),
) -> RepositoryGraphResponse:
    """Symbol-level CALLS neighborhood (deep languages; confidence-aware)."""
    repo = db.get(Repository, repository_id)
    if repo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found")
    _validate_graph_filter_params(
        support_level=support_level,
        relation_kind=None,
        confidence=confidence,
    )
    applied = filters_echo(
        language=language,
        support_level=support_level,
        confidence=confidence,
        path_prefix=path_prefix,
        max_nodes=max_nodes,
        max_edges=max_edges,
        depth=depth,
    )
    snapshot = latest_ready_snapshot(db, repository_id)
    if snapshot is None:
        return _graph_response(
            repository_id=repository_id,
            snapshot_id=None,
            graph_type="calls",
            nodes=[],
            edges=[],
            center_symbol_id=symbol_id,
            depth=depth,
            filters=applied,
        )
    nodes, edges, center = build_call_neighborhood_graph(
        db,
        snapshot_id=snapshot.id,
        center_symbol_id=symbol_id,
        depth=depth,
        confidence=confidence,
        language=language,
    )
    if center is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Symbol not found")
    nodes, edges = apply_graph_filters(
        nodes,
        edges,
        support_level=support_level,
        path_prefix=path_prefix,
        max_nodes=max_nodes,
        max_edges=max_edges,
    )
    return _graph_response(
        repository_id=repository_id,
        snapshot_id=snapshot.id,
        graph_type="calls",
        nodes=nodes,
        edges=edges,
        center_symbol_id=symbol_id,
        depth=depth,
        filters=applied,
    )


@router.get(
    "/repositories/{repository_id}/graph/directories",
    response_model=RepositoryGraphResponse,
)
def get_repository_directory_graph(
    repository_id: UUID,
    include_files: bool = Query(default=False),
    support_level: str | None = Query(default=None),
    relation_kind: str | None = Query(default=None),
    confidence: str | None = Query(default=None),
    path_prefix: str | None = Query(default=None),
    inferred: bool | None = Query(default=None),
    max_nodes: int | None = Query(default=None, ge=1, le=2000),
    max_edges: int | None = Query(default=None, ge=1, le=5000),
    db: Session = Depends(get_db),
) -> RepositoryGraphResponse:
    """Directory hierarchy for all indexed files; inferred cross-dir IMPORTS when known."""
    repo = db.get(Repository, repository_id)
    if repo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found")
    _validate_graph_filter_params(
        support_level=support_level,
        relation_kind=relation_kind,
        confidence=confidence,
    )
    applied = filters_echo(
        support_level=support_level,
        relation_kind=relation_kind,
        confidence=confidence,
        path_prefix=path_prefix,
        inferred=inferred,
        include_files=include_files,
        max_nodes=max_nodes,
        max_edges=max_edges,
    )
    snapshot = latest_ready_snapshot(db, repository_id)
    if snapshot is None:
        return _graph_response(
            repository_id=repository_id,
            snapshot_id=None,
            graph_type="directories",
            nodes=[],
            edges=[],
            filters=applied,
        )
    nodes, edges = build_directory_graph(
        db,
        snapshot_id=snapshot.id,
        include_files=include_files,
    )
    nodes, edges = apply_graph_filters(
        nodes,
        edges,
        support_level=support_level,
        relation_kind=relation_kind,
        confidence=confidence,
        path_prefix=path_prefix,
        inferred=inferred,
        max_nodes=max_nodes,
        max_edges=max_edges,
    )
    return _graph_response(
        repository_id=repository_id,
        snapshot_id=snapshot.id,
        graph_type="directories",
        nodes=nodes,
        edges=edges,
        filters=applied,
    )


@router.get(
    "/repositories/{repository_id}/calls",
    response_model=SymbolCallListResponse,
)
def get_repository_calls(
    repository_id: UUID,
    confidence: str | None = Query(default=None),
    caller_contains: str | None = Query(default=None),
    path_prefix: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> SymbolCallListResponse:
    repo = db.get(Repository, repository_id)
    if repo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found",
        )

    if confidence is not None and confidence.lower() not in {
        "resolved",
        "ambiguous",
        "unresolved",
    }:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "invalid_confidence",
                "message": "confidence must be resolved, ambiguous, or unresolved",
            },
        )

    snapshot = latest_ready_snapshot(db, repository_id)
    if snapshot is None:
        return SymbolCallListResponse(
            repository_id=repository_id,
            snapshot_id=None,
            total=0,
            limit=limit,
            offset=offset,
            calls=[],
        )

    rows, total = list_symbol_calls(
        db,
        snapshot_id=snapshot.id,
        confidence=confidence,
        caller_contains=caller_contains,
        path_prefix=path_prefix,
        limit=limit,
        offset=offset,
    )
    calls = [_call_read(call, path) for call, path in rows]
    return SymbolCallListResponse(
        repository_id=repository_id,
        snapshot_id=snapshot.id,
        total=total,
        limit=limit,
        offset=offset,
        calls=calls,
    )


@router.get(
    "/repositories/{repository_id}/symbols/{symbol_id}/callers",
    response_model=SymbolNeighborsResponse,
)
def get_symbol_callers(
    repository_id: UUID,
    symbol_id: UUID,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> SymbolNeighborsResponse:
    repo = db.get(Repository, repository_id)
    if repo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found")
    snapshot = latest_ready_snapshot(db, repository_id)
    if snapshot is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No ready snapshot")
    symbol = get_symbol_in_snapshot(db, snapshot_id=snapshot.id, symbol_id=symbol_id)
    if symbol is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Symbol not found")
    rows = list_callers_for_symbol(
        db, snapshot_id=snapshot.id, symbol=symbol, limit=limit
    )
    calls = [_call_read(call, path) for call, path in rows]
    return SymbolNeighborsResponse(
        repository_id=repository_id,
        snapshot_id=snapshot.id,
        symbol_id=symbol.id,
        symbol_qualified_name=symbol.qualified_name,
        direction="callers",
        total=len(calls),
        calls=calls,
    )


@router.get(
    "/repositories/{repository_id}/symbols/{symbol_id}/callees",
    response_model=SymbolNeighborsResponse,
)
def get_symbol_callees(
    repository_id: UUID,
    symbol_id: UUID,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> SymbolNeighborsResponse:
    repo = db.get(Repository, repository_id)
    if repo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found")
    snapshot = latest_ready_snapshot(db, repository_id)
    if snapshot is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No ready snapshot")
    symbol = get_symbol_in_snapshot(db, snapshot_id=snapshot.id, symbol_id=symbol_id)
    if symbol is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Symbol not found")
    rows = list_callees_for_symbol(
        db, snapshot_id=snapshot.id, symbol_id=symbol.id, limit=limit
    )
    calls = [_call_read(call, path) for call, path in rows]
    return SymbolNeighborsResponse(
        repository_id=repository_id,
        snapshot_id=snapshot.id,
        symbol_id=symbol.id,
        symbol_qualified_name=symbol.qualified_name,
        direction="callees",
        total=len(calls),
        calls=calls,
    )


@router.get(
    "/repositories/{repository_id}/symbols/{symbol_id}/implementations",
    response_model=SymbolImplementationsResponse,
)
def get_symbol_implementations(
    repository_id: UUID,
    symbol_id: UUID,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> SymbolImplementationsResponse:
    """Classes that implement the given interface/type (Java IMPLEMENTS edges)."""
    repo = db.get(Repository, repository_id)
    if repo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found")
    snapshot = latest_ready_snapshot(db, repository_id)
    if snapshot is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No ready snapshot")
    symbol = get_symbol_in_snapshot(db, snapshot_id=snapshot.id, symbol_id=symbol_id)
    if symbol is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Symbol not found")
    rows = list_implementations_for_symbol(
        db, snapshot_id=snapshot.id, symbol=symbol, limit=limit
    )
    implementations = [
        SymbolImplementationRead(
            symbol_id=impl.id,
            qualified_name=impl.qualified_name,
            name=impl.name,
            kind=impl.kind,
            path=path,
            line=impl.start_line,
            confidence=conf,
            relation_kind="implements",
            language=impl.language,
            created_at=impl.created_at,
        )
        for impl, path, conf in rows
    ]
    return SymbolImplementationsResponse(
        repository_id=repository_id,
        snapshot_id=snapshot.id,
        symbol_id=symbol.id,
        symbol_qualified_name=symbol.qualified_name,
        symbol_kind=symbol.kind,
        total=len(implementations),
        implementations=implementations,
    )


@router.get(
    "/repositories/{repository_id}/summary",
    response_model=RepositorySummaryResponse,
)
def get_repository_summary(
    repository_id: UUID,
    db: Session = Depends(get_db),
) -> RepositorySummaryResponse:
    """Deterministic summary always; optional LLM-enhanced summary when enabled."""
    repo = db.get(Repository, repository_id)
    if repo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found")
    snapshot = latest_ready_snapshot(db, repository_id)
    if snapshot is None:
        return RepositorySummaryResponse(
            repository_id=repository_id,
            snapshot_id=None,
            deterministic_summary=None,
            llm_summary=None,
            llm_summary_status="no_snapshot",
            evidence=[],
            model_provenance=None,
        )
    built = build_repository_summary(db, snapshot_id=snapshot.id)
    det = built.get("deterministic_summary")
    return RepositorySummaryResponse(
        repository_id=repository_id,
        snapshot_id=snapshot.id,
        deterministic_summary=(
            DeterministicSummary.model_validate(det) if isinstance(det, dict) else None
        ),
        llm_summary=built.get("llm_summary") if isinstance(built.get("llm_summary"), dict) else None,
        llm_summary_status=str(built.get("llm_summary_status", "skipped")),
        evidence=[EvidenceRef.model_validate(e) for e in (built.get("evidence") or [])],
        model_provenance=(
            built.get("model_provenance")
            if isinstance(built.get("model_provenance"), dict)
            else None
        ),
    )


@router.get(
    "/repositories/{repository_id}/chunks/search",
    response_model=ChunkSearchResponse,
)
def search_repository_chunks(
    repository_id: UUID,
    q: str = Query(..., min_length=1, max_length=500, description="Search query"),
    search_mode: str = Query(
        default="exact",
        description="exact | semantic | hybrid | rrf | rerank",
    ),
    language: str | None = Query(default=None),
    path_prefix: str | None = Query(default=None),
    support_level: str | None = Query(default=None),
    chunk_type: str | None = Query(default=None),
    extraction_method: str | None = Query(default=None),
    parser_name: str | None = Query(default=None),
    llm_enriched: bool | None = Query(default=None),
    validation_status: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> ChunkSearchResponse:
    """Chunk search: exact (default), semantic (pgvector), or hybrid fusion."""
    repo = db.get(Repository, repository_id)
    if repo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found")

    mode = search_mode.strip().lower()
    if mode not in VALID_SEARCH_MODES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "invalid_search_mode",
                "message": "search_mode must be exact, semantic, hybrid, rrf, or rerank",
            },
        )

    if support_level is not None and support_level.lower() not in {"deep", "generic", "skip"}:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "invalid_support_level",
                "message": "support_level must be deep, generic, or skip",
            },
        )

    snapshot = latest_ready_snapshot(db, repository_id)
    if snapshot is None:
        return ChunkSearchResponse(
            repository_id=repository_id,
            snapshot_id=None,
            query=q,
            total=0,
            limit=limit,
            offset=offset,
            search_mode=mode,
            hits=[],
        )

    ranked, total = search_chunks_ranked(
        db,
        snapshot_id=snapshot.id,
        query=q,
        search_mode=mode,
        language=language,
        path_prefix=path_prefix,
        support_level=support_level,
        chunk_type=chunk_type,
        extraction_method=extraction_method,
        parser_name=parser_name,
        llm_enriched=llm_enriched,
        validation_status=validation_status,
        limit=limit,
        offset=offset,
    )
    hits = [
        ChunkSearchHit(
            id=row.chunk.id,
            path=row.chunk.path,
            language=row.chunk.language,
            support_level=row.chunk.support_level,
            chunk_type=row.chunk.chunk_type,
            start_line=row.chunk.start_line,
            end_line=row.chunk.end_line,
            content=row.chunk.content,
            content_hash=row.chunk.content_hash,
            extraction_method=row.chunk.extraction_method,
            parser_name=row.chunk.parser_name,
            parser_version=row.chunk.parser_version,
            verified_deep=row.chunk.verified_deep,
            llm_enriched=row.chunk.llm_enriched,
            validation_status=row.chunk.validation_status,
            semantic_label=row.chunk.semantic_label,
            concise_summary=row.chunk.concise_summary,
            parent_context=row.chunk.parent_context,
            created_at=row.chunk.created_at,
            score=row.score,
            score_breakdown=row.score_breakdown,
        )
        for row in ranked
    ]
    return ChunkSearchResponse(
        repository_id=repository_id,
        snapshot_id=snapshot.id,
        query=q,
        total=total,
        limit=limit,
        offset=offset,
        search_mode=mode,
        hits=hits,
    )


@router.post(
    "/repositories/{repository_id}/ask",
    response_model=AskResponse,
)
def ask_repository(
    repository_id: UUID,
    body: AskRequest,
    db: Session = Depends(get_db),
) -> AskResponse:
    """Grounded Ask: retrieve → optional LLM answer → citation post-validation."""
    repo = db.get(Repository, repository_id)
    if repo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found")

    if body.support_level is not None and body.support_level.lower() not in {
        "deep",
        "generic",
        "skip",
    }:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "invalid_support_level",
                "message": "support_level must be deep, generic, or skip",
            },
        )

    snapshot = latest_ready_snapshot(db, repository_id)
    if snapshot is None:
        return AskResponse(
            repository_id=repository_id,
            snapshot_id=None,
            question=body.question.strip(),
            answer="No ready snapshot is available for this repository yet.",
            status="no_evidence",
            citations=[],
            evidence=[],
            analysis=None,
            validation=AskValidationEcho(ok=True, valid_count=0, dropped_count=0, errors=[]),
            notes=["no_ready_snapshot"],
        )

    result = run_ask(
        db,
        snapshot_id=snapshot.id,
        question=body.question,
        language=body.language,
        path_prefix=body.path_prefix,
        support_level=body.support_level,
        apply_rerank=body.apply_rerank,
        expand=body.expand,
    )

    citations = [
        AskCitation(
            path=c.path,
            start_line=c.start_line,
            end_line=c.end_line,
            chunk_id=c.chunk_id,
            valid=c.valid,
            reason=c.reason,
            raw=c.raw,
        )
        for c in result.validation.valid_citations
    ]
    evidence = [
        AskEvidenceItem(
            chunk_id=u.chunk.id,
            path=u.chunk.path,
            start_line=u.chunk.start_line,
            end_line=u.chunk.end_line,
            support_level=u.chunk.support_level,
            role=u.role,
            depth=u.depth,
            citation=citation_key(u.chunk.path, u.chunk.start_line, u.chunk.end_line),
        )
        for u in result.context.units
    ]
    analysis = AskAnalysisEcho(
        kind=str(result.analysis.kind),
        rewrite_applied=result.analysis.rewrite_applied,
        retrieval_queries=list(result.analysis.retrieval_queries),
        identifiers=list(result.analysis.identifiers),
        paths=list(result.analysis.paths),
    )
    validation = AskValidationEcho(
        ok=result.validation.ok,
        valid_count=len(result.validation.valid_citations),
        dropped_count=len(result.validation.dropped),
        errors=list(result.validation.errors),
    )
    return AskResponse(
        repository_id=repository_id,
        snapshot_id=snapshot.id,
        question=result.question,
        answer=result.answer,
        status=result.status,
        citations=citations,
        evidence=evidence,
        analysis=analysis,
        validation=validation,
        context_depth=result.context.depth_used,
        context_tokens_used=result.context.tokens_used,
        context_token_budget=result.context.token_budget,
        ranked_chunk_ids=list(result.ranked_chunk_ids),
        model_provenance=result.model_provenance,
        cached=result.cached,
        notes=list(result.notes),
    )


@router.get("/jobs", response_model=list[IndexingJobRead])
def list_jobs(
    limit: int = 50,
    db: Session = Depends(get_db),
) -> list[IndexingJobRead]:
    capped = max(1, min(limit, 200))
    jobs = db.scalars(
        select(IndexingJob).order_by(IndexingJob.created_at.desc()).limit(capped)
    ).all()
    return [IndexingJobRead.model_validate(job) for job in jobs]


@router.get("/jobs/{job_id}", response_model=IndexingJobRead)
def get_job(job_id: UUID, db: Session = Depends(get_db)) -> IndexingJobRead:
    job = db.get(IndexingJob, job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return IndexingJobRead.model_validate(job)


@router.get("/repositories/{repository_id}/jobs", response_model=list[IndexingJobRead])
def list_repository_jobs(
    repository_id: UUID,
    db: Session = Depends(get_db),
) -> list[IndexingJobRead]:
    repo = db.get(Repository, repository_id)
    if repo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found")
    jobs = db.scalars(
        select(IndexingJob)
        .where(IndexingJob.repository_id == repo.id)
        .order_by(IndexingJob.created_at.desc())
    ).all()
    return [IndexingJobRead.model_validate(job) for job in jobs]


@router.post("/jobs/{job_id}/retry", response_model=IndexingJobRead)
def retry_job(job_id: UUID, db: Session = Depends(get_db)) -> IndexingJobRead:
    try:
        job = retry_indexing_job(db, job_id)
    except RepositoryImportError as exc:
        code = (
            status.HTTP_404_NOT_FOUND
            if exc.code == "job_not_found"
            else status.HTTP_409_CONFLICT
        )
        raise HTTPException(
            status_code=code,
            detail={"code": exc.code, "message": str(exc)},
        ) from exc
    return IndexingJobRead.model_validate(job)
