"""Root-cause regression tests: coverage-complete indexing + deployment routing.

Arbitrary filenames only — no product-repo hardcoding.
"""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest
from pydantic_settings import SettingsConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.models import Chunk, ChunkEmbedding, Repository, SnapshotStatus
from app.services.chunking import replace_chunks_for_snapshot
from app.services.chunking.config_chunking import chunk_json_source
from app.services.discovery import discover_repository
from app.services.embeddings import replace_embeddings_for_snapshot
from app.services.java_symbols import replace_java_symbols_for_snapshot
from app.services.js_ts_symbols import replace_js_ts_symbols_for_snapshot
from app.services.rag.evidence_policy import (
    is_deployment_query,
    normalize_repo_path,
    resolve_path_chunks,
)
from app.services.rag.pipeline import retrieve_ask_bundle
from app.services.rag.query_analysis import analyze_query
from app.services.snapshots import create_or_update_snapshot
from app.services.source_files import replace_source_files_for_snapshot
from app.services.symbols import replace_python_symbols_for_snapshot
from tests.conftest import requires_postgres

pytestmark = requires_postgres


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
    ask_prompt_version: str = "10.7-rca"
    ask_rerank_use_mock: bool = True
    ask_query_rewrite_enabled: bool = True
    ask_context_token_budget: int = 12_000
    ask_expand_seed_limit: int = 12
    llm_kill_switch: bool = False


def _patch(monkeypatch: pytest.MonkeyPatch, cfg: Settings) -> None:
    for mod in (
        "app.services.rag.answer",
        "app.services.rag.pipeline",
        "app.services.rag.candidates",
        "app.services.rag.rerank",
        "app.services.rag.query_analysis",
        "app.services.rag.context_expand",
    ):
        monkeypatch.setattr(f"{mod}.settings", cfg)


def _write(root: Path, files: dict[str, str]) -> None:
    for rel, body in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")


def _index(
    db: Session,
    root: Path,
    cfg: Settings,
    *,
    with_embeddings: bool = True,
    commit_sha: str | None = None,
    repo: Repository | None = None,
) -> tuple[Repository, object]:
    if repo is None:
        repo = Repository(
            host="github.com",
            owner_name="rca",
            name=f"fix-{uuid4().hex[:8]}",
            default_branch="main",
            clone_url="https://github.com/rca/fix.git",
        )
        db.add(repo)
        db.flush()
    snap = create_or_update_snapshot(
        db,
        repository_id=repo.id,
        branch="main",
        commit_sha=commit_sha or uuid4().hex[:12],
        file_count=0,
        status=SnapshotStatus.READY,
    )
    disc = discover_repository(root)
    replace_source_files_for_snapshot(db, snapshot_id=snap.id, discovery=disc)
    db.flush()
    replace_python_symbols_for_snapshot(db, snapshot_id=snap.id, repo_root=root)
    replace_js_ts_symbols_for_snapshot(db, snapshot_id=snap.id, repo_root=root)
    replace_java_symbols_for_snapshot(db, snapshot_id=snap.id, repo_root=root)
    db.flush()
    replace_chunks_for_snapshot(db, snapshot_id=snap.id, repo_root=root)
    db.flush()
    if with_embeddings:
        replace_embeddings_for_snapshot(db, snapshot_id=snap.id, cfg=cfg)
    db.commit()
    return repo, snap


def test_small_ts_config_gets_full_coverage_chunk(
    db_session: Session, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "repo"
    path = "configs/build_engine_47.ts"
    body = (
        'import { defineConfig } from "tool";\n'
        "\n"
        "export default defineConfig({\n"
        '  mode: "prod",\n'
        "});\n"
    )
    _write(root, {path: body, "package.json": '{"name":"x"}\n'})
    cfg = _AskSettings()
    _patch(monkeypatch, cfg)
    _repo, snap = _index(db_session, root, cfg)
    rows = list(
        db_session.scalars(
            select(Chunk).where(Chunk.snapshot_id == snap.id, Chunk.path == path)
        )
    )
    assert rows
    assert min(r.start_line for r in rows) == 1
    assert max(r.end_line for r in rows) == 5
    bundle = retrieve_ask_bundle(
        db_session, snapshot_id=snap.id, query=f"Walk through {path}", cfg=cfg
    )
    cov = next(c for c in bundle.file_coverage if c.get("path") == path)
    assert cov["coverage_complete"] is True
    assert cov["missing_ranges"] == []
    indexed = cov.get("indexed_line_range")
    assert indexed == [1, 5]


def test_json_manifest_preserves_opening_brace_line(
    db_session: Session, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "repo"
    path = "metadata/app_manifest_83.json"
    body = '{\n  "alpha": 1,\n  "beta": 2\n}\n'
    assert body[0] == "{"
    offline = chunk_json_source(source=body, path=path)
    assert min(c.start_line for c in offline) == 1
    _write(root, {path: body})
    cfg = _AskSettings()
    _patch(monkeypatch, cfg)
    _repo, snap = _index(db_session, root, cfg)
    rows = resolve_path_chunks(
        db_session, snapshot_id=snap.id, path_token=path, limit=None
    )
    assert min(r.start_line for r in rows) == 1
    bundle = retrieve_ask_bundle(
        db_session, snapshot_id=snap.id, query=f"Walk through {path}", cfg=cfg
    )
    cov = next(c for c in bundle.file_coverage if c.get("path") == path)
    assert cov["coverage_complete"] is True
    text = "\n".join(u.chunk.content for u in bundle.context.units if u.chunk.path == path)
    assert "{" in text.splitlines()[0] or text.lstrip().startswith("{")


def test_nested_dot_workflow_path_normalizes() -> None:
    raw = ".automation/workflows/release_site_29.yml"
    assert normalize_repo_path(raw) == raw
    assert not normalize_repo_path(raw).startswith("automation/")


def test_multi_file_flow_retrieves_all_explicit_paths(
    db_session: Session, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "repo"
    files = {
        "shell.html": "<!doctype html><script type=\"module\" src=\"/client_bootstrap_47.ts\"></script>\n",
        "client_bootstrap_47.ts": 'export const boot = () => "ok";\n',
        "RootShell91.tsx": "export function RootShell91() { return null; }\n",
        "package.json": '{"name":"flow"}\n',
    }
    _write(root, files)
    cfg = _AskSettings()
    _patch(monkeypatch, cfg)
    _repo, snap = _index(db_session, root, cfg)
    q = "Trace shell.html → client_bootstrap_47.ts → RootShell91.tsx"
    analysis = analyze_query(q)
    assert "shell.html" in analysis.paths
    assert any("client_bootstrap_47.ts" in p for p in analysis.paths)
    assert any("RootShell91.tsx" in p for p in analysis.paths)
    bundle = retrieve_ask_bundle(db_session, snapshot_id=snap.id, query=q, cfg=cfg)
    assert bundle.exact_file_mode
    mandatory = set(bundle.mandatory_paths)
    assert any(p.endswith("shell.html") for p in mandatory)
    assert any("client_bootstrap_47.ts" in p for p in mandatory)
    assert any("RootShell91.tsx" in p for p in mandatory)
    for path in ("shell.html", "client_bootstrap_47.ts", "RootShell91.tsx"):
        cov = next((c for c in bundle.file_coverage if str(c.get("path", "")).endswith(path)), None)
        assert cov is not None
        assert cov.get("chunk_count", 0) >= 1 or cov.get("coverage_complete")


def test_deployment_query_prefers_workflow_over_ui_component(
    db_session: Session, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "repo"
    _write(
        root,
        {
            "README.md": "# Site\n",
            "package.json": '{"scripts":{"build":"vite build"}}\n',
            ".github/workflows/release_site_29.yml": (
                "name: Release\non:\n  push:\n    branches: [main]\n"
                "jobs:\n  deploy:\n    runs-on: ubuntu-latest\n"
                "    steps:\n      - run: npm run build\n"
            ),
            "src/components/HeroBanner.tsx": (
                "export function HeroBanner() { return <h1>Hello</h1>; }\n"
            ),
        },
    )
    assert is_deployment_query(
        "Explain exactly how a push to main becomes the live site"
    )
    cfg = _AskSettings()
    _patch(monkeypatch, cfg)
    _repo, snap = _index(db_session, root, cfg)
    bundle = retrieve_ask_bundle(
        db_session,
        snapshot_id=snap.id,
        query="Explain exactly how a push to main becomes the live production site",
        cfg=cfg,
    )
    paths = [r.chunk.path for r in bundle.ranked[:8]]
    assert any("workflows/" in p or p.endswith(".yml") for p in paths)
    # Workflow / manifest should outrank the UI component in the top set.
    top = paths[:4]
    assert any("workflow" in p or p.endswith("package.json") for p in top)
    assert not (len(top) == 1 and "HeroBanner" in top[0])


def test_github_pages_query_does_not_treat_github_as_symbol() -> None:
    a = analyze_query(
        "Explain exactly how a push to main becomes the live GitHub Pages site."
    )
    assert "GitHub" not in a.identifiers


def test_partial_symbol_file_still_gets_whole_file_coverage(
    db_session: Session, tmp_path: Path
) -> None:
    """Function-only symbol extraction must not leave import lines uncovered."""
    root = tmp_path / "repo"
    path = "src/RootShell91.tsx"
    body = (
        'import "./styles.css";\n'
        "\n"
        "export function RootShell91() {\n"
        "  return null;\n"
        "}\n"
        "\n"
    )
    _write(root, {path: body, "package.json": '{"name":"x"}\n'})
    _repo, snap = _index(db_session, root, _AskSettings())
    rows = list(
        db_session.scalars(
            select(Chunk).where(Chunk.snapshot_id == snap.id, Chunk.path == path)
        )
    )
    assert min(r.start_line for r in rows) == 1
    assert max(r.end_line for r in rows) >= 5


def test_exact_file_works_without_embeddings(
    db_session: Session, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Exact-path resolution must not require embeddings."""
    root = tmp_path / "repo"
    path = "configs/no_embed_engine_11.ts"
    _write(
        root,
        {
            path: "export const FLAG = 11;\n",
            "package.json": '{"name":"x"}\n',
        },
    )
    cfg = _AskSettings()
    _patch(monkeypatch, cfg)
    _repo, snap = _index(db_session, root, cfg, with_embeddings=False)
    emb_n = db_session.scalars(
        select(ChunkEmbedding).where(ChunkEmbedding.snapshot_id == snap.id).limit(1)
    ).first()
    assert emb_n is None
    rows = resolve_path_chunks(
        db_session, snapshot_id=snap.id, path_token=path, limit=None
    )
    assert rows and rows[0].content.strip()
    bundle = retrieve_ask_bundle(
        db_session, snapshot_id=snap.id, query=f"Walk through {path}", cfg=cfg
    )
    assert bundle.exact_file_mode
    assert any(u.chunk.path == path for u in bundle.context.units)


def test_ask_uses_only_selected_snapshot(
    db_session: Session, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Two snapshots of the same path must not leak across Ask stages."""
    cfg = _AskSettings()
    _patch(monkeypatch, cfg)
    path = "configs/versioned_knob_3.ts"
    root_a = tmp_path / "a"
    root_b = tmp_path / "b"
    _write(root_a, {path: 'export const V = "snap-a-unique";\n', "package.json": "{}\n"})
    _write(root_b, {path: 'export const V = "snap-b-unique";\n', "package.json": "{}\n"})
    repo, snap_a = _index(db_session, root_a, cfg, commit_sha="aaaaaaaaaaaa")
    _repo, snap_b = _index(
        db_session, root_b, cfg, commit_sha="bbbbbbbbbbbb", repo=repo
    )
    assert snap_a.id != snap_b.id
    bundle_a = retrieve_ask_bundle(
        db_session, snapshot_id=snap_a.id, query=f"Walk through {path}", cfg=cfg
    )
    text_a = "\n".join(
        u.chunk.content for u in bundle_a.context.units if u.chunk.path == path
    )
    assert "snap-a-unique" in text_a
    assert "snap-b-unique" not in text_a
    for u in bundle_a.context.units:
        assert u.chunk.snapshot_id == snap_a.id


def test_exact_file_not_displaced_by_semantic_noise(
    db_session: Session, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "repo"
    target = "configs/build_engine_47.ts"
    _write(
        root,
        {
            target: "export const KEEP = 1;\n",
            "src/components/NoiseWidget.tsx": (
                "export function NoiseWidget() { return null; }\n"
            ),
            "README.md": "# noise\n" + ("lorem " * 200) + "\n",
            "package.json": '{"name":"x"}\n',
        },
    )
    cfg = _AskSettings()
    _patch(monkeypatch, cfg)
    _repo, snap = _index(db_session, root, cfg)
    bundle = retrieve_ask_bundle(
        db_session, snapshot_id=snap.id, query=f"Walk through {target}", cfg=cfg
    )
    assert bundle.exact_file_mode
    assert any(u.chunk.path == target for u in bundle.context.units)
    # Exact target must appear before unrelated semantic fillers in ranked list.
    ranked_paths = [r.chunk.path for r in bundle.ranked]
    assert target in ranked_paths
    assert ranked_paths.index(target) < ranked_paths.index("src/components/NoiseWidget.tsx") or (
        "src/components/NoiseWidget.tsx" not in ranked_paths
    )


@pytest.mark.parametrize(
    "rel_path,body",
    [
        (
            "pkg/service_alpha_9.py",
            "def service_alpha_9():\n    return 9\n",
        ),
        (
            "com/example/ServiceBeta9.java",
            "package com.example;\npublic class ServiceBeta9 { public int x() { return 9; } }\n",
        ),
        (
            "lib/gamma_util_9.ts",
            "export function gammaUtil9() { return 9; }\n",
        ),
    ],
)
def test_cross_ecosystem_exact_file_coverage(
    db_session: Session,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    rel_path: str,
    body: str,
) -> None:
    root = tmp_path / "repo"
    extras = {"README.md": "# x\n"}
    if rel_path.endswith(".py"):
        extras["pyproject.toml"] = '[project]\nname = "x"\n'
    elif rel_path.endswith(".java"):
        extras["pom.xml"] = "<project></project>\n"
    else:
        extras["package.json"] = '{"name":"x"}\n'
    _write(root, {rel_path: body, **extras})
    cfg = _AskSettings()
    _patch(monkeypatch, cfg)
    _repo, snap = _index(db_session, root, cfg)
    rows = list(
        db_session.scalars(
            select(Chunk).where(Chunk.snapshot_id == snap.id, Chunk.path == rel_path)
        )
    )
    assert rows
    assert min(r.start_line for r in rows) == 1
    bundle = retrieve_ask_bundle(
        db_session, snapshot_id=snap.id, query=f"Walk through {rel_path}", cfg=cfg
    )
    cov = next(c for c in bundle.file_coverage if c.get("path") == rel_path)
    assert cov["coverage_complete"] is True
    assert cov["missing_ranges"] == []
