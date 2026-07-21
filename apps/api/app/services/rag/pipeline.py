"""Compose Day 1–4 Ask retrieval: analyze → multi-query RRF → rerank → expand."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import Settings, settings
from app.services.chunks_query import ChunkSearchResult
from app.services.rag.candidates import retrieve_rrf_candidates
from app.services.rag.context_expand import ExpandedContext, expand_context
from app.services.rag.query_analysis import QueryAnalysis, analyze_query
from app.services.rag.rerank import rerank_candidates


@dataclass(frozen=True, slots=True)
class AskRetrievalBundle:
    analysis: QueryAnalysis
    ranked: tuple[ChunkSearchResult, ...]
    context: ExpandedContext


def _merge_rrf_lists(
    lists: list[list[ChunkSearchResult]],
    *,
    k: int,
) -> list[ChunkSearchResult]:
    """Merge multiple RRF-ranked lists with another RRF pass (stable)."""
    if not lists:
        return []
    if len(lists) == 1:
        return lists[0]

    ranks: dict[UUID, list[int | None]] = {}
    chunks: dict[UUID, ChunkSearchResult] = {}
    for list_idx, ranked in enumerate(lists):
        for i, item in enumerate(ranked, start=1):
            cid = item.chunk.id
            chunks.setdefault(cid, item)
            slot = ranks.setdefault(cid, [None] * len(lists))
            slot[list_idx] = i

    scored: list[tuple[float, ChunkSearchResult]] = []
    for cid, rank_row in ranks.items():
        score = 0.0
        for rank in rank_row:
            if rank is not None:
                score += 1.0 / (float(k) + float(rank))
        base = chunks[cid]
        scored.append((score, base))

    scored.sort(
        key=lambda t: (
            -t[0],
            t[1].chunk.path,
            t[1].chunk.start_line,
            str(t[1].chunk.id),
        )
    )
    out: list[ChunkSearchResult] = []
    for score, base in scored:
        breakdown = dict(base.score_breakdown or {})
        breakdown["multi_query_rrf"] = round(score, 6)
        breakdown["fused"] = round(score + float(breakdown.get("path_boost", 0.0)), 6)
        out.append(
            ChunkSearchResult(
                chunk=base.chunk,
                score=round(score + float(breakdown.get("path_boost", 0.0)), 6),
                score_breakdown=breakdown,
            )
        )
    return out


def retrieve_ask_bundle(
    session: Session,
    *,
    snapshot_id: UUID,
    query: str,
    cfg: Settings | None = None,
    limit: int = 40,
    apply_rerank: bool = True,
    expand: bool = True,
    language: str | None = None,
    path_prefix: str | None = None,
    support_level: str | None = None,
) -> AskRetrievalBundle:
    """Full Day 1–4 pipeline without answer generation."""
    conf = cfg or settings
    analysis = analyze_query(query, cfg=conf)

    per_query: list[list[ChunkSearchResult]] = []
    for rq in analysis.retrieval_queries or (analysis.original,):
        ranked, _total = retrieve_rrf_candidates(
            session,
            snapshot_id=snapshot_id,
            query=rq,
            language=language,
            path_prefix=path_prefix,
            support_level=support_level,
            limit=max(limit, conf.ask_rerank_max_candidates),
            offset=0,
            cfg=conf,
        )
        per_query.append(ranked)

    merged = _merge_rrf_lists(per_query, k=conf.ask_rrf_k)
    if apply_rerank:
        merged = rerank_candidates(merged, query=analysis.original, cfg=conf)
    merged = merged[: max(1, min(limit, conf.ask_rerank_max_candidates))]

    if expand:
        context = expand_context(
            session,
            snapshot_id=snapshot_id,
            ranked=merged,
            cfg=conf,
        )
    else:
        context = ExpandedContext(
            units=(),
            depth_used=0,
            low_confidence=False,
            tokens_used=0,
            token_budget=conf.ask_context_token_budget,
            truncated=False,
            notes=("expand_skipped",),
        )

    return AskRetrievalBundle(
        analysis=analysis,
        ranked=tuple(merged),
        context=context,
    )
