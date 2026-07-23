"""Ask evidence-policy regressions (AeroDelay-style fixture).

Covers ranking tiers, exact-file routing/completeness, symbol routing,
onboarding seeds, plan demotion, and negative infra queries.
"""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest
from pydantic_settings import SettingsConfigDict
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.models import Repository, SnapshotStatus, Symbol
from app.services.chunking import replace_chunks_for_snapshot
from app.services.discovery import discover_repository
from app.services.embeddings import replace_embeddings_for_snapshot
from app.services.files_query import latest_ready_snapshot
from app.services.js_ts_symbols import replace_js_ts_symbols_for_snapshot
from app.services.rag.answer import _evidence_payload, run_ask
from app.services.rag.evidence_policy import (
    EvidenceTier,
    ProjectEcosystem,
    apply_evidence_priors,
    classify_evidence_path,
    detect_project_ecosystems,
    is_file_walk_query,
    is_onboarding_query,
)
from app.services.rag.pipeline import retrieve_ask_bundle
from app.services.rag.query_analysis import analyze_query
from app.services.snapshots import create_or_update_snapshot
from app.services.source_files import replace_source_files_for_snapshot
from app.services.symbols import replace_python_symbols_for_snapshot
from tests.conftest import requires_postgres

pytestmark = requires_postgres

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "ask_evidence_policy"
NODE_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "ask_onboarding_node"
GO_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "ask_onboarding_go"
EXACT_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "ask_exact_file"


def test_extract_paths_multidot_and_specials() -> None:
    from app.services.rag.query_analysis import analyze_query

    a = analyze_query("Explain vite.config.ts and why base is /")
    assert "vite.config.ts" in a.paths
    assert "config.ts" not in a.paths

    b = analyze_query("Walk through package.json and README")
    assert any(p.lower().endswith("package.json") or p == "package.json" for p in b.paths)
    assert any("README" in p for p in b.paths)


def test_exact_file_mode_retrieves_full_vite_config(
    db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    cfg = _AskSettings()
    _patch_settings(monkeypatch, cfg)
    repo = _index(db_session, cfg, fixture=EXACT_FIXTURE)
    snap = latest_ready_snapshot(db_session, repo.id)
    assert snap is not None

    q = "Walk through vite.config.ts from beginning to end"
    bundle = retrieve_ask_bundle(
        db_session, snapshot_id=snap.id, query=q, cfg=cfg
    )
    assert bundle.exact_file_mode
    assert any(n == "exact_file_mode" for n in bundle.routing_notes)
    assert any("vite.config.ts" in p for p in bundle.mandatory_paths)
    assert any(n.startswith("retrieval_reason:exact_file_match") for n in bundle.routing_notes)
    contents = "\n".join(
        u.chunk.content for u in bundle.context.units if "vite.config" in u.chunk.path
    )
    assert contents.strip()
    assert "base" in contents
    assert "defineConfig" in contents
    assert "import" in contents
    assert bundle.file_coverage
    cov = next(
        (c for c in bundle.file_coverage if "vite.config.ts" in str(c.get("path", ""))),
        None,
    )
    assert cov is not None
    assert cov.get("coverage_complete") is True
    assert cov.get("missing_ranges") in ([], None) or cov.get("missing_ranges") == []
    indexed = cov.get("indexed_line_range")
    assert indexed == [1, 9]
    assert any(d.get("retrieval_reason") == "exact_file_match" for d in bundle.file_diagnostics)


def test_exact_file_package_json_includes_opening_brace(
    db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    cfg = _AskSettings()
    _patch_settings(monkeypatch, cfg)
    repo = _index(db_session, cfg, fixture=EXACT_FIXTURE)
    snap = latest_ready_snapshot(db_session, repo.id)
    assert snap is not None

    bundle = retrieve_ask_bundle(
        db_session,
        snapshot_id=snap.id,
        query="Walk through package.json field by field",
        cfg=cfg,
    )
    assert bundle.exact_file_mode
    contents = "\n".join(
        u.chunk.content for u in bundle.context.units if u.chunk.path.endswith("package.json")
    )
    assert contents.lstrip().startswith("{")
    cov = next(
        (c for c in bundle.file_coverage if str(c.get("path", "")).endswith("package.json")),
        None,
    )
    assert cov is not None
    assert cov.get("coverage_complete") is True
    retrieved = cov.get("retrieved_line_ranges") or []
    assert retrieved
    assert retrieved[0][0] == 1
    missing = cov.get("missing_ranges") or []
    assert not any(m[0] == 1 for m in missing)


def test_merge_overlapping_chunks_dedupes_lines() -> None:
    from types import SimpleNamespace

    from app.services.rag.evidence_policy import assemble_file_lines

    c1 = SimpleNamespace(id="1", start_line=1, end_line=3, content="a\nb\nc")
    c2 = SimpleNamespace(id="2", start_line=2, end_line=4, content="b\nc\nd")
    text, stored, sent, trunc, covered = assemble_file_lines([c1, c2], max_chars=1000)
    assert text == "a\nb\nc\nd"
    assert not trunc
    assert stored == len(text)
    assert covered == [(1, 4)]


def test_coverage_reports_missing_ranges() -> None:
    from types import SimpleNamespace

    from app.services.rag.evidence_policy import compute_file_coverage

    chunks = [
        SimpleNamespace(
            path="x.py",
            start_line=1,
            end_line=10,
            language="python",
            support_level="deep",
        ),
        SimpleNamespace(
            path="x.py",
            start_line=20,
            end_line=30,
            language="python",
            support_level="deep",
        ),
    ]
    sf = SimpleNamespace(path="x.py", line_count=30, language="python", support_level="deep")
    cov = compute_file_coverage(chunks, source_file=sf)
    assert cov["coverage_complete"] is False
    assert [11, 19] in cov["missing_ranges"] or (11, 19) in {
        tuple(x) for x in cov["missing_ranges"]  # type: ignore[misc]
    }


class _AskSettings(Settings):
    model_config = SettingsConfigDict(env_file=None, extra="ignore")
    embedding_provider: str = "local"
    embedding_model: str = "local-hash-v1"
    embedding_version: str = "9.2"
    embedding_dimensions: int = 1536
    embeddings_enabled: bool = True
    ask_enabled: bool = True
    ask_use_mock: bool = True
    ask_cache_enabled: bool = False
    ask_prompt_version: str = "10.7-test"
    ask_rerank_use_mock: bool = True
    ask_query_rewrite_enabled: bool = True
    ask_query_max_rewrites: int = 4
    ask_context_token_budget: int = 12_000
    ask_expand_seed_limit: int = 8
    ask_expand_neighbor_limit: int = 6
    ask_rerank_max_candidates: int = 40
    llm_kill_switch: bool = False


def _patch_settings(monkeypatch: pytest.MonkeyPatch, cfg: Settings) -> None:
    for mod in (
        "app.services.rag.answer",
        "app.services.rag.pipeline",
        "app.services.rag.candidates",
        "app.services.rag.rerank",
        "app.services.rag.query_analysis",
        "app.services.rag.context_expand",
    ):
        monkeypatch.setattr(f"{mod}.settings", cfg)


def _index(
    db_session: Session,
    cfg: Settings | None = None,
    *,
    fixture: Path | None = None,
) -> Repository:
    conf = cfg or _AskSettings()
    root = fixture or FIXTURE
    repo = Repository(
        host="github.com",
        owner_name="ask-policy",
        name=f"aerodelay-fixture-{uuid4().hex[:8]}",
        default_branch="main",
        clone_url="https://github.com/ask-policy/aerodelay-fixture.git",
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
    discovery = discover_repository(root)
    replace_source_files_for_snapshot(
        db_session, snapshot_id=snapshot.id, discovery=discovery
    )
    db_session.flush()
    replace_python_symbols_for_snapshot(
        db_session, snapshot_id=snapshot.id, repo_root=root
    )
    replace_js_ts_symbols_for_snapshot(
        db_session, snapshot_id=snapshot.id, repo_root=root
    )
    db_session.flush()
    replace_chunks_for_snapshot(db_session, snapshot_id=snapshot.id, repo_root=root)
    db_session.flush()
    replace_embeddings_for_snapshot(db_session, snapshot_id=snapshot.id, cfg=conf)
    db_session.commit()
    return repo


def test_detect_project_ecosystems_by_manifests() -> None:
    node = detect_project_ecosystems(
        ["README.md", "package.json", "vite.config.ts", "src/App.tsx"]
    )
    assert ProjectEcosystem.NODE in node
    assert ProjectEcosystem.DATA_ENGINEERING not in node

    py = detect_project_ecosystems(
        ["README.md", "pyproject.toml", "src/pkg/service.py", "src/pkg/models.py"]
    )
    assert ProjectEcosystem.PYTHON in py

    java = detect_project_ecosystems(
        ["pom.xml", "src/main/java/com/example/App.java"]
    )
    assert ProjectEcosystem.JAVA in java

    go = detect_project_ecosystems(["go.mod", "cmd/hello/main.go", "internal/x.go"])
    assert ProjectEcosystem.GO in go

    rust = detect_project_ecosystems(["Cargo.toml", "src/lib.rs", "src/main.rs"])
    assert ProjectEcosystem.RUST in rust

    de = detect_project_ecosystems(
        [
            "README.md",
            "dbt/dbt_project.yml",
            "docker-compose.yml",
            "airflow/dags/etl.py",
            "dbt/models/intermediate/x.sql",
        ]
    )
    assert ProjectEcosystem.DATA_ENGINEERING in de
    # Plain docker-compose alone is not enough for DE.
    assert ProjectEcosystem.DATA_ENGINEERING not in detect_project_ecosystems(
        ["docker-compose.yml", "README.md"]
    )


def test_classify_evidence_tiers() -> None:
    assert classify_evidence_path("README.md") == EvidenceTier.README
    assert (
        classify_evidence_path("docs/ARCHITECTURE.md") == EvidenceTier.ARCHITECTURE
    )
    assert (
        classify_evidence_path(
            "dbt/models/intermediate/int_flights__weather_at_departure.sql"
        )
        == EvidenceTier.SOURCE
    )
    assert classify_evidence_path("docs/DAY1_CHECKLIST.md") == EvidenceTier.PLAN
    assert classify_evidence_path("docs/WEEK1_PLAN.md") == EvidenceTier.PLAN
    assert classify_evidence_path("docs/FLAGSHIP_PLAN.md") == EvidenceTier.PLAN
    assert (
        classify_evidence_path("docs/data_dictionary.md")
        == EvidenceTier.DATA_DICTIONARY
    )


def test_readme_walkthrough_routes_readme(
    db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    cfg = _AskSettings()
    _patch_settings(monkeypatch, cfg)
    repo = _index(db_session, cfg)
    snap = latest_ready_snapshot(db_session, repo.id)
    assert snap is not None

    q = "Walk through README.md section by section"
    assert is_file_walk_query(q)
    bundle = retrieve_ask_bundle(
        db_session, snapshot_id=snap.id, query=q, cfg=cfg, apply_rerank=True
    )
    assert any(n.startswith("file_routed:README.md") for n in bundle.routing_notes)
    assert "README.md" in bundle.mandatory_paths
    paths = [u.chunk.path for u in bundle.context.units]
    assert any(p.endswith("README.md") for p in paths)
    # Plans must not dominate README walkthrough evidence.
    top_paths = [r.chunk.path for r in bundle.ranked[:5]]
    assert not any("CHECKLIST" in p or "_PLAN" in p for p in top_paths[:2])


def test_exact_sql_columns_aggregated_full_content(
    db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    cfg = _AskSettings()
    _patch_settings(monkeypatch, cfg)
    repo = _index(db_session, cfg)
    snap = latest_ready_snapshot(db_session, repo.id)
    assert snap is not None

    q = "What SQL columns are produced by int_flights__weather_at_departure.sql?"
    result = run_ask(db_session, snapshot_id=snap.id, question=q, cfg=cfg)
    assert result.status in {"ok", "partial"}
    assert result.evidence_diagnostics
    sql_diag = [
        d
        for d in result.evidence_diagnostics
        if "int_flights__weather_at_departure.sql" in str(d.get("path") or "")
    ]
    assert sql_diag
    assert any(d.get("role") == "file_aggregate" for d in sql_diag)
    assert all(not d.get("content_truncated") for d in sql_diag)

    # Full SELECT list must reach the LLM payload (regression for 900-char clip).
    bundle = retrieve_ask_bundle(
        db_session, snapshot_id=snap.id, query=q, cfg=cfg
    )
    payload, diags = _evidence_payload(
        bundle.context.units,
        mandatory_paths=bundle.mandatory_paths,
        file_walk=True,
    )
    sql_items = [
        e
        for e in payload
        if "int_flights__weather_at_departure.sql" in e["path"]
    ]
    assert sql_items
    joined = "\n".join(e["content"] for e in sql_items)
    for col in (
        "flight_id",
        "origin",
        "dest",
        "dep_time_utc",
        "station_id",
        "temp_c",
        "wind_speed_knots",
        "precip_1hr_inches",
        "weather_obs_lag_minutes",
        "weather_match_status",
    ):
        assert col in joined
    assert all(not e["content_truncated"] for e in sql_items)
    assert any(
        d.get("chars_sent", 0) >= d.get("chars_stored", 0)
        for d in diags
        if "weather_at_departure" in str(d.get("path"))
    )


def test_weather_match_status_symbol_and_values(
    db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    cfg = _AskSettings()
    _patch_settings(monkeypatch, cfg)
    repo = _index(db_session, cfg)
    snap = latest_ready_snapshot(db_session, repo.id)
    assert snap is not None

    sym = (
        db_session.query(Symbol)
        .filter(Symbol.snapshot_id == snap.id, Symbol.name == "weather_match_status")
        .first()
    )
    assert sym is not None

    q = "What are the accepted values for weather_match_status?"
    bundle = retrieve_ask_bundle(
        db_session, snapshot_id=snap.id, query=q, cfg=cfg
    )
    assert any("symbol_routed:weather_match_status" in n for n in bundle.routing_notes)
    contents = "\n".join(u.chunk.content for u in bundle.context.units)
    for value in (
        "no_obs_in_window",
        "matched_near",
        "matched_window",
        "matched_far",
    ):
        assert value in contents


def test_onboarding_reading_order_seeds_core_files(
    db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    cfg = _AskSettings()
    _patch_settings(monkeypatch, cfg)
    repo = _index(db_session, cfg)
    snap = latest_ready_snapshot(db_session, repo.id)
    assert snap is not None

    q = "I'm a new engineer — what reading order should I use to onboard?"
    assert is_onboarding_query(q)
    bundle = retrieve_ask_bundle(
        db_session, snapshot_id=snap.id, query=q, cfg=cfg
    )
    assert any(n.startswith("onboarding_seeded:") for n in bundle.routing_notes)
    eco_notes = [n for n in bundle.routing_notes if n.startswith("onboarding_ecosystems:")]
    assert eco_notes
    assert "data_engineering" in eco_notes[0]
    mandatory = set(bundle.mandatory_paths)
    assert "README.md" in mandatory
    assert "docs/ARCHITECTURE.md" in mandatory
    assert "docker-compose.yml" in mandatory
    assert any("dbt_project.yml" in p for p in mandatory)
    top = [r.chunk.path for r in bundle.ranked[:8]]
    assert any(p.endswith("README.md") for p in top)
    # Plans stay behind core onboarding anchors.
    plan_ranks = [
        i
        for i, p in enumerate(top)
        if "CHECKLIST" in p or "_PLAN" in p or "FLAGSHIP" in p
    ]
    readme_ranks = [i for i, p in enumerate(top) if p.endswith("README.md")]
    if plan_ranks and readme_ranks:
        assert min(readme_ranks) < min(plan_ranks)


def test_onboarding_node_ecosystem_seeds_package_and_src(
    db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    cfg = _AskSettings()
    _patch_settings(monkeypatch, cfg)
    repo = _index(db_session, cfg, fixture=NODE_FIXTURE)
    snap = latest_ready_snapshot(db_session, repo.id)
    assert snap is not None

    bundle = retrieve_ask_bundle(
        db_session,
        snapshot_id=snap.id,
        query="Explain this repository from start to finish as if taking ownership tomorrow",
        cfg=cfg,
    )
    eco_notes = [n for n in bundle.routing_notes if n.startswith("onboarding_ecosystems:")]
    assert eco_notes and "node" in eco_notes[0]
    assert "data_engineering" not in eco_notes[0]
    mandatory = set(bundle.mandatory_paths)
    assert "README.md" in mandatory
    assert "package.json" in mandatory
    assert "vite.config.ts" in mandatory
    assert "src/main.tsx" in mandatory or any(p.endswith("main.tsx") for p in mandatory)
    assert "src/App.tsx" in mandatory or any(p.endswith("App.tsx") for p in mandatory)
    assert any("Hero" in p or "components/" in p for p in mandatory)
    # Workflow may be present but must not be the only seed.
    workflow_paths = [p for p in mandatory if "workflows/" in p]
    assert len(mandatory) > len(workflow_paths)
    assert any(n.startswith("onboarding_selected:") for n in bundle.routing_notes)
    assert any(n.startswith("onboarding_category_counts:") for n in bundle.routing_notes)
    assert not any("dbt_project.yml" in p for p in mandatory)
    assert not any(p.endswith("docker-compose.yml") for p in mandatory)

def test_onboarding_go_ecosystem_seeds_gomod_and_cmd(
    db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    cfg = _AskSettings()
    _patch_settings(monkeypatch, cfg)
    repo = _index(db_session, cfg, fixture=GO_FIXTURE)
    snap = latest_ready_snapshot(db_session, repo.id)
    assert snap is not None

    bundle = retrieve_ask_bundle(
        db_session,
        snapshot_id=snap.id,
        query="Where should I start reading this repository?",
        cfg=cfg,
    )
    eco_notes = [n for n in bundle.routing_notes if n.startswith("onboarding_ecosystems:")]
    assert eco_notes and "go" in eco_notes[0]
    mandatory = set(bundle.mandatory_paths)
    assert "README.md" in mandatory
    assert "go.mod" in mandatory
    assert any(p.startswith("cmd/") for p in mandatory)


def test_role_ranking_prefers_data_engineering_over_plans(
    db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    cfg = _AskSettings()
    _patch_settings(monkeypatch, cfg)
    repo = _index(db_session, cfg)
    snap = latest_ready_snapshot(db_session, repo.id)
    assert snap is not None

    q = "What is the strongest role fit for this repository — data engineering or ML?"
    bundle = retrieve_ask_bundle(
        db_session, snapshot_id=snap.id, query=q, cfg=cfg
    )
    ranked_paths = [r.chunk.path for r in bundle.ranked]
    # Shipped DE sources / README / architecture before FLAGSHIP / WEEK plans.
    def _first_idx(pred) -> int:
        for i, p in enumerate(ranked_paths):
            if pred(p):
                return i
        return 10_000

    de_idx = min(
        _first_idx(lambda p: p.endswith("README.md")),
        _first_idx(lambda p: "ARCHITECTURE" in p),
        _first_idx(lambda p: p.endswith(".sql")),
        _first_idx(lambda p: "airflow" in p or "ingestion" in p),
    )
    plan_idx = min(
        _first_idx(lambda p: "FLAGSHIP_PLAN" in p),
        _first_idx(lambda p: "WEEK1_PLAN" in p),
        _first_idx(lambda p: "DAY1_CHECKLIST" in p),
    )
    assert de_idx < plan_idx

    result = run_ask(db_session, snapshot_id=snap.id, question=q, cfg=cfg)
    lower = result.answer.lower()
    # Mock answer cites retrieved evidence lines; README states DE core.
    assert "data engineering" in lower or "readme" in lower


def test_negative_kubernetes_redis_demotes_plans(
    db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    cfg = _AskSettings()
    _patch_settings(monkeypatch, cfg)
    repo = _index(db_session, cfg)
    snap = latest_ready_snapshot(db_session, repo.id)
    assert snap is not None

    q = "Does this repository use Kubernetes or Redis in production?"
    result = run_ask(db_session, snapshot_id=snap.id, question=q, cfg=cfg)
    assert "negative_infra_query" in result.notes
    bundle = retrieve_ask_bundle(
        db_session, snapshot_id=snap.id, query=q, cfg=cfg
    )
    # Architecture/README explicitly say K8s/Redis are not in scope — prefer those.
    top5 = [r.chunk.path for r in bundle.ranked[:5]]
    assert not top5[0].endswith("FLAGSHIP_PLAN.md")


def test_missing_symbol_build_fct_flights(
    db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    cfg = _AskSettings()
    _patch_settings(monkeypatch, cfg)
    repo = _index(db_session, cfg)
    snap = latest_ready_snapshot(db_session, repo.id)
    assert snap is not None

    q = "Explain the function build_fct_flights"
    bundle = retrieve_ask_bundle(
        db_session, snapshot_id=snap.id, query=q, cfg=cfg
    )
    assert any("symbol_missing:build_fct_flights" in n for n in bundle.routing_notes)

    result = run_ask(db_session, snapshot_id=snap.id, question=q, cfg=cfg)
    notes = " ".join(result.notes)
    answer_l = result.answer.lower()
    assert (
        "build_fct_flights" in notes
        or "not found" in answer_l
        or "symbol_missing" in notes
    )


def test_no_plan_dominance_when_source_exists(
    db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    cfg = _AskSettings()
    _patch_settings(monkeypatch, cfg)
    repo = _index(db_session, cfg)
    snap = latest_ready_snapshot(db_session, repo.id)
    assert snap is not None

    q = "How does the weather join work in the dbt intermediate model?"
    analysis = analyze_query(q, cfg=cfg)
    bundle = retrieve_ask_bundle(
        db_session, snapshot_id=snap.id, query=q, cfg=cfg
    )
    ranked = apply_evidence_priors(
        list(bundle.ranked), analysis=analysis, mandatory_paths=set(bundle.mandatory_paths)
    )
    top3 = [r.chunk.path for r in ranked[:3]]
    assert any(p.endswith(".sql") or p.endswith(".py") for p in top3)
    assert not any(
        classify_evidence_path(p) == EvidenceTier.PLAN for p in top3
    )


def test_evidence_diagnostics_exposed_on_ask_result(
    db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    cfg = _AskSettings()
    _patch_settings(monkeypatch, cfg)
    repo = _index(db_session, cfg)
    snap = latest_ready_snapshot(db_session, repo.id)
    assert snap is not None

    result = run_ask(
        db_session,
        snapshot_id=snap.id,
        question="What SQL columns are produced by int_flights__weather_at_departure.sql?",
        cfg=cfg,
    )
    assert result.evidence_diagnostics
    sample = result.evidence_diagnostics[0]
    for key in (
        "chars_stored",
        "chars_sent",
        "content_truncated",
        "estimated_tokens_sent",
        "evidence_tier",
        "path",
    ):
        assert key in sample
