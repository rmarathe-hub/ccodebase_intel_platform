"""Compose Ask retrieval: analyze → route → RRF → priors → rerank → expand."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.config import Settings, settings
from app.models import SourceFile
from app.services.chunks_query import ChunkSearchResult
from app.services.rag.candidates import retrieve_rrf_candidates
from app.services.rag.context_expand import ExpandedContext, expand_context
from app.services.rag.evidence_policy import (
    EvidenceTier,
    apply_evidence_priors,
    build_path_retrieval_diagnostic,
    chunks_to_search_results,
    compute_file_coverage,
    is_deployment_query,
    is_exact_file_mode,
    is_onboarding_query,
    lookup_source_file,
    merge_routed_ahead,
    normalize_repo_path,
    resolve_deployment_chunks,
    resolve_onboarding_chunks,
    resolve_path_chunks,
    resolve_symbol_chunks,
    tier_boost,
)
from app.services.rag.query_analysis import QueryAnalysis, analyze_query
from app.services.rag.rerank import rerank_candidates


@dataclass(frozen=True, slots=True)
class AskRetrievalBundle:
    analysis: QueryAnalysis
    ranked: tuple[ChunkSearchResult, ...]
    context: ExpandedContext
    routing_notes: tuple[str, ...] = ()
    mandatory_paths: tuple[str, ...] = ()
    exact_file_mode: bool = False
    file_coverage: tuple[dict[str, Any], ...] = ()
    file_diagnostics: tuple[dict[str, Any], ...] = ()


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


def _route_mandatory_hits(
    session: Session,
    *,
    snapshot_id: UUID,
    analysis: QueryAnalysis,
) -> tuple[
    list[ChunkSearchResult],
    list[str],
    set[str],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    """Exact-file, symbol, and onboarding routing ahead of RRF."""
    routed: list[ChunkSearchResult] = []
    notes: list[str] = []
    mandatory_paths: set[str] = set()
    file_coverage: list[dict[str, Any]] = []
    file_diagnostics: list[dict[str, Any]] = []
    exact_mode = is_exact_file_mode(analysis.original, analysis)
    if exact_mode and analysis.paths:
        notes.append("exact_file_mode")

    for path_token in analysis.paths:
        chunks = resolve_path_chunks(
            session, snapshot_id=snapshot_id, path_token=path_token, limit=None
        )
        if not chunks:
            sf = lookup_source_file(
                session, snapshot_id=snapshot_id, path=path_token
            )
            if sf is None:
                base = PurePosixPath(path_token).name
                sf = session.scalars(
                    select(SourceFile)
                    .where(
                        SourceFile.snapshot_id == snapshot_id,
                        or_(
                            SourceFile.path.endswith("/" + base),
                            func.lower(SourceFile.path) == base.lower(),
                        ),
                    )
                    .order_by(SourceFile.path.asc())
                    .limit(1)
                ).first()
            if sf is not None:
                notes.append(f"file_indexed_no_chunks:{sf.path}")
                notes.append("retrieval_reason:exact_file_match")
                diag = build_path_retrieval_diagnostic(
                    session,
                    snapshot_id=snapshot_id,
                    path=sf.path,
                    chunks=[],
                    reason="exact_file_match_no_chunks",
                )
                file_diagnostics.append(diag)
                cov = compute_file_coverage([], source_file=sf)
                cov["requested_file"] = path_token
                file_coverage.append(cov)
                notes.append("coverage_partial")
            else:
                notes.append(f"file_missing:{path_token}")
                notes.append("retrieval_reason:file_not_indexed")
            continue

        path = chunks[0].path
        mandatory_paths.add(path)
        notes.append(f"file_routed:{path}:{len(chunks)}")
        notes.append("retrieval_reason:exact_file_match")
        token_norm = normalize_repo_path(path_token)
        if "/" not in token_norm and token_norm.lower() != path.lower():
            notes.append("retrieval_reason:basename_match")

        sf = lookup_source_file(session, snapshot_id=snapshot_id, path=path)
        cov = compute_file_coverage(chunks, source_file=sf)
        cov["requested_file"] = path_token
        file_coverage.append(cov)
        notes.append(
            "coverage_complete" if cov.get("coverage_complete") else "coverage_partial"
        )
        missing = cov.get("missing_ranges") or []
        if isinstance(missing, list) and missing:
            parts: list[str] = []
            for item in missing:
                if isinstance(item, (list, tuple)) and len(item) >= 2:
                    parts.append(f"{item[0]}-{item[1]}")
            if parts:
                notes.append(f"missing_ranges:{path}:{','.join(parts)}")

        diag = build_path_retrieval_diagnostic(
            session,
            snapshot_id=snapshot_id,
            path=path,
            chunks=chunks,
            reason="exact_file_match",
            coverage=cov,
        )
        file_diagnostics.append(diag)

        routed.extend(
            chunks_to_search_results(
                chunks,
                role_score=10.0 + tier_boost(EvidenceTier.EXACT_FILE),
                evidence_tier=EvidenceTier.EXACT_FILE,
                reason=f"file:{path_token}",
            )
        )

    for ident in analysis.identifiers:
        chunks, note = resolve_symbol_chunks(
            session, snapshot_id=snapshot_id, name=ident, limit=8
        )
        if note == "missing":
            notes.append(f"symbol_missing:{ident}")
            notes.append("retrieval_reason:symbol_missing")
            continue
        notes.append(f"symbol_routed:{ident}:{note}:{len(chunks)}")
        notes.append("retrieval_reason:symbol_match")
        for c in chunks:
            mandatory_paths.add(c.path)
        routed.extend(
            chunks_to_search_results(
                chunks,
                role_score=9.0 + tier_boost(EvidenceTier.SOURCE),
                evidence_tier=EvidenceTier.SOURCE,
                reason=f"symbol:{ident}:{note}",
            )
        )

    if is_onboarding_query(analysis.original, analysis):
        onboard, ecosystems, onboard_diag = resolve_onboarding_chunks(
            session, snapshot_id=snapshot_id
        )
        if ecosystems:
            notes.append(
                "onboarding_ecosystems:" + ",".join(e.value for e in ecosystems)
            )
        notes.extend(onboard_diag)
        if onboard:
            notes.append(f"onboarding_seeded:{len(onboard)}")
            notes.append("retrieval_reason:ecosystem_seed")
            for c in onboard:
                mandatory_paths.add(c.path)
            routed.extend(
                chunks_to_search_results(
                    onboard,
                    role_score=8.0 + tier_boost(EvidenceTier.README),
                    evidence_tier=EvidenceTier.README,
                    reason="onboarding",
                )
            )

    if is_deployment_query(analysis.original) and not analysis.paths:
        deploy_chunks, deploy_notes = resolve_deployment_chunks(
            session, snapshot_id=snapshot_id
        )
        notes.extend(deploy_notes)
        if deploy_chunks:
            notes.append("retrieval_reason:deployment_seed")
            for c in deploy_chunks:
                mandatory_paths.add(c.path)
            routed.extend(
                chunks_to_search_results(
                    deploy_chunks,
                    role_score=8.5 + tier_boost(EvidenceTier.CONFIG_WORKFLOW),
                    evidence_tier=EvidenceTier.CONFIG_WORKFLOW,
                    reason="deployment",
                )
            )

    return routed, notes, mandatory_paths, file_coverage, file_diagnostics


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
    """Full Ask retrieval with file/symbol routing and evidence-tier priors."""
    conf = cfg or settings
    analysis = analyze_query(query, cfg=conf)
    exact_mode = is_exact_file_mode(query, analysis)

    routed, routing_notes, mandatory_paths, file_coverage, file_diagnostics = (
        _route_mandatory_hits(session, snapshot_id=snapshot_id, analysis=analysis)
    )
    notes = list(routing_notes)
    prefer = {normalize_repo_path(p) for p in mandatory_paths}

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
    if exact_mode and routed:
        supplemental = [
            r
            for r in merged
            if normalize_repo_path(r.chunk.path) not in prefer
        ]
        tagged: list[ChunkSearchResult] = []
        for item in supplemental:
            bd = dict(item.score_breakdown or {})
            bd["semantic_match"] = 1.0
            tagged.append(
                ChunkSearchResult(
                    chunk=item.chunk, score=item.score, score_breakdown=bd
                )
            )
        merged = merge_routed_ahead(routed, tagged)
        notes.append("retrieval_reason:file_aggregation")
    else:
        merged = merge_routed_ahead(routed, merged)

    merged = apply_evidence_priors(
        merged, analysis=analysis, mandatory_paths=mandatory_paths
    )

    if apply_rerank:
        head = [r for r in merged if (r.score_breakdown or {}).get("exact_file_match")]
        tail = [r for r in merged if not (r.score_breakdown or {}).get("exact_file_match")]
        if exact_mode and head:
            if tail:
                reranked_tail = rerank_candidates(
                    tail, query=analysis.original, cfg=conf
                )
                merged = merge_routed_ahead(head, reranked_tail)
            else:
                merged = head
        else:
            reranked_tail = rerank_candidates(
                tail or merged, query=analysis.original, cfg=conf
            )
            if head:
                merged = merge_routed_ahead(head, reranked_tail)
            else:
                merged = reranked_tail

    if exact_mode and prefer:
        exact_hits = [
            r
            for r in merged
            if normalize_repo_path(r.chunk.path) in prefer
        ]
        other = [
            r
            for r in merged
            if normalize_repo_path(r.chunk.path) not in prefer
        ]
        other_cap = max(0, max(limit, conf.ask_rerank_max_candidates) - len(exact_hits))
        merged = exact_hits + other[:other_cap]
    else:
        merged = merged[: max(1, min(limit, conf.ask_rerank_max_candidates))]

    if expand:
        context = expand_context(
            session,
            snapshot_id=snapshot_id,
            ranked=merged,
            cfg=conf,
            prefer_paths=mandatory_paths or None,
            exact_file_mode=exact_mode and bool(mandatory_paths),
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
        routing_notes=tuple(notes),
        mandatory_paths=tuple(sorted(mandatory_paths)),
        exact_file_mode=exact_mode and bool(analysis.paths),
        file_coverage=tuple(file_coverage),
        file_diagnostics=tuple(file_diagnostics),
    )
