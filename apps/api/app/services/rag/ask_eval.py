"""Week 10 Day 7: Ask/RAG eval matrix (hybrid vs rewrite vs rerank vs full RAG)."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Literal
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import Settings
from app.models import Chunk
from app.services.chunks_query import ChunkSearchResult, search_chunks_ranked
from app.services.hybrid_weight_eval import (
    GoldQuery,
    _first_relevant_rank,
    _recall_at_k,
    build_eval_tree,
    index_eval_corpus,
    load_queries,
    mean,
)
from app.services.rag.answer import run_ask
from app.services.rag.candidates import retrieve_rrf_candidates
from app.services.rag.context_expand import estimate_tokens
from app.services.rag.pipeline import _merge_rrf_lists
from app.services.rag.query_analysis import analyze_query
from app.services.rag.rerank import rerank_candidates

AskMode = Literal["hybrid", "rewrite", "rerank", "full_rag"]

MODES: tuple[AskMode, ...] = ("hybrid", "rewrite", "rerank", "full_rag")

MODE_LABELS: dict[AskMode, str] = {
    "hybrid": "Hybrid retrieval only",
    "rewrite": "Query rewrite (≤4) + multi-query RRF",
    "rerank": "RRF + LLM/mock rerank (≤40)",
    "full_rag": "Full Ask (rewrite + rerank + expand + answer)",
}


def _retrieve_mode(
    session: Session,
    *,
    snapshot_id: UUID,
    query: str,
    mode: AskMode,
    cfg: Settings,
    limit: int = 20,
) -> tuple[list[ChunkSearchResult], dict[str, Any]]:
    """Return ranked hits + mode-specific extras (analysis, ask answer, etc.)."""
    extras: dict[str, Any] = {}

    if mode == "hybrid":
        ranked, _ = search_chunks_ranked(
            session,
            snapshot_id=snapshot_id,
            query=query,
            search_mode="hybrid",
            limit=limit,
            cfg=cfg,
        )
        return ranked, extras

    if mode == "rewrite":
        analysis = analyze_query(query, cfg=cfg)
        extras["analysis"] = {
            "kind": str(analysis.kind),
            "rewrite_applied": analysis.rewrite_applied,
            "retrieval_queries": list(analysis.retrieval_queries),
        }
        per_query: list[list[ChunkSearchResult]] = []
        for rq in analysis.retrieval_queries or (query,):
            ranked, _ = retrieve_rrf_candidates(
                session,
                snapshot_id=snapshot_id,
                query=rq,
                limit=max(limit, cfg.ask_rerank_max_candidates),
                cfg=cfg,
            )
            per_query.append(ranked)
        merged = _merge_rrf_lists(per_query, k=cfg.ask_rrf_k)
        return merged[:limit], extras

    if mode == "rerank":
        ranked, _ = retrieve_rrf_candidates(
            session,
            snapshot_id=snapshot_id,
            query=query,
            limit=max(limit, cfg.ask_rerank_max_candidates),
            cfg=cfg,
        )
        reranked = rerank_candidates(ranked, query=query, cfg=cfg)
        return reranked[:limit], extras

    # full_rag: rewrite + rerank + expand + grounded answer (mock in CI)
    ask_cfg = cfg.model_copy(
        update={
            "ask_enabled": True,
            "ask_use_mock": True,
            "ask_cache_enabled": False,
            "ask_rerank_use_mock": True,
            "ask_query_rewrite_enabled": True,
        }
    )
    result = run_ask(
        session,
        snapshot_id=snapshot_id,
        question=query,
        cfg=ask_cfg,
        apply_rerank=True,
        expand=True,
    )
    valid_n = len(result.validation.valid_citations)
    dropped_n = len(result.validation.dropped)
    total_cites = valid_n + dropped_n
    citation_correctness = 1.0 if total_cites == 0 else valid_n / total_cites
    unsupported = (
        0.0
        if valid_n > 0 or result.status in {"no_evidence", "ask_disabled"}
        else 1.0
    )
    extras["ask"] = {
        "status": result.status,
        "validation_ok": result.validation.ok,
        "valid_citations": valid_n,
        "dropped_citations": dropped_n,
        "citation_correctness": citation_correctness,
        "unsupported_claim_rate": unsupported,
        "context_tokens": result.context.tokens_used,
        "answer_tokens_est": estimate_tokens(result.answer),
        "provider": (result.model_provenance or {}).get("provider"),
    }

    ranked_out: list[ChunkSearchResult] = []
    for i, cid in enumerate(result.ranked_chunk_ids[:limit], start=1):
        chunk = session.get(Chunk, cid)
        if chunk is None:
            continue
        ranked_out.append(
            ChunkSearchResult(chunk=chunk, score=1.0 / i, score_breakdown={"ask_rank": float(i)})
        )
    if not ranked_out:
        for i, unit in enumerate(result.context.units, start=1):
            if unit.role != "seed":
                continue
            ranked_out.append(
                ChunkSearchResult(
                    chunk=unit.chunk,
                    score=1.0 / i,
                    score_breakdown={"ask_rank": float(i)},
                )
            )
            if len(ranked_out) >= limit:
                break
    return ranked_out[:limit], extras


def evaluate_mode(
    session: Session,
    *,
    snapshot_id: UUID,
    queries: list[GoldQuery],
    mode: AskMode,
    limit: int = 20,
    cfg: Settings | None = None,
) -> dict[str, Any]:
    conf = cfg or Settings()
    per_query: list[dict[str, Any]] = []
    latencies_ms: list[float] = []
    citation_scores: list[float] = []
    unsupported_rates: list[float] = []
    token_estimates: list[float] = []

    for gold in queries:
        t0 = time.perf_counter()
        ranked, extras = _retrieve_mode(
            session,
            snapshot_id=snapshot_id,
            query=gold.q,
            mode=mode,
            cfg=conf,
            limit=limit,
        )
        latencies_ms.append((time.perf_counter() - t0) * 1000.0)
        hits = [r.chunk for r in ranked]
        rank = _first_relevant_rank(hits, gold)
        mrr = 0.0 if rank is None else 1.0 / rank
        row: dict[str, Any] = {
            "id": gold.id,
            "style": gold.style,
            "q": gold.q,
            "first_relevant_rank": rank,
            "mrr": round(mrr, 6),
            "recall_at_5": _recall_at_k(hits, gold, 5),
            "recall_at_10": _recall_at_k(hits, gold, 10),
            "latency_ms": round(latencies_ms[-1], 2),
            "top_paths": [h.path for h in hits[:5]],
        }
        ask = extras.get("ask")
        if ask is not None:
            row["citation_correctness"] = round(float(ask["citation_correctness"]), 4)
            row["unsupported_claim_rate"] = round(float(ask["unsupported_claim_rate"]), 4)
            row["context_tokens"] = ask["context_tokens"]
            row["answer_tokens_est"] = ask["answer_tokens_est"]
            citation_scores.append(float(ask["citation_correctness"]))
            unsupported_rates.append(float(ask["unsupported_claim_rate"]))
            token_estimates.append(
                float(ask["context_tokens"]) + float(ask["answer_tokens_est"])
            )
        if "analysis" in extras:
            row["rewrite_applied"] = extras["analysis"]["rewrite_applied"]
            row["retrieval_query_count"] = len(extras["analysis"]["retrieval_queries"])
        per_query.append(row)

    latencies_sorted = sorted(latencies_ms)
    p95_idx = max(0, int(len(latencies_sorted) * 0.95) - 1)

    def _subset(style: str | None) -> list[dict[str, Any]]:
        if style is None:
            return per_query
        return [r for r in per_query if r["style"] == style]

    def _metrics(rows: list[dict[str, Any]]) -> dict[str, float]:
        if not rows:
            return {"n": 0, "recall_at_5": 0.0, "recall_at_10": 0.0, "mrr": 0.0}
        return {
            "n": float(len(rows)),
            "recall_at_5": round(mean(r["recall_at_5"] for r in rows), 4),
            "recall_at_10": round(mean(r["recall_at_10"] for r in rows), 4),
            "mrr": round(mean(r["mrr"] for r in rows), 4),
        }

    out: dict[str, Any] = {
        "mode": mode,
        "label": MODE_LABELS[mode],
        "latency_ms_mean": round(mean(latencies_ms), 2),
        "latency_ms_p95": round(latencies_sorted[p95_idx], 2),
        "overall": _metrics(per_query),
        "identifier": _metrics(_subset("identifier")),
        "natural_language": _metrics(_subset("natural_language")),
        "per_query": per_query,
        "estimated_cost_usd": 0.0,
    }
    if citation_scores:
        out["citation_correctness_mean"] = round(mean(citation_scores), 4)
        out["unsupported_claim_rate_mean"] = round(mean(unsupported_rates), 4)
        out["tokens_est_mean"] = round(mean(token_estimates), 1)
    return out


def run_ask_eval(
    session: Session,
    *,
    work_dir: Path,
    queries_path: Path | None = None,
    cfg: Settings | None = None,
    modes: tuple[AskMode, ...] = MODES,
) -> dict[str, Any]:
    conf = cfg or Settings()
    queries = load_queries(queries_path)
    repo_root = build_eval_tree(work_dir / "corpus")
    _repo, snapshot_id = index_eval_corpus(session, repo_root, cfg=conf)

    configs: dict[str, Any] = {}
    for mode in modes:
        configs[mode] = evaluate_mode(
            session,
            snapshot_id=snapshot_id,
            queries=queries,
            mode=mode,
            cfg=conf,
        )

    ranked = sorted(
        configs.items(),
        key=lambda item: (
            item[1]["overall"]["mrr"],
            item[1]["overall"]["recall_at_5"],
            item[1]["overall"]["recall_at_10"],
            -item[1]["latency_ms_mean"],
        ),
        reverse=True,
    )
    winner = ranked[0][0]
    hybrid = configs["hybrid"]["overall"]
    full = configs.get("full_rag", {}).get("overall", {})

    keep_llm = False
    reasons: list[str] = []
    if "full_rag" in configs and "hybrid" in configs:
        if configs["full_rag"]["overall"]["mrr"] > hybrid["mrr"] + 0.02:
            keep_llm = True
            reasons.append("full_rag MRR improves over hybrid by >0.02.")
        if configs["full_rag"]["overall"]["recall_at_5"] > hybrid["recall_at_5"] + 0.02:
            keep_llm = True
            reasons.append("full_rag Recall@5 improves over hybrid by >0.02.")
        cite = configs["full_rag"].get("citation_correctness_mean")
        if cite is not None and cite >= 0.95:
            reasons.append(f"Citation correctness mean={cite}.")
        if not keep_llm:
            reasons.append(
                "LLM Ask path does not clearly beat hybrid on MRR/Recall@5 on this fixture; "
                "keep Ask opt-in for grounded NL answers, Search/hybrid for cheap lookup."
            )

    recommendation = (
        f"Retrieval winner on this fixture (mock Ask): **{winner}**. "
        + " ".join(reasons)
        + " Gate: keep the LLM Ask path only when it measurably improves retrieval or "
        "citation-validated answer quality."
    )

    return {
        "snapshot_id": str(snapshot_id),
        "query_count": len(queries),
        "embedding": {
            "provider": conf.embedding_provider,
            "model": conf.embedding_model,
            "dimensions": conf.embedding_dimensions,
        },
        "ask": {
            "use_mock": True,
            "rerank_use_mock": True,
        },
        "configs": configs,
        "ranking": [name for name, _ in ranked],
        "winner": winner,
        "keep_llm_path": keep_llm,
        "hybrid_baseline": hybrid,
        "full_rag_metrics": full,
        "recommendation": recommendation,
    }


def render_ask_eval_report(result: dict[str, Any]) -> str:
    lines = [
        "# Ask / RAG evaluation matrix",
        "",
        "Compares four retrieval/answer modes on the shared hybrid-weight gold fixture:",
        "",
        "1. **hybrid** — weighted exact∥semantic only",
        "2. **rewrite** — NL query rewrite (≤4) + multi-query RRF",
        "3. **rerank** — RRF + mock/LLM rerank (≤40)",
        "4. **full_rag** — rewrite + rerank + context expand + grounded Ask answer",
        "",
        "Metrics: Recall@5, Recall@10, MRR. Full RAG also reports citation correctness "
        "and unsupported-claim rate (mock answers over retrieved evidence).",
        "",
        f"- Queries: **{result['query_count']}**",
        f"- Embeddings: **{result.get('embedding', {}).get('provider', 'unknown')}** "
        f"({result.get('embedding', {}).get('model', '?')}, "
        f"{result.get('embedding', {}).get('dimensions', '?')} dims)",
        f"- Ask mock: **{result.get('ask', {}).get('use_mock', True)}**",
        f"- Winner (MRR → R@5 → R@10 → −latency): **{result['winner']}**",
        f"- Ranking: {', '.join(result['ranking'])}",
        f"- Keep LLM Ask path (gate): **{result.get('keep_llm_path')}**",
        "",
        "## Overall",
        "",
        (
            "| Mode | Recall@5 | Recall@10 | MRR | mean latency (ms) "
            "| p95 (ms) | cite OK | unsupported |"
        ),
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for mode in MODES:
        if mode not in result["configs"]:
            continue
        cfg = result["configs"][mode]
        m = cfg["overall"]
        cite = cfg.get("citation_correctness_mean")
        unsup = cfg.get("unsupported_claim_rate_mean")
        lines.append(
            f"| {mode} | {m['recall_at_5']:.4f} | {m['recall_at_10']:.4f} | "
            f"{m['mrr']:.4f} | {cfg['latency_ms_mean']:.1f} | {cfg['latency_ms_p95']:.1f} | "
            f"{'—' if cite is None else f'{cite:.4f}'} | "
            f"{'—' if unsup is None else f'{unsup:.4f}'} |"
        )

    for style, title in (
        ("identifier", "Identifier-style queries"),
        ("natural_language", "Natural-language queries"),
    ):
        lines += [
            "",
            f"## {title}",
            "",
            "| Mode | Recall@5 | Recall@10 | MRR | n |",
            "| --- | --- | --- | --- | --- |",
        ]
        for mode in MODES:
            if mode not in result["configs"]:
                continue
            m = result["configs"][mode][style]
            lines.append(
                f"| {mode} | {m['recall_at_5']:.4f} | {m['recall_at_10']:.4f} | "
                f"{m['mrr']:.4f} | {int(m['n'])} |"
            )

    lines += [
        "",
        "## Recommendation",
        "",
        result["recommendation"],
        "",
        "## Per-query (winner mode)",
        "",
        "| id | style | rank | MRR | R@5 | R@10 | top paths |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    winner_rows = result["configs"][result["winner"]]["per_query"]
    for row in winner_rows:
        rank = row["first_relevant_rank"]
        lines.append(
            f"| {row['id']} | {row['style']} | {rank if rank is not None else '—'} | "
            f"{row['mrr']:.4f} | {row['recall_at_5']:.0f} | {row['recall_at_10']:.0f} | "
            f"{', '.join(row['top_paths'][:3])} |"
        )
    lines.append("")
    return "\n".join(lines)
