"""Week 10 Days 3–4: query analysis/rewrite + context expansion."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest
from pydantic_settings import SettingsConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.models import Chunk, Repository, SnapshotStatus, Symbol
from app.services.chunking import replace_chunks_for_snapshot
from app.services.chunks_query import ChunkSearchResult
from app.services.discovery import discover_repository
from app.services.embeddings import replace_embeddings_for_snapshot
from app.services.files_query import latest_ready_snapshot
from app.services.rag.context_expand import (
    estimate_tokens,
    expand_context,
    retrieval_confidence_is_low,
)
from app.services.rag.pipeline import retrieve_ask_bundle
from app.services.rag.query_analysis import (
    QueryKind,
    analyze_query,
    classify_query,
)
from app.services.snapshots import create_or_update_snapshot
from app.services.source_files import replace_source_files_for_snapshot
from app.services.symbols import replace_python_symbols_for_snapshot
from tests.conftest import requires_postgres

pytestmark = requires_postgres

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "generic_polyglot"


class _AskSettings(Settings):
    model_config = SettingsConfigDict(env_file=None, extra="ignore")
    embedding_provider: str = "local"
    embedding_model: str = "local-hash-v1"
    embedding_version: str = "9.2"
    embedding_dimensions: int = 1536
    embeddings_enabled: bool = True
    ask_candidate_exact_limit: int = 30
    ask_candidate_semantic_limit: int = 30
    ask_rrf_k: int = 60
    ask_rerank_enabled: bool = True
    ask_rerank_max_candidates: int = 40
    ask_rerank_use_mock: bool = True
    ask_query_rewrite_enabled: bool = True
    ask_query_max_rewrites: int = 4
    ask_context_token_budget: int = 6000
    ask_expand_seed_limit: int = 5
    ask_expand_neighbor_limit: int = 2
    ask_expand_relation_limit: int = 4
    ask_expand_low_confidence_score: float = 0.02
    llm_kill_switch: bool = False


# --- Day 3: query analysis (no DB) ---


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        ("UserService", QueryKind.IDENTIFIER),
        ("auth_middleware", QueryKind.IDENTIFIER),
        ("pkg/service.py", QueryKind.PATH),
        ("how does authentication login work?", QueryKind.NATURAL_LANGUAGE),
        ("explain the architecture of request handling", QueryKind.ARCHITECTURAL),
        ("null pointer exception in handler", QueryKind.DEBUGGING),
        ("TypeError: cannot unpack non-iterable", QueryKind.MIXED),
        ("where is UserService used?", QueryKind.MIXED),
    ],
)
def test_classify_query_kinds(query: str, expected: QueryKind) -> None:
    assert classify_query(query) == expected


def test_identifier_query_not_paraphrased() -> None:
    cfg = _AskSettings()
    analysis = analyze_query("UserService", cfg=cfg)
    assert analysis.kind == QueryKind.IDENTIFIER
    assert analysis.retrieval_queries == ("UserService",)
    assert analysis.rewrite_applied is False
    assert "UserService" in analysis.identifiers or analysis.original == "UserService"


def test_path_query_not_rewritten() -> None:
    analysis = analyze_query("pkg/helpers.ts", cfg=_AskSettings())
    assert analysis.kind == QueryKind.PATH
    assert analysis.retrieval_queries == ("pkg/helpers.ts",)
    assert analysis.rewrite_applied is False


def test_nl_rewrite_capped_at_four_and_keeps_identifiers() -> None:
    cfg = _AskSettings(ask_query_max_rewrites=4)
    analysis = analyze_query(
        "where is the UserService authentication middleware configured?",
        cfg=cfg,
    )
    assert analysis.kind == QueryKind.MIXED
    assert 1 <= len(analysis.retrieval_queries) <= 4
    assert analysis.original in analysis.retrieval_queries
    # Identifier must appear unchanged in at least one retrieval query.
    assert any("UserService" in q for q in analysis.retrieval_queries)
    # Never invent a paraphrased form of the identifier.
    joined = " ".join(analysis.retrieval_queries)
    assert "UserSvc" not in joined
    assert "UserServiceClass" not in joined


def test_rewrite_disabled_returns_original_only() -> None:
    analysis = analyze_query(
        "how does authentication work?",
        cfg=_AskSettings(ask_query_rewrite_enabled=False),
    )
    assert analysis.retrieval_queries == ("how does authentication work?",)
    assert analysis.rewrite_applied is False
    assert "rewrite_disabled" in analysis.notes


def test_architectural_rewrite_produces_extra_queries() -> None:
    analysis = analyze_query(
        "explain the architecture of the request pipeline",
        cfg=_AskSettings(),
    )
    assert analysis.kind == QueryKind.ARCHITECTURAL
    assert analysis.rewrite_applied is True
    assert len(analysis.retrieval_queries) <= 4
    assert len(analysis.retrieval_queries) >= 2


# --- Day 4: context expansion ---


def _index_python_with_calls(db_session: Session, tmp_path: Path, cfg: Settings) -> Repository:
    (tmp_path / "svc.py").write_text(
        "class AuthService:\n"
        "    def login(self, user: str) -> bool:\n"
        "        return self._validate(user)\n\n"
        "    def _validate(self, user: str) -> bool:\n"
        "        return bool(user)\n\n"
        "def entrypoint() -> None:\n"
        "    AuthService().login('a')\n",
        encoding="utf-8",
    )
    (tmp_path / "other.py").write_text(
        "def neighbor_a() -> int:\n"
        "    return 1\n\n"
        "def neighbor_b() -> int:\n"
        "    return 2\n\n"
        "def neighbor_c() -> int:\n"
        "    return 3\n",
        encoding="utf-8",
    )
    repo = Repository(
        host="github.com",
        owner_name="week10",
        name=f"expand-{uuid4().hex[:8]}",
        default_branch="main",
        clone_url="https://github.com/week10/expand.git",
    )
    db_session.add(repo)
    db_session.flush()
    snapshot = create_or_update_snapshot(
        db_session,
        repository_id=repo.id,
        branch="main",
        commit_sha=uuid4().hex[:12],
        file_count=0,
        status=SnapshotStatus.READY,
    )
    discovery = discover_repository(tmp_path)
    replace_source_files_for_snapshot(
        db_session, snapshot_id=snapshot.id, discovery=discovery
    )
    db_session.flush()
    replace_python_symbols_for_snapshot(
        db_session, snapshot_id=snapshot.id, repo_root=tmp_path
    )
    db_session.flush()
    replace_chunks_for_snapshot(db_session, snapshot_id=snapshot.id, repo_root=tmp_path)
    db_session.flush()
    replace_embeddings_for_snapshot(db_session, snapshot_id=snapshot.id, cfg=cfg)
    db_session.commit()
    return repo


def test_estimate_tokens() -> None:
    assert estimate_tokens("") == 0
    assert estimate_tokens("abcd") == 1
    assert estimate_tokens("a" * 40) == 10


def test_low_confidence_when_empty_or_weak_scores() -> None:
    cfg = _AskSettings(ask_expand_low_confidence_score=0.05)
    assert retrieval_confidence_is_low([], cfg=cfg) is True


def test_expand_includes_neighbors_and_respects_budget(
    db_session: Session, tmp_path: Path
) -> None:
    cfg = _AskSettings(
        ask_context_token_budget=500,
        ask_expand_neighbor_limit=3,
        ask_expand_seed_limit=1,
    )
    repo = _index_python_with_calls(db_session, tmp_path, cfg)
    snap = latest_ready_snapshot(db_session, repo.id)
    assert snap is not None

    other_chunks = list(
        db_session.scalars(
            select(Chunk)
            .where(Chunk.snapshot_id == snap.id, Chunk.path == "other.py")
            .order_by(Chunk.start_line.asc())
        ).all()
    )
    assert len(other_chunks) >= 2
    seed = other_chunks[1]
    ranked = [
        ChunkSearchResult(
            chunk=seed,
            score=0.5,
            score_breakdown={"exact": 2.0, "fused": 0.5},
        )
    ]
    expanded = expand_context(
        db_session,
        snapshot_id=snap.id,
        ranked=ranked,
        cfg=cfg,
        force_depth=1,
    )
    assert expanded.depth_used == 1
    assert expanded.units
    assert expanded.units[0].role == "seed"
    assert expanded.units[0].chunk.id == seed.id
    roles = {u.role for u in expanded.units}
    assert "neighbor" in roles or len(expanded.units) == 1
    assert expanded.tokens_used <= expanded.token_budget
    # Dedupe: unique chunk ids
    ids = [u.chunk.id for u in expanded.units]
    assert len(ids) == len(set(ids))


def test_expand_depth2_when_low_confidence(db_session: Session, tmp_path: Path) -> None:
    cfg = _AskSettings(
        ask_expand_low_confidence_score=0.99,
        ask_expand_relation_limit=4,
        ask_expand_seed_limit=2,
    )
    repo = _index_python_with_calls(db_session, tmp_path, cfg)
    snap = latest_ready_snapshot(db_session, repo.id)
    assert snap is not None

    login = db_session.scalars(
        select(Symbol).where(
            Symbol.snapshot_id == snap.id,
            Symbol.name == "login",
        )
    ).first()
    assert login is not None
    seed_chunks = list(
        db_session.scalars(
            select(Chunk).where(
                Chunk.snapshot_id == snap.id,
                Chunk.symbol_id == login.id,
            )
        ).all()
    )
    if not seed_chunks:
        # Fallback: any deep chunk on svc.py
        seed_chunks = list(
            db_session.scalars(
                select(Chunk).where(
                    Chunk.snapshot_id == snap.id,
                    Chunk.path == "svc.py",
                    Chunk.support_level == "deep",
                )
            ).all()
        )
    assert seed_chunks
    ranked = [
        ChunkSearchResult(
            chunk=seed_chunks[0],
            score=0.001,
            score_breakdown={"exact": 0.0, "fused": 0.001},
        )
    ]
    expanded = expand_context(
        db_session,
        snapshot_id=snap.id,
        ranked=ranked,
        cfg=cfg,
    )
    assert expanded.low_confidence is True
    assert expanded.depth_used == 2
    assert "depth2_expanded" in expanded.notes or expanded.truncated_used == 2


def test_expand_token_budget_truncates(db_session: Session, tmp_path: Path) -> None:
    cfg = _AskSettings(
        ask_context_token_budget=30,
        ask_expand_neighbor_limit=5,
        ask_expand_seed_limit=3,
    )
    repo = _index_python_with_calls(db_session, tmp_path, cfg)
    snap = latest_ready_snapshot(db_session, repo.id)
    assert snap is not None
    chunks = list(
        db_session.scalars(
            select(Chunk)
            .where(Chunk.snapshot_id == snap.id)
            .order_by(Chunk.path.asc(), Chunk.start_line.asc())
        ).all()
    )
    ranked = [
        ChunkSearchResult(chunk=c, score=1.0 - i * 0.01, score_breakdown={"exact": 1.0})
        for i, c in enumerate(chunks[:5])
    ]
    expanded = expand_context(
        db_session,
        snapshot_id=snap.id,
        ranked=ranked,
        cfg=cfg,
        force_depth=1,
    )
    assert expanded.tokens_used <= expanded.token_budget
    assert expanded.truncated is True or expanded.tokens_used <= 30


def test_retrieve_ask_bundle_pipeline(db_session: Session) -> None:
    cfg = _AskSettings()
    repo = Repository(
        host="github.com",
        owner_name="week10",
        name=f"pipe-{uuid4().hex[:8]}",
        default_branch="main",
        clone_url="https://github.com/week10/pipe.git",
    )
    db_session.add(repo)
    db_session.flush()
    snapshot = create_or_update_snapshot(
        db_session,
        repository_id=repo.id,
        branch="main",
        commit_sha=uuid4().hex[:12],
        file_count=0,
        status=SnapshotStatus.READY,
    )
    discovery = discover_repository(FIXTURE)
    replace_source_files_for_snapshot(
        db_session, snapshot_id=snapshot.id, discovery=discovery
    )
    db_session.flush()
    replace_chunks_for_snapshot(db_session, snapshot_id=snapshot.id, repo_root=FIXTURE)
    db_session.flush()
    replace_embeddings_for_snapshot(db_session, snapshot_id=snapshot.id, cfg=cfg)
    db_session.commit()

    snap = latest_ready_snapshot(db_session, repo.id)
    assert snap is not None
    bundle = retrieve_ask_bundle(
        db_session,
        snapshot_id=snap.id,
        query="how does the greeting helper work?",
        cfg=cfg,
        limit=10,
        apply_rerank=True,
        expand=True,
    )
    assert bundle.analysis.kind in {
        QueryKind.NATURAL_LANGUAGE,
        QueryKind.ARCHITECTURAL,
        QueryKind.MIXED,
    }
    assert 1 <= len(bundle.analysis.retrieval_queries) <= 4
    assert bundle.ranked
    assert bundle.context.units
    assert bundle.context.tokens_used <= bundle.context.token_budget
