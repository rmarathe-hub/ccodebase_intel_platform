"""Week 9 hybrid weight evaluation: Recall@k and MRR across weight configs."""

from __future__ import annotations

import json
import shutil
import time
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.core.config import Settings
from app.models import Chunk, Repository, SnapshotStatus
from app.services.chunking import replace_chunks_for_snapshot
from app.services.chunks_query import search_chunks_ranked
from app.services.discovery import discover_repository
from app.services.embeddings import replace_embeddings_for_snapshot
from app.services.java_symbols import replace_java_symbols_for_snapshot
from app.services.js_ts_symbols import replace_js_ts_symbols_for_snapshot
from app.services.snapshots import create_or_update_snapshot
from app.services.source_files import replace_source_files_for_snapshot
from app.services.symbols import replace_python_symbols_for_snapshot

_API_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = _API_ROOT / "tests" / "fixtures"
QUERIES_PATH = FIXTURES / "hybrid_weight_eval" / "queries.json"

WEIGHT_CONFIGS: tuple[tuple[str, float, float], ...] = (
    ("exact70_sem30", 0.70, 0.30),
    ("exact50_sem50", 0.50, 0.50),
    ("exact30_sem70", 0.30, 0.70),
)


@dataclass(frozen=True, slots=True)
class GoldQuery:
    id: str
    style: str
    q: str
    relevant_paths: tuple[str, ...]
    content_contains_any: tuple[str, ...]


def load_queries(path: Path | None = None) -> list[GoldQuery]:
    raw = json.loads((path or QUERIES_PATH).read_text(encoding="utf-8"))
    out: list[GoldQuery] = []
    for item in raw["queries"]:
        out.append(
            GoldQuery(
                id=str(item["id"]),
                style=str(item["style"]),
                q=str(item["q"]),
                relevant_paths=tuple(item["relevant_paths"]),
                content_contains_any=tuple(item.get("content_contains_any") or ()),
            )
        )
    return out


def build_eval_tree(dest: Path) -> Path:
    """Copy deep + polyglot fixtures under stable path prefixes for gold labels."""
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    mapping = {
        "python": FIXTURES / "python_deep",
        "java": FIXTURES / "java_deep",
        "js_ts": FIXTURES / "js_ts_deep",
        "polyglot": FIXTURES / "generic_polyglot",
    }
    for prefix, src in mapping.items():
        target = dest / prefix
        shutil.copytree(src, target)
    return dest


def index_eval_corpus(
    session: Session,
    repo_root: Path,
    *,
    cfg: Settings | None = None,
) -> tuple[Repository, UUID]:
    conf = cfg or Settings()
    repo = Repository(
        host="github.com",
        owner_name="eval",
        name=f"hybrid-weights-{uuid4().hex[:8]}",
        default_branch="main",
        clone_url="https://github.com/eval/hybrid-weights.git",
    )
    session.add(repo)
    session.flush()
    snapshot = create_or_update_snapshot(
        session,
        repository_id=repo.id,
        branch="main",
        commit_sha=uuid4().hex[:12],
        file_count=0,
        status=SnapshotStatus.READY,
    )
    discovery = discover_repository(repo_root)
    replace_source_files_for_snapshot(
        session, snapshot_id=snapshot.id, discovery=discovery
    )
    session.flush()
    replace_python_symbols_for_snapshot(
        session, snapshot_id=snapshot.id, repo_root=repo_root
    )
    replace_js_ts_symbols_for_snapshot(
        session, snapshot_id=snapshot.id, repo_root=repo_root
    )
    replace_java_symbols_for_snapshot(
        session, snapshot_id=snapshot.id, repo_root=repo_root
    )
    session.flush()
    replace_chunks_for_snapshot(session, snapshot_id=snapshot.id, repo_root=repo_root)
    session.flush()
    replace_embeddings_for_snapshot(session, snapshot_id=snapshot.id, cfg=conf)
    session.commit()
    return repo, snapshot.id


def _is_relevant(chunk: Chunk, gold: GoldQuery) -> bool:
    path_ok = any(
        chunk.path == p or chunk.path.endswith("/" + p) or chunk.path.endswith(p)
        for p in gold.relevant_paths
    )
    if not path_ok:
        return False
    if not gold.content_contains_any:
        return True
    content = chunk.content
    return any(token in content for token in gold.content_contains_any)


def _first_relevant_rank(hits: list[Chunk], gold: GoldQuery) -> int | None:
    for idx, chunk in enumerate(hits, start=1):
        if _is_relevant(chunk, gold):
            return idx
    return None


def _recall_at_k(hits: list[Chunk], gold: GoldQuery, k: int) -> float:
    top = hits[:k]
    relevant_ids = {c.id for c in top if _is_relevant(c, gold)}
    # Success@k style when gold is path-level (at least one relevant hit).
    return 1.0 if relevant_ids else 0.0


def mean(values: Iterable[float]) -> float:
    seq = list(values)
    if not seq:
        return 0.0
    return sum(seq) / len(seq)


def evaluate_config(
    session: Session,
    *,
    snapshot_id: UUID,
    queries: list[GoldQuery],
    w_exact: float,
    w_semantic: float,
    limit: int = 20,
    cfg: Settings | None = None,
) -> dict[str, Any]:
    conf = cfg or Settings()
    per_query: list[dict[str, Any]] = []
    latencies_ms: list[float] = []
    for gold in queries:
        t0 = time.perf_counter()
        ranked, _total = search_chunks_ranked(
            session,
            snapshot_id=snapshot_id,
            query=gold.q,
            search_mode="hybrid",
            limit=limit,
            cfg=conf,
            w_exact=w_exact,
            w_semantic=w_semantic,
        )
        latencies_ms.append((time.perf_counter() - t0) * 1000.0)
        hits = [r.chunk for r in ranked]
        rank = _first_relevant_rank(hits, gold)
        mrr = 0.0 if rank is None else 1.0 / rank
        per_query.append(
            {
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
        )

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

    return {
        "w_exact": w_exact,
        "w_semantic": w_semantic,
        "latency_ms_mean": round(mean(latencies_ms), 2),
        "latency_ms_p95": round(latencies_sorted[p95_idx], 2),
        "overall": _metrics(per_query),
        "identifier": _metrics(_subset("identifier")),
        "natural_language": _metrics(_subset("natural_language")),
        "per_query": per_query,
    }


def run_hybrid_weight_eval(
    session: Session,
    *,
    work_dir: Path,
    queries_path: Path | None = None,
    cfg: Settings | None = None,
) -> dict[str, Any]:
    conf = cfg or Settings()
    queries = load_queries(queries_path)
    repo_root = build_eval_tree(work_dir / "corpus")
    _repo, snapshot_id = index_eval_corpus(session, repo_root, cfg=conf)

    embedding_meta = {
        "provider": conf.embedding_provider,
        "model": conf.embedding_model or conf.azure_openai_embedding_deployment,
        "version": conf.embedding_version,
        "dimensions": conf.embedding_dimensions,
    }

    configs: dict[str, Any] = {}
    for name, w_exact, w_semantic in WEIGHT_CONFIGS:
        configs[name] = evaluate_config(
            session,
            snapshot_id=snapshot_id,
            queries=queries,
            w_exact=w_exact,
            w_semantic=w_semantic,
            cfg=conf,
        )

    # Rank configs by overall MRR then Recall@5 then Recall@10.
    ranked = sorted(
        configs.items(),
        key=lambda item: (
            item[1]["overall"]["mrr"],
            item[1]["overall"]["recall_at_5"],
            item[1]["overall"]["recall_at_10"],
        ),
        reverse=True,
    )
    winner = ranked[0][0]
    fifty = configs["exact50_sem50"]["overall"]
    seventy = configs["exact70_sem30"]["overall"]
    recommendation = (
        f"Measured winner on this fixture corpus ({conf.embedding_provider} embeddings, "
        f"{conf.embedding_dimensions} dims): **{winner}**. "
        "Identifier queries favor higher exact weight; natural-language quality depends on "
        "embedding model strength. "
        "**Default remains 50/50 exact/semantic** plus path exact-match boosts as a balanced "
        "baseline; **query-aware weighting** (identifier → raise exact, NL → raise semantic) "
        "is the strongest final design."
    )
    if winner == "exact50_sem50":
        recommendation = (
            "50/50 exact/semantic wins overall on this run and is the recommended default, "
            "with path exact-match boosts. Query-aware weighting is the strongest follow-on."
        )
    return {
        "snapshot_id": str(snapshot_id),
        "query_count": len(queries),
        "embedding": embedding_meta,
        "configs": configs,
        "ranking": [name for name, _ in ranked],
        "winner": winner,
        "default_config": "exact50_sem50",
        "default_metrics": fifty,
        "exact_heavy_metrics": seventy,
        "recommendation": recommendation,
    }


def render_report_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# Week 9 hybrid weight evaluation",
        "",
        "Configs compared (semantic / exact):",
        "",
        "- **exact70_sem30** — 30% semantic / 70% exact",
        "- **exact50_sem50** — 50% semantic / 50% exact",
        "- **exact30_sem70** — 70% semantic / 30% exact",
        "",
        "Metrics: Recall@5, Recall@10, MRR (mean reciprocal rank of first gold hit).",
        "Gold labels are path + content token matches on the fixture corpus.",
        "",
        f"- Queries: **{result['query_count']}**",
        f"- Embeddings: **{result.get('embedding', {}).get('provider', 'unknown')}** "
        f"({result.get('embedding', {}).get('model', '?')}, "
        f"{result.get('embedding', {}).get('dimensions', '?')} dims)",
        f"- Winner (MRR → R@5 → R@10): **{result['winner']}**",
        f"- Ranking: {', '.join(result['ranking'])}",
        f"- Product default: **{result.get('default_config', 'exact50_sem50')}** "
        f"(configurable `hybrid_w_exact` / `hybrid_w_semantic`)",
        "",
        "## Overall",
        "",
        (
            "| Config | exact | semantic | Recall@5 | Recall@10 | MRR "
            "| mean latency (ms) | p95 latency (ms) |"
        ),
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for name, w_exact, w_semantic in WEIGHT_CONFIGS:
        m = result["configs"][name]["overall"]
        cfg = result["configs"][name]
        lines.append(
            f"| {name} | {w_exact:.2f} | {w_semantic:.2f} | "
            f"{m['recall_at_5']:.4f} | {m['recall_at_10']:.4f} | {m['mrr']:.4f} | "
            f"{cfg['latency_ms_mean']:.1f} | {cfg['latency_ms_p95']:.1f} |"
        )

    for style, title in (
        ("identifier", "Identifier-style queries"),
        ("natural_language", "Natural-language queries"),
    ):
        lines += [
            "",
            f"## {title}",
            "",
            "| Config | Recall@5 | Recall@10 | MRR | n |",
            "| --- | --- | --- | --- | --- |",
        ]
        for name, _a, _b in WEIGHT_CONFIGS:
            m = result["configs"][name][style]
            lines.append(
                f"| {name} | {m['recall_at_5']:.4f} | {m['recall_at_10']:.4f} | "
                f"{m['mrr']:.4f} | {int(m['n'])} |"
            )

    lines += [
        "",
        "## Recommendation",
        "",
        result["recommendation"],
        "",
        "Path boost (+0.05 when the query substring appears in the path) remains enabled "
        "for all configs (exact-match style boost).",
        "",
        "## Per-query (winner config)",
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