"""Week 10 Day 1: independent exact ∥ semantic pools + RRF merge."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings, settings
from app.models import Chunk
from app.services.chunks_query import (
    ChunkSearchResult,
    _chunk_filters,
    _distance_to_similarity,
    _escape_like,
    _path_boost,
    _query_vector,
    _semantic_rows,
)


def rrf_score(*, ranks: list[int | None], k: int) -> float:
    """Reciprocal Rank Fusion over 1-based ranks (None = not in that list)."""
    total = 0.0
    for rank in ranks:
        if rank is None or rank < 1:
            continue
        total += 1.0 / (float(k) + float(rank))
    return total


def retrieve_rrf_candidates(
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
    cfg: Settings | None = None,
    exact_pool_size: int | None = None,
    semantic_pool_size: int | None = None,
    rrf_k: int | None = None,
) -> tuple[list[ChunkSearchResult], int]:
    """Retrieve exact and semantic pools independently, merge with RRF + path boost.

    Does not call an LLM. Hybrid weighted fusion remains available via search_mode=hybrid.
    """
    conf = cfg or settings
    q = query.strip()
    if not q:
        return [], 0

    capped = max(1, min(limit, 200))
    start = max(0, offset)
    exact_n = max(1, exact_pool_size or conf.ask_candidate_exact_limit)
    semantic_n = max(1, semantic_pool_size or conf.ask_candidate_semantic_limit)
    k = max(1, rrf_k or conf.ask_rrf_k)

    filters = _chunk_filters(
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

    pattern = f"%{_escape_like(q)}%"
    exact_filters = [*filters, Chunk.content.ilike(pattern, escape="\\")]
    exact_chunks = list(
        session.scalars(
            select(Chunk)
            .where(*exact_filters)
            .order_by(Chunk.path.asc(), Chunk.start_line.asc(), Chunk.id.asc())
            .limit(exact_n)
        ).all()
    )
    exact_rank: dict[UUID, int] = {c.id: i for i, c in enumerate(exact_chunks, start=1)}

    semantic_rank: dict[UUID, int] = {}
    semantic_sim: dict[UUID, float] = {}
    semantic_dist: dict[UUID, float] = {}
    semantic_chunks: list[Chunk] = []
    query_vector = _query_vector(conf, q)
    if query_vector is not None:
        for i, (chunk, dist) in enumerate(
            _semantic_rows(
                session,
                query_vector=query_vector,
                filters=filters,
                snapshot_id=snapshot_id,
                conf=conf,
                fetch_limit=semantic_n,
            ),
            start=1,
        ):
            semantic_chunks.append(chunk)
            semantic_rank[chunk.id] = i
            semantic_sim[chunk.id] = _distance_to_similarity(dist)
            semantic_dist[chunk.id] = dist

    candidates: dict[UUID, Chunk] = {c.id: c for c in exact_chunks}
    for chunk in semantic_chunks:
        candidates.setdefault(chunk.id, chunk)

    if not candidates:
        return [], 0

    scored: list[ChunkSearchResult] = []
    for cid, chunk in candidates.items():
        er = exact_rank.get(cid)
        sr = semantic_rank.get(cid)
        base = rrf_score(ranks=[er, sr], k=k)
        path_score = _path_boost(q, chunk.path)
        fused = base + path_score
        breakdown: dict[str, float] = {
            "rrf": round(base, 6),
            "path_boost": path_score,
            "fused": round(fused, 6),
            "exact": 1.0 if er is not None else 0.0,
            "semantic": round(semantic_sim.get(cid, 0.0), 6),
            "rrf_k": float(k),
        }
        if er is not None:
            breakdown["exact_rank"] = float(er)
        if sr is not None:
            breakdown["semantic_rank"] = float(sr)
        if cid in semantic_dist:
            breakdown["cosine_distance"] = round(semantic_dist[cid], 6)
        scored.append(
            ChunkSearchResult(
                chunk=chunk,
                score=round(fused, 6),
                score_breakdown=breakdown,
            )
        )

    scored.sort(
        key=lambda r: (
            -(r.score or 0.0),
            r.chunk.path,
            r.chunk.start_line,
            str(r.chunk.id),
        )
    )
    total = len(scored)
    return scored[start : start + capped], total
