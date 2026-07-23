"""Week 10 Day 4: deterministic context expansion with depth + token budget."""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings, settings
from app.models import Chunk, Symbol
from app.services.calls_query import list_callees_for_symbol, list_callers_for_symbol
from app.services.chunks_query import ChunkSearchResult
from app.services.rag.evidence_policy import normalize_repo_path


@dataclass(frozen=True, slots=True)
class ContextUnit:
    chunk: Chunk
    role: str  # seed | neighbor | caller | callee | related_symbol
    depth: int
    estimated_tokens: int
    source_seed_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class ExpandedContext:
    units: tuple[ContextUnit, ...]
    depth_used: int
    low_confidence: bool
    tokens_used: int
    token_budget: int
    truncated: bool
    notes: tuple[str, ...] = field(default_factory=tuple)


def estimate_tokens(text: str) -> int:
    """Cheap char-based token estimate (≈4 chars/token)."""
    if not text:
        return 0
    return max(1, (len(text) + 3) // 4)


def retrieval_confidence_is_low(
    results: list[ChunkSearchResult],
    *,
    cfg: Settings | None = None,
) -> bool:
    conf = cfg or settings
    if not results:
        return True
    top = results[0]
    score = float(top.score or 0.0)
    if score < conf.ask_expand_low_confidence_score:
        return True
    # Few exact hits among top seeds → weak lexical grounding.
    exactish = 0
    for r in results[:5]:
        bd = r.score_breakdown or {}
        if float(bd.get("exact", 0.0)) >= 1.0 or float(bd.get("exact_rank", 0.0)) > 0:
            exactish += 1
    if exactish == 0 and score < conf.ask_expand_low_confidence_score + 0.15:
        return True
    return False


def _neighbor_chunks(
    session: Session,
    *,
    seed: Chunk,
    limit: int,
) -> list[Chunk]:
    """Same-file chunks ordered by line distance to the seed span."""
    rows = list(
        session.scalars(
            select(Chunk)
            .where(
                Chunk.snapshot_id == seed.snapshot_id,
                Chunk.path == seed.path,
                Chunk.id != seed.id,
            )
            .order_by(Chunk.start_line.asc(), Chunk.id.asc())
            .limit(200)
        ).all()
    )
    def dist(c: Chunk) -> int:
        # Distance between ranges (0 if overlapping/adjacent).
        if c.end_line < seed.start_line:
            return seed.start_line - c.end_line
        if c.start_line > seed.end_line:
            return c.start_line - seed.end_line
        return 0

    rows.sort(key=lambda c: (dist(c), c.start_line, str(c.id)))
    return rows[:limit]


def _chunks_for_symbol(
    session: Session,
    *,
    snapshot_id: UUID,
    symbol_id: UUID,
    limit: int = 3,
) -> list[Chunk]:
    return list(
        session.scalars(
            select(Chunk)
            .where(
                Chunk.snapshot_id == snapshot_id,
                Chunk.symbol_id == symbol_id,
            )
            .order_by(Chunk.start_line.asc(), Chunk.id.asc())
            .limit(limit)
        ).all()
    )


def _related_symbol_ids_depth1(
    session: Session,
    *,
    snapshot_id: UUID,
    symbol: Symbol,
    limit: int,
) -> list[tuple[UUID, str]]:
    """Direct callers/callees as (symbol_id, role). Deep languages only."""
    out: list[tuple[UUID, str]] = []
    seen: set[UUID] = set()

    for call, _path in list_callers_for_symbol(
        session, snapshot_id=snapshot_id, symbol=symbol, limit=limit
    ):
        if call.caller_symbol_id and call.caller_symbol_id not in seen:
            seen.add(call.caller_symbol_id)
            out.append((call.caller_symbol_id, "caller"))

    for call, _path in list_callees_for_symbol(
        session, snapshot_id=snapshot_id, symbol_id=symbol.id, limit=limit
    ):
        # Best-effort: resolve callee via candidate qname when present.
        callee_id: UUID | None = None
        if call.candidate_qualified_name:
            callee = session.scalars(
                select(Symbol).where(
                    Symbol.snapshot_id == snapshot_id,
                    Symbol.qualified_name == call.candidate_qualified_name,
                )
            ).first()
            if callee is not None:
                callee_id = callee.id
        if callee_id and callee_id not in seen:
            seen.add(callee_id)
            out.append((callee_id, "callee"))
    return out[:limit]


def expand_context(
    session: Session,
    *,
    snapshot_id: UUID,
    ranked: list[ChunkSearchResult],
    cfg: Settings | None = None,
    force_depth: int | None = None,
    prefer_paths: set[str] | None = None,
    exact_file_mode: bool = False,
) -> ExpandedContext:
    """Assemble neighboring + call-graph context under a token budget.

    Depth 1 by default; depth 2 only when retrieval confidence is low (or forced).
    When ``prefer_paths`` is set, same-file neighbors for those paths are expanded
    more aggressively (exact-file / onboarding routing).
    In Exact File Mode, load ALL chunks for preferred paths before other expansion.
    """
    conf = cfg or settings
    budget = max(1, conf.ask_context_token_budget)
    seed_n = max(1, conf.ask_expand_seed_limit)
    neighbor_n = max(0, conf.ask_expand_neighbor_limit)
    relation_n = max(0, conf.ask_expand_relation_limit)
    prefer = {normalize_repo_path(p) for p in (prefer_paths or set())}

    low = retrieval_confidence_is_low(ranked, cfg=conf)
    if force_depth is not None:
        depth = 1 if force_depth <= 1 else 2
    else:
        depth = 2 if low else 1

    # Prefer mandatory-path hits as seeds when present.
    # Order prefer-path seeds by evidence tier so workflows cannot crowd out README/src.
    if prefer:
        from app.services.rag.evidence_policy import classify_evidence_path

        preferred_seeds = [
            r
            for r in ranked
            if normalize_repo_path(r.chunk.path) in prefer
        ]
        preferred_seeds.sort(
            key=lambda r: (
                int(classify_evidence_path(r.chunk.path)),
                r.chunk.path,
                r.chunk.start_line,
            )
        )
        other_seeds = [
            r
            for r in ranked
            if normalize_repo_path(r.chunk.path) not in prefer
        ]
        # Exact File Mode: keep ALL preferred-path chunks as seeds.
        if exact_file_mode:
            seeds = preferred_seeds + other_seeds[: max(0, seed_n)]
        else:
            seeds = (preferred_seeds + other_seeds)[:seed_n]
    else:
        seeds = ranked[:seed_n]
    units: list[ContextUnit] = []
    seen_chunk_ids: set[UUID] = set()
    tokens_used = 0
    truncated = False
    notes: list[str] = [f"depth={depth}", f"low_confidence={str(low).lower()}"]
    if prefer:
        notes.append(f"prefer_paths={len(prefer)}")
    if exact_file_mode:
        notes.append("exact_file_mode_expand")

    def try_add(
        chunk: Chunk,
        *,
        role: str,
        depth_val: int,
        source_seed_id: UUID | None,
    ) -> bool:
        nonlocal tokens_used, truncated
        if chunk.id in seen_chunk_ids:
            return True
        cost = estimate_tokens(chunk.content) + estimate_tokens(
            f"{chunk.path}:{chunk.start_line}-{chunk.end_line}"
        )
        if tokens_used + cost > budget:
            truncated = True
            return False
        seen_chunk_ids.add(chunk.id)
        tokens_used += cost
        units.append(
            ContextUnit(
                chunk=chunk,
                role=role,
                depth=depth_val,
                estimated_tokens=cost,
                source_seed_id=source_seed_id,
            )
        )
        return True

    # Seeds first (all exact-file chunks when in exact mode).
    for r in seeds:
        role = (
            "file_mandatory"
            if normalize_repo_path(r.chunk.path) in prefer
            else "seed"
        )
        if not try_add(r.chunk, role=role, depth_val=0, source_seed_id=r.chunk.id):
            break

    # Exact File Mode: pull any remaining same-file chunks not already seeded.
    if exact_file_mode and prefer and not truncated:
        for path in sorted(prefer):
            remaining = list(
                session.scalars(
                    select(Chunk)
                    .where(Chunk.snapshot_id == snapshot_id, Chunk.path == path)
                    .order_by(Chunk.start_line.asc(), Chunk.end_line.asc(), Chunk.id.asc())
                ).all()
            )
            for ch in remaining:
                if not try_add(
                    ch, role="file_mandatory", depth_val=0, source_seed_id=ch.id
                ):
                    notes.append(f"exact_file_budget_truncated:{path}")
                    break

    # Depth-1 expansion from seeds (more neighbors for preferred paths).
    frontier_symbol_ids: list[tuple[UUID, str, UUID]] = []  # symbol_id, role, seed_id
    for r in seeds:
        seed = r.chunk
        if truncated:
            break
        path_key = normalize_repo_path(seed.path)
        # In exact file mode preferred paths already loaded fully — skip neighbor fanout.
        if exact_file_mode and path_key in prefer:
            continue
        local_neighbor_n = max(neighbor_n, 24) if path_key in prefer else neighbor_n
        for nb in _neighbor_chunks(session, seed=seed, limit=local_neighbor_n):
            nb_role = "file_mandatory" if path_key in prefer else "neighbor"
            if not try_add(
                nb, role=nb_role, depth_val=1, source_seed_id=seed.id
            ):
                break
        if seed.symbol_id is None or seed.support_level != "deep":
            continue
        symbol = session.scalars(
            select(Symbol).where(
                Symbol.id == seed.symbol_id,
                Symbol.snapshot_id == snapshot_id,
            )
        ).first()
        if symbol is None:
            continue
        for sym_id, role in _related_symbol_ids_depth1(
            session, snapshot_id=snapshot_id, symbol=symbol, limit=relation_n
        ):
            frontier_symbol_ids.append((sym_id, role, seed.id))
            for ch in _chunks_for_symbol(
                session, snapshot_id=snapshot_id, symbol_id=sym_id, limit=2
            ):
                if not try_add(
                    ch, role=role, depth_val=1, source_seed_id=seed.id
                ):
                    break

    # Depth-2: one more hop from depth-1 related symbols (only when needed).
    if depth >= 2 and not truncated:
        notes.append("depth2_expanded")
        second: list[tuple[UUID, str, UUID]] = []
        for sym_id, _role, seed_id in frontier_symbol_ids:
            symbol = session.scalars(
                select(Symbol).where(
                    Symbol.id == sym_id,
                    Symbol.snapshot_id == snapshot_id,
                )
            ).first()
            if symbol is None:
                continue
            for nxt_id, nxt_role in _related_symbol_ids_depth1(
                session,
                snapshot_id=snapshot_id,
                symbol=symbol,
                limit=max(1, relation_n // 2),
            ):
                second.append((nxt_id, nxt_role, seed_id))
        for sym_id, role, seed_id in second:
            if truncated:
                break
            for ch in _chunks_for_symbol(
                session, snapshot_id=snapshot_id, symbol_id=sym_id, limit=1
            ):
                if not try_add(
                    ch, role=f"{role}_d2", depth_val=2, source_seed_id=seed_id
                ):
                    break

    return ExpandedContext(
        units=tuple(units),
        depth_used=depth,
        low_confidence=low,
        tokens_used=tokens_used,
        token_budget=budget,
        truncated=truncated,
        notes=tuple(notes),
    )
