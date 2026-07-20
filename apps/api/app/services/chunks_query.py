"""Chunk search: exact (LLM-independent), semantic (pgvector), hybrid fusion."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.core.config import Settings, settings
from app.models import Chunk, ChunkEmbedding
from app.services.embeddings.factory import get_embedding_provider
from app.services.embeddings.null_provider import NullEmbeddingProvider

VALID_SEARCH_MODES = frozenset({"exact", "semantic", "hybrid"})


@dataclass(frozen=True, slots=True)
class ChunkSearchResult:
    chunk: Chunk
    score: float | None
    score_breakdown: dict[str, float] | None


def _escape_like(term: str) -> str:
    return term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _chunk_filters(
    *,
    snapshot_id: UUID,
    language: str | None,
    path_prefix: str | None,
    support_level: str | None,
    chunk_type: str | None,
    extraction_method: str | None,
    parser_name: str | None,
    llm_enriched: bool | None,
    validation_status: str | None,
) -> list[object]:
    filters: list[object] = [Chunk.snapshot_id == snapshot_id]
    if language:
        filters.append(Chunk.language == language)
    if path_prefix:
        filters.append(Chunk.path.startswith(path_prefix))
    if support_level:
        filters.append(Chunk.support_level == support_level.lower())
    if chunk_type:
        filters.append(Chunk.chunk_type == chunk_type)
    if extraction_method:
        filters.append(Chunk.extraction_method == extraction_method)
    if parser_name:
        filters.append(Chunk.parser_name == parser_name)
    if llm_enriched is not None:
        filters.append(Chunk.llm_enriched.is_(llm_enriched))
    if validation_status:
        filters.append(Chunk.validation_status == validation_status)
    return filters


def search_chunks(
    session: Session,
    *,
    snapshot_id: UUID,
    query: str,
    language: str | None = None,
    path_prefix: str | None = None,
    support_level: str | None = None,
    chunk_type: str | None = None,
    extraction_method: str | None = None,
    parser_name: str | None = None,
    llm_enriched: bool | None = None,
    validation_status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[Chunk], int]:
    """Case-insensitive substring match on chunk content. No embeddings."""
    results, total = search_chunks_ranked(
        session,
        snapshot_id=snapshot_id,
        query=query,
        search_mode="exact",
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
    return [r.chunk for r in results], total


def search_chunks_ranked(
    session: Session,
    *,
    snapshot_id: UUID,
    query: str,
    search_mode: str = "exact",
    language: str | None = None,
    path_prefix: str | None = None,
    support_level: str | None = None,
    chunk_type: str | None = None,
    extraction_method: str | None = None,
    parser_name: str | None = None,
    llm_enriched: bool | None = None,
    validation_status: str | None = None,
    limit: int = 50,
    offset: int = 0,
    cfg: Settings | None = None,
) -> tuple[list[ChunkSearchResult], int]:
    """Search with exact | semantic | hybrid modes. Citations always from persisted chunks."""
    mode = (search_mode or "exact").strip().lower()
    if mode not in VALID_SEARCH_MODES:
        raise ValueError(f"invalid search_mode: {search_mode}")

    q = query.strip()
    if not q:
        return [], 0

    capped = max(1, min(limit, 200))
    start = max(0, offset)
    conf = cfg or settings
    base_filters = _chunk_filters(
        snapshot_id=snapshot_id,
        language=language,
        path_prefix=path_prefix,
        support_level=support_level,
        chunk_type=chunk_type,
        extraction_method=extraction_method,
        parser_name=parser_name,
        llm_enriched=llm_enriched,
        validation_status=validation_status,
    )

    if mode == "exact":
        return _exact_search(
            session,
            query=q,
            filters=base_filters,
            limit=capped,
            offset=start,
        )
    if mode == "semantic":
        return _semantic_search(
            session,
            query=q,
            filters=base_filters,
            snapshot_id=snapshot_id,
            limit=capped,
            offset=start,
            conf=conf,
        )
    return _hybrid_search(
        session,
        query=q,
        filters=base_filters,
        snapshot_id=snapshot_id,
        limit=capped,
        offset=start,
        conf=conf,
    )


def _exact_search(
    session: Session,
    *,
    query: str,
    filters: list[object],
    limit: int,
    offset: int,
) -> tuple[list[ChunkSearchResult], int]:
    pattern = f"%{_escape_like(query)}%"
    exact_filters = [*filters, Chunk.content.ilike(pattern, escape="\\")]
    count_stmt: Select[tuple[int]] = (
        select(func.count()).select_from(Chunk).where(*exact_filters)
    )
    total = int(session.scalar(count_stmt) or 0)
    rows = list(
        session.scalars(
            select(Chunk)
            .where(*exact_filters)
            .order_by(Chunk.path.asc(), Chunk.start_line.asc(), Chunk.id.asc())
            .offset(offset)
            .limit(limit)
        ).all()
    )
    return [
        ChunkSearchResult(
            chunk=row,
            score=1.0,
            score_breakdown={"exact": 1.0},
        )
        for row in rows
    ], total


def _query_vector(conf: Settings, query: str) -> list[float] | None:
    provider = get_embedding_provider(conf)
    if isinstance(provider, NullEmbeddingProvider) or provider.dimensions < 1:
        return None
    vectors = provider.embed_texts([query])
    if not vectors or len(vectors[0]) != conf.embedding_dimensions:
        return None
    return list(vectors[0])


def _semantic_rows(
    session: Session,
    *,
    query_vector: list[float],
    filters: list[object],
    snapshot_id: UUID,
    conf: Settings,
    fetch_limit: int,
) -> list[tuple[Chunk, float]]:
    """Return (chunk, cosine_distance) ascending by distance."""
    distance = ChunkEmbedding.embedding.cosine_distance(query_vector)
    stmt = (
        select(Chunk, distance.label("distance"))
        .join(ChunkEmbedding, ChunkEmbedding.chunk_id == Chunk.id)
        .where(
            *filters,
            ChunkEmbedding.snapshot_id == snapshot_id,
            ChunkEmbedding.embedding_model == conf.embedding_model,
            ChunkEmbedding.embedding_version == conf.embedding_version,
            ChunkEmbedding.dimensions == conf.embedding_dimensions,
        )
        .order_by(distance.asc(), Chunk.path.asc(), Chunk.start_line.asc(), Chunk.id.asc())
        .limit(fetch_limit)
    )
    rows = session.execute(stmt).all()
    out: list[tuple[Chunk, float]] = []
    for chunk, dist in rows:
        out.append((chunk, float(dist)))
    return out


def _distance_to_similarity(distance: float) -> float:
    # cosine_distance in [0, 2] typically; map to [0, 1] similarity.
    sim = 1.0 - distance
    if sim < 0.0:
        return 0.0
    if sim > 1.0:
        return 1.0
    return sim


def _semantic_search(
    session: Session,
    *,
    query: str,
    filters: list[object],
    snapshot_id: UUID,
    limit: int,
    offset: int,
    conf: Settings,
) -> tuple[list[ChunkSearchResult], int]:
    query_vector = _query_vector(conf, query)
    if query_vector is None:
        return [], 0

    # Count matching embedded chunks (same filters).
    count_stmt = (
        select(func.count())
        .select_from(Chunk)
        .join(ChunkEmbedding, ChunkEmbedding.chunk_id == Chunk.id)
        .where(
            *filters,
            ChunkEmbedding.snapshot_id == snapshot_id,
            ChunkEmbedding.embedding_model == conf.embedding_model,
            ChunkEmbedding.embedding_version == conf.embedding_version,
            ChunkEmbedding.dimensions == conf.embedding_dimensions,
        )
    )
    total = int(session.scalar(count_stmt) or 0)
    if total == 0:
        return [], 0

    fetch = offset + limit
    ranked = _semantic_rows(
        session,
        query_vector=query_vector,
        filters=filters,
        snapshot_id=snapshot_id,
        conf=conf,
        fetch_limit=fetch,
    )
    page = ranked[offset : offset + limit]
    results = [
        ChunkSearchResult(
            chunk=chunk,
            score=round(_distance_to_similarity(dist), 6),
            score_breakdown={
                "semantic": round(_distance_to_similarity(dist), 6),
                "cosine_distance": round(dist, 6),
            },
        )
        for chunk, dist in page
    ]
    return results, total


def _path_boost(query: str, path: str) -> float:
    q = query.lower()
    p = path.lower()
    if q and q in p:
        return 0.05
    return 0.0


def _hybrid_search(
    session: Session,
    *,
    query: str,
    filters: list[object],
    snapshot_id: UUID,
    limit: int,
    offset: int,
    conf: Settings,
) -> tuple[list[ChunkSearchResult], int]:
    """Fuse exact substring + semantic similarity with stable tie-break."""
    pattern = f"%{_escape_like(query)}%"
    exact_filters = [*filters, Chunk.content.ilike(pattern, escape="\\")]
    exact_chunks = list(
        session.scalars(
            select(Chunk)
            .where(*exact_filters)
            .order_by(Chunk.path.asc(), Chunk.start_line.asc(), Chunk.id.asc())
            .limit(500)
        ).all()
    )
    exact_ids = {c.id for c in exact_chunks}

    query_vector = _query_vector(conf, query)
    semantic_by_id: dict[UUID, tuple[Chunk, float]] = {}
    if query_vector is not None:
        for chunk, dist in _semantic_rows(
            session,
            query_vector=query_vector,
            filters=filters,
            snapshot_id=snapshot_id,
            conf=conf,
            fetch_limit=500,
        ):
            semantic_by_id[chunk.id] = (chunk, dist)

    # Candidate universe: exact ∪ semantic
    candidates: dict[UUID, Chunk] = {c.id: c for c in exact_chunks}
    for cid, (chunk, _) in semantic_by_id.items():
        candidates.setdefault(cid, chunk)

    if not candidates:
        return [], 0

    w_exact = 0.45
    w_semantic = 0.55
    scored: list[ChunkSearchResult] = []
    for cid, chunk in candidates.items():
        exact_score = 1.0 if cid in exact_ids else 0.0
        if cid in semantic_by_id:
            semantic_score = _distance_to_similarity(semantic_by_id[cid][1])
            cosine_distance = semantic_by_id[cid][1]
        else:
            semantic_score = 0.0
            cosine_distance = None
        path_score = _path_boost(query, chunk.path)
        fused = w_exact * exact_score + w_semantic * semantic_score + path_score
        breakdown: dict[str, float] = {
            "exact": exact_score,
            "semantic": round(semantic_score, 6),
            "path_boost": path_score,
            "fused": round(fused, 6),
        }
        if cosine_distance is not None:
            breakdown["cosine_distance"] = round(cosine_distance, 6)
        scored.append(
            ChunkSearchResult(
                chunk=chunk,
                score=round(fused, 6),
                score_breakdown=breakdown,
            )
        )

    # Deterministic ordering: score desc, path, lines, id
    scored.sort(
        key=lambda r: (
            -(r.score or 0.0),
            r.chunk.path,
            r.chunk.start_line,
            str(r.chunk.id),
        )
    )
    total = len(scored)
    page = scored[offset : offset + limit]
    return page, total
