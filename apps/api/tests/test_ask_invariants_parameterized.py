"""Invariant-based Ask/chunking tests — no repository- or filename-specific branches.

Fixtures use arbitrary generated names. Assertions use metadata and content only.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest
from pydantic_settings import SettingsConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.language_contract import SupportLevel
from app.models import Chunk, Repository, SnapshotStatus, SourceFile
from app.services.chunking import replace_chunks_for_snapshot
from app.services.chunking.config_chunking import physical_line_count
from app.services.discovery import discover_repository
from app.services.embeddings import replace_embeddings_for_snapshot
from app.services.files_query import latest_ready_snapshot
from app.services.java_symbols import replace_java_symbols_for_snapshot
from app.services.js_ts_symbols import replace_js_ts_symbols_for_snapshot
from app.services.rag.evidence_policy import (
    ProjectEcosystem,
    assemble_file_lines,
    compute_file_coverage,
    detect_project_ecosystems,
    normalize_repo_path,
    resolve_onboarding_chunks,
    resolve_path_chunks,
)
from app.services.rag.pipeline import retrieve_ask_bundle
from app.services.rag.query_analysis import analyze_query
from app.services.snapshots import create_or_update_snapshot
from app.services.source_files import replace_source_files_for_snapshot
from app.services.symbols import replace_python_symbols_for_snapshot
from tests.conftest import requires_postgres

pytestmark = requires_postgres


# ---------------------------------------------------------------------------
# Arbitrary generated paths (must not match implementation hardcodes)
# ---------------------------------------------------------------------------

_WHOLE_FILE_CASES: list[tuple[str, str, str]] = [
    # path, content, expected_language_family (for reporting)
    ("lib/service_kernel_82.py", "VALUE = 41\nOTHER = 42\n", "python"),
    (
        "ui/client_bootstrap_47.ts",
        'export default { mode: "boot", port: 9 };\n',
        "typescript",
    ),
    (
        "ui/widget_factory_63.js",
        "export default function factory() { return 1; }\n",
        "javascript",
    ),
    (
        "src/main/java/com/acme/RuntimeGateway91.java",
        "package com.acme;\n// no type body\n",
        "java",
    ),
    (
        "cfg/settings_bundle_33.toml",
        "[alpha]\nkey = \"value\"\n",
        "toml",
    ),
    (
        "nested/.pipeline/build_release_19.yml",
        "stage: release\nsteps:\n  - run: echo ok\n",
        "yaml",
    ),
    (
        "data/matrix_payload_55.json",
        '{\n  "alpha": 1,\n  "beta": 2\n}\n',
        "json",
    ),
    (
        "notes/overview_letter_12.md",
        "Plain prose without any markdown heading lines.\nSecond line.\n",
        "markdown",
    ),
    (
        "assets/theme_tokens_28.css",
        ".root { color: #111; }\n",
        "css",
    ),
    (
        "db/rollup_query_44.sql",
        "SELECT 1 AS n;\n",
        "sql",
    ),
    (
        "scripts/warm_cache_71.sh",
        "#!/usr/bin/env bash\necho warm\n",
        "shell",
    ),
    # Extensionless but discovery-special (LICENSE) — not a product filename hardcode.
    (
        "LICENSE",
        "Permission is hereby granted for testing.\nLine two.\n",
        "extensionless",
    ),
]


_DOT_PATHS = [
    ".github/workflows/ship_artifact_88.yml",
    ".github/workflows/nested/deep_job_03.yaml",
    ".pipeline/build_release_19.yml",
    "./.hidden_tooling/run_once_14.sh",
]


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
    ask_prompt_version: str = "10.7-invariant"
    ask_rerank_use_mock: bool = True
    ask_query_rewrite_enabled: bool = True
    ask_query_max_rewrites: int = 2
    ask_context_token_budget: int = 12_000
    ask_expand_seed_limit: int = 12
    ask_expand_neighbor_limit: int = 4
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


def _write_tree(root: Path, files: dict[str, str]) -> None:
    for rel, body in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")


def _physical_lines(text: str) -> int:
    return physical_line_count(text)


def _index_tree(
    db_session: Session,
    root: Path,
    *,
    cfg: Settings | None = None,
    with_embeddings: bool = False,
) -> Repository:
    conf = cfg or _AskSettings()
    repo = Repository(
        host="github.com",
        owner_name="invariant",
        name=f"gen-{uuid4().hex[:10]}",
        default_branch="main",
        clone_url="https://github.com/invariant/gen.git",
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
    replace_java_symbols_for_snapshot(
        db_session, snapshot_id=snapshot.id, repo_root=root
    )
    db_session.flush()
    replace_chunks_for_snapshot(db_session, snapshot_id=snapshot.id, repo_root=root)
    db_session.flush()
    if with_embeddings:
        replace_embeddings_for_snapshot(
            db_session, snapshot_id=snapshot.id, cfg=conf
        )
        db_session.flush()
    db_session.commit()
    return repo


# ---------------------------------------------------------------------------
# 1–2. Whole-file fallback when parsers emit zero chunks
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "relpath,content,family",
    _WHOLE_FILE_CASES,
    ids=[c[2] + ":" + Path(c[0]).name for c in _WHOLE_FILE_CASES],
)
def test_zero_parser_chunks_get_exactly_one_whole_file_fallback(
    db_session: Session,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    relpath: str,
    content: str,
    family: str,
) -> None:
    """Invariant: non-skip indexed text with empty parser output → one 1..N chunk."""
    root = tmp_path / "repo"
    _write_tree(root, {relpath: content})

    # Force empty parser output so the safety net is the only producer.
    monkeypatch.setattr(
        "app.services.chunking.deep_chunks_from_symbols",
        lambda *a, **k: [],
    )
    monkeypatch.setattr(
        "app.services.chunking.collect_generic_chunks",
        lambda *a, **k: [],
    )

    repo = _index_tree(db_session, root)
    snap = latest_ready_snapshot(db_session, repo.id)
    assert snap is not None

    sf = db_session.scalars(
        select(SourceFile).where(
            SourceFile.snapshot_id == snap.id, SourceFile.path == relpath
        )
    ).first()
    assert sf is not None, f"{relpath} must be indexed"
    assert sf.support_level != SupportLevel.SKIP.value
    assert not sf.is_binary

    rows = list(
        db_session.scalars(
            select(Chunk).where(Chunk.snapshot_id == snap.id, Chunk.path == relpath)
        ).all()
    )
    assert len(rows) == 1, f"{family}/{relpath}: expected one fallback chunk"
    ch = rows[0]
    expected_end = _physical_lines(content)
    assert ch.start_line == 1
    assert ch.end_line == expected_end
    assert ch.extraction_method == "whole_file_fallback"
    phys = content.split("\n")
    if content.endswith("\n") and phys:
        phys = phys[:-1]
    assert phys
    assembled = (
        ch.content.split("\n")[:-1] if ch.content.endswith("\n") else ch.content.split("\n")
    )
    assert assembled[0] == phys[0]
    if len(assembled) >= len(phys):
        assert assembled[-1] == phys[-1]


# ---------------------------------------------------------------------------
# 3. Exact-file retrieval returns all chunks ordered by source position
# ---------------------------------------------------------------------------


def test_exact_file_retrieval_returns_all_chunks_in_source_order(
    db_session: Session, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "repo"
    payload = (
        "{\n"
        '  "zeta_field": 1,\n'
        '  "alpha_field": 2,\n'
        '  "mu_field": 3,\n'
        '  "omega_field": 4\n'
        "}\n"
    )
    path = "cfg/settings_bundle_33.json"
    _write_tree(root, {path: payload, "README.md": "# T\n"})
    cfg = _AskSettings()
    _patch_settings(monkeypatch, cfg)
    repo = _index_tree(db_session, root, cfg=cfg, with_embeddings=True)
    snap = latest_ready_snapshot(db_session, repo.id)
    assert snap is not None

    chunks = resolve_path_chunks(
        db_session, snapshot_id=snap.id, path_token=path, limit=None
    )
    assert len(chunks) >= 2
    starts = [c.start_line for c in chunks]
    assert starts == sorted(starts)
    assert all(c.path == path for c in chunks)

    bundle = retrieve_ask_bundle(
        db_session,
        snapshot_id=snap.id,
        query=f"Walk through {path} from beginning to end",
        cfg=cfg,
    )
    assert bundle.exact_file_mode
    assert path in bundle.mandatory_paths
    routed = [r.chunk for r in bundle.ranked if r.chunk.path == path]
    same = sorted(routed, key=lambda c: (c.start_line, c.end_line))
    assert [c.start_line for c in same] == sorted(c.start_line for c in same)
    cov = next(c for c in bundle.file_coverage if c.get("path") == path)
    assert cov["coverage_complete"] is True
    assert cov["missing_ranges"] == []
    assert cov["indexed_line_range"] == [1, _physical_lines(payload)]


# ---------------------------------------------------------------------------
# 4. Aggregation preserves first/last lines; removes only true overlap
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "chunks_spec,expected_text,expected_covered",
    [
        (
            [
                (1, 3, "L1\nL2\nL3"),
                (3, 5, "L3\nL4\nL5"),
            ],
            "L1\nL2\nL3\nL4\nL5",
            [(1, 5)],
        ),
        (
            [
                (1, 1, "ONLY"),
            ],
            "ONLY",
            [(1, 1)],
        ),
        (
            [
                (2, 3, "B\nC"),
                (1, 2, "A\nB"),
            ],
            "A\nB\nC",
            [(1, 3)],
        ),
    ],
    ids=["overlap_middle", "one_line", "out_of_order_seeds"],
)
def test_aggregation_preserves_edges_dedupes_overlap_only(
    chunks_spec: list[tuple[int, int, str]],
    expected_text: str,
    expected_covered: list[tuple[int, int]],
) -> None:
    chunks = [
        SimpleNamespace(
            id=str(i),
            start_line=s,
            end_line=e,
            content=body,
        )
        for i, (s, e, body) in enumerate(chunks_spec)
    ]
    text, _stored, _sent, trunc, covered = assemble_file_lines(chunks, max_chars=10_000)
    assert not trunc
    assert text == expected_text
    assert covered == expected_covered
    lines = text.split("\n")
    assert lines[0] == expected_text.split("\n")[0]
    assert lines[-1] == expected_text.split("\n")[-1]


# ---------------------------------------------------------------------------
# 5. Coverage from physical source ranges, not filename/parser
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "line_count,chunk_ranges,complete,missing",
    [
        (9, [(1, 9)], True, []),
        (9, [(2, 9)], False, [(1, 1)]),
        (25, [(1, 10), (11, 25)], True, []),
        (25, [(1, 10), (15, 25)], False, [(11, 14)]),
        (1, [(1, 1)], True, []),
    ],
    ids=["full", "missing_first", "adjacent", "gap", "one_line"],
)
def test_coverage_uses_physical_line_ranges(
    line_count: int,
    chunk_ranges: list[tuple[int, int]],
    complete: bool,
    missing: list[tuple[int, int]],
) -> None:
    path = f"arbitrary/file_{uuid4().hex[:6]}.txt"
    chunks = [
        SimpleNamespace(
            path=path,
            start_line=s,
            end_line=e,
            language="documentation",
            support_level="generic",
        )
        for s, e in chunk_ranges
    ]
    sf = SimpleNamespace(
        path=path,
        line_count=line_count,
        language="documentation",
        support_level="generic",
    )
    cov = compute_file_coverage(chunks, source_file=sf)
    assert cov["coverage_complete"] is complete
    assert cov["indexed_line_range"] == [1, line_count]
    assert [tuple(x) for x in cov["missing_ranges"]] == missing  # type: ignore[misc]


# ---------------------------------------------------------------------------
# 6. Dot-prefixed nested paths normalize without character loss
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("raw", _DOT_PATHS)
def test_dot_paths_normalize_without_character_loss(raw: str) -> None:
    got = normalize_repo_path(raw)
    assert not got.startswith("github/workflows")  # classic lstrip("./") bug
    if raw.startswith("./"):
        assert got == raw[2:].replace("\\", "/")
    else:
        assert got == raw.replace("\\", "/")
    # Dot segment of .github / .pipeline / .hidden must survive.
    assert got.startswith(".") or "/." in got


def test_dot_workflow_path_survives_index_and_onboarding_note(
    db_session: Session, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "repo"
    wf = ".github/workflows/ship_artifact_88.yml"
    _write_tree(
        root,
        {
            "README.md": "# Own\n",
            "package.json": '{"name":"x"}\n',
            wf: (
                "name: ship\non: push\njobs:\n  a:\n    runs-on: ubuntu-latest\n"
                "    steps:\n      - run: echo\n"
            ),
            "src/client_bootstrap_47.ts": "export const n = 1;\n",
        },
    )
    cfg = _AskSettings()
    _patch_settings(monkeypatch, cfg)
    repo = _index_tree(db_session, root, cfg=cfg, with_embeddings=True)
    snap = latest_ready_snapshot(db_session, repo.id)
    assert snap is not None
    chunks, ecos, notes = resolve_onboarding_chunks(db_session, snapshot_id=snap.id)
    selected = next(n for n in notes if n.startswith("onboarding_selected:"))
    assert wf in selected
    assert ProjectEcosystem.NODE in ecos
    assert any(c.path == wf for c in chunks)


# ---------------------------------------------------------------------------
# 7–8. Onboarding by ecosystem/category with unfamiliar filenames
# ---------------------------------------------------------------------------


def test_python_fixture_unfamiliar_names_onboards_by_ecosystem(
    db_session: Session, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "py_repo"
    _write_tree(
        root,
        {
            "README.md": "# Py kernel\n",
            "pyproject.toml": '[project]\nname = "kernel82"\nversion = "0.0.1"\n',
            "src/service_kernel_82.py": "def run():\n    return 82\n",
            "src/helpers_q9.py": "def help_x():\n    return 1\n",
            ".github/workflows/ship_artifact_88.yml": (
                "name: x\non: push\njobs:\n  j:\n    runs-on: ubuntu-latest\n"
                "    steps:\n      - run: echo\n"
            ),
        },
    )
    assert ProjectEcosystem.PYTHON in detect_project_ecosystems(
        ["README.md", "pyproject.toml", "src/service_kernel_82.py"]
    )
    cfg = _AskSettings()
    _patch_settings(monkeypatch, cfg)
    repo = _index_tree(db_session, root, cfg=cfg, with_embeddings=True)
    snap = latest_ready_snapshot(db_session, repo.id)
    assert snap is not None
    bundle = retrieve_ask_bundle(
        db_session,
        snapshot_id=snap.id,
        query="Explain this repository from start to finish as if taking ownership tomorrow",
        cfg=cfg,
    )
    eco = next(n for n in bundle.routing_notes if n.startswith("onboarding_ecosystems:"))
    assert "python" in eco
    mandatory = set(bundle.mandatory_paths)
    assert "README.md" in mandatory
    assert "pyproject.toml" in mandatory
    assert any(p.startswith("src/") and p.endswith(".py") for p in mandatory)
    assert any("service_kernel_82.py" in p for p in mandatory)
    selected = next(n for n in bundle.routing_notes if n.startswith("onboarding_selected:"))
    assert "README.md:docs" in selected or ":docs" in selected
    assert "pyproject.toml" in selected
    assert len(mandatory) > 1


def test_typescript_fixture_unfamiliar_names_onboards_by_ecosystem(
    db_session: Session, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "ts_repo"
    _write_tree(
        root,
        {
            "README.md": "# TS boot\n",
            "package.json": '{"name":"boot47","private":true}\n',
            "tsconfig.json": '{"compilerOptions":{"strict":true}}\n',
            "src/client_bootstrap_47.ts": "export const boot = () => 47;\n",
            "src/components/Panel_Z3.tsx": "export const Panel = () => null;\n",
            ".github/workflows/ship_artifact_88.yml": (
                "name: x\non: push\njobs:\n  j:\n    runs-on: ubuntu-latest\n"
                "    steps:\n      - run: echo\n"
            ),
        },
    )
    cfg = _AskSettings()
    _patch_settings(monkeypatch, cfg)
    repo = _index_tree(db_session, root, cfg=cfg, with_embeddings=True)
    snap = latest_ready_snapshot(db_session, repo.id)
    assert snap is not None
    bundle = retrieve_ask_bundle(
        db_session,
        snapshot_id=snap.id,
        query="architecture overview for taking ownership",
        cfg=cfg,
    )
    eco = next(n for n in bundle.routing_notes if n.startswith("onboarding_ecosystems:"))
    assert "node" in eco
    mandatory = set(bundle.mandatory_paths)
    assert "package.json" in mandatory
    assert any("client_bootstrap_47.ts" in p for p in mandatory)
    assert any("Panel_Z3" in p or "components/" in p for p in mandatory)
    assert not any(p.endswith("vite.config.ts") for p in mandatory)


def test_java_fixture_unfamiliar_names_onboards_by_ecosystem(
    db_session: Session, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "java_repo"
    java_src = (
        "package com.acme.gate;\n"
        "public class RuntimeGateway91 {\n"
        "  public int ping() { return 91; }\n"
        "}\n"
    )
    _write_tree(
        root,
        {
            "README.md": "# Java gate\n",
            "pom.xml": (
                "<project><modelVersion>4.0.0</modelVersion>"
                "<groupId>com.acme</groupId><artifactId>gate</artifactId>"
                "<version>1.0</version></project>\n"
            ),
            "src/main/java/com/acme/gate/RuntimeGateway91.java": java_src,
            "src/main/java/com/acme/gate/HelperBean17.java": (
                "package com.acme.gate;\npublic class HelperBean17 {}\n"
            ),
        },
    )
    cfg = _AskSettings()
    _patch_settings(monkeypatch, cfg)
    repo = _index_tree(db_session, root, cfg=cfg, with_embeddings=True)
    snap = latest_ready_snapshot(db_session, repo.id)
    assert snap is not None
    bundle = retrieve_ask_bundle(
        db_session,
        snapshot_id=snap.id,
        query="Where should I start reading this repository?",
        cfg=cfg,
    )
    eco = next(n for n in bundle.routing_notes if n.startswith("onboarding_ecosystems:"))
    assert "java" in eco
    mandatory = set(bundle.mandatory_paths)
    assert "pom.xml" in mandatory
    assert any("RuntimeGateway91.java" in p for p in mandatory)
    assert any(p.startswith("src/main/java/") for p in mandatory)


# ---------------------------------------------------------------------------
# 9. Wrong / nonexistent filenames never silently resolve as exact matches
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "bogus",
    [
        "TotallyMissing_ZZZ.ts",
        "no_such_kernel_999.py",
        "AbsentGateway00.java",
        "phantom_settings_00.toml",
    ],
)
def test_nonexistent_filename_never_silent_exact_match(
    db_session: Session,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    bogus: str,
) -> None:
    root = tmp_path / "repo"
    _write_tree(
        root,
        {
            "README.md": "# R\n",
            "src/service_kernel_82.py": "def run():\n    return 1\n",
            "package.json": '{"name":"x"}\n',
        },
    )
    cfg = _AskSettings()
    _patch_settings(monkeypatch, cfg)
    repo = _index_tree(db_session, root, cfg=cfg, with_embeddings=True)
    snap = latest_ready_snapshot(db_session, repo.id)
    assert snap is not None

    analysis = analyze_query(f"Walk through {bogus} from beginning to end")
    assert bogus in analysis.paths or any(p.endswith(bogus) for p in analysis.paths)

    chunks = resolve_path_chunks(
        db_session, snapshot_id=snap.id, path_token=bogus, limit=None
    )
    assert chunks == []

    bundle = retrieve_ask_bundle(
        db_session,
        snapshot_id=snap.id,
        query=f"Walk through {bogus} from beginning to end",
        cfg=cfg,
    )
    assert bogus not in bundle.mandatory_paths
    assert not any(r.chunk.path.endswith(bogus) for r in bundle.ranked)
    assert any(
        (n.startswith("file_missing:") and bogus in n)
        or n == "retrieval_reason:file_not_indexed"
        for n in bundle.routing_notes
    )


def test_basename_collision_does_not_pick_wrong_sibling(
    db_session: Session, tmp_path: Path
) -> None:
    root = tmp_path / "repo"
    _write_tree(
        root,
        {
            "a/unique_alpha_1.py": "A = 1\n",
            "b/unique_beta_2.py": "B = 2\n",
        },
    )
    repo = _index_tree(db_session, root)
    snap = latest_ready_snapshot(db_session, repo.id)
    assert snap is not None
    chunks = resolve_path_chunks(
        db_session,
        snapshot_id=snap.id,
        path_token="unique_alpha_1.py",
        limit=None,
    )
    assert chunks
    assert all(c.path.endswith("unique_alpha_1.py") for c in chunks)
    assert not any("unique_beta_2" in c.path for c in chunks)


# ---------------------------------------------------------------------------
# 10. Exact-file complete coverage on fresh ecosystem fixtures
# ---------------------------------------------------------------------------


def test_exact_file_complete_on_python_arbitrary_module(
    db_session: Session, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Assignment-only module → whole-file/deep fallback → physical coverage 1..N."""
    root = tmp_path / "py"
    body = "KERNEL_ID = 82\nKERNEL_NAME = \"service_kernel_82\"\n"
    path = "src/service_kernel_82.py"
    _write_tree(
        root,
        {"README.md": "# P\n", "pyproject.toml": "[project]\nname='p'\n", path: body},
    )
    cfg = _AskSettings()
    _patch_settings(monkeypatch, cfg)
    repo = _index_tree(db_session, root, cfg=cfg, with_embeddings=True)
    snap = latest_ready_snapshot(db_session, repo.id)
    assert snap is not None
    bundle = retrieve_ask_bundle(
        db_session, snapshot_id=snap.id, query=f"Explain {path}", cfg=cfg
    )
    assert bundle.exact_file_mode
    cov = next(c for c in bundle.file_coverage if c.get("path") == path)
    assert cov["coverage_complete"] is True
    assert cov["missing_ranges"] == []
    contents = "\n".join(
        u.chunk.content for u in bundle.context.units if u.chunk.path == path
    )
    assert "KERNEL_ID" in contents and "KERNEL_NAME" in contents


def test_exact_file_complete_on_typescript_arbitrary_module(
    db_session: Session, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "ts"
    body = 'export default { boot: "client_bootstrap_47" };\n'
    path = "src/client_bootstrap_47.ts"
    _write_tree(
        root,
        {"README.md": "# T\n", "package.json": '{"name":"t"}\n', path: body},
    )
    cfg = _AskSettings()
    _patch_settings(monkeypatch, cfg)
    repo = _index_tree(db_session, root, cfg=cfg, with_embeddings=True)
    snap = latest_ready_snapshot(db_session, repo.id)
    assert snap is not None
    bundle = retrieve_ask_bundle(
        db_session, snapshot_id=snap.id, query=f"Walk through {path}", cfg=cfg
    )
    assert bundle.exact_file_mode
    cov = next(c for c in bundle.file_coverage if c.get("path") == path)
    assert cov["coverage_complete"] is True
    assert cov["missing_ranges"] == []


def test_exact_file_complete_on_java_arbitrary_type(
    db_session: Session, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """No class/method symbols → deep/whole-file fallback covers package line too."""
    root = tmp_path / "java"
    path = "src/main/java/com/acme/RuntimeGateway91.java"
    body = "package com.acme;\n// RuntimeGateway91 marker only\n"
    _write_tree(
        root,
        {
            "README.md": "# J\n",
            "pom.xml": "<project><modelVersion>4.0.0</modelVersion></project>\n",
            path: body,
        },
    )
    cfg = _AskSettings()
    _patch_settings(monkeypatch, cfg)
    repo = _index_tree(db_session, root, cfg=cfg, with_embeddings=True)
    snap = latest_ready_snapshot(db_session, repo.id)
    assert snap is not None
    bundle = retrieve_ask_bundle(
        db_session, snapshot_id=snap.id, query=f"Explain {path}", cfg=cfg
    )
    assert bundle.exact_file_mode
    cov = next(c for c in bundle.file_coverage if c.get("path") == path)
    assert cov["coverage_complete"] is True
    assert cov["missing_ranges"] == []
    contents = "\n".join(
        u.chunk.content for u in bundle.context.units if u.chunk.path == path
    )
    assert "com.acme" in contents


def test_deep_symbol_interstitial_gaps_reported_honestly(
    db_session: Session, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Remaining parser exception: multi-symbol deep files may miss blank lines.

    Coverage must stay honest (not invent completeness from filename).
    """
    root = tmp_path / "py_gap"
    path = "src/service_kernel_82.py"
    body = "def alpha():\n    return 1\n\ndef beta():\n    return 2\n"
    _write_tree(root, {path: body})
    cfg = _AskSettings()
    _patch_settings(monkeypatch, cfg)
    repo = _index_tree(db_session, root, cfg=cfg, with_embeddings=True)
    snap = latest_ready_snapshot(db_session, repo.id)
    assert snap is not None
    bundle = retrieve_ask_bundle(
        db_session, snapshot_id=snap.id, query=f"Explain {path}", cfg=cfg
    )
    cov = next(c for c in bundle.file_coverage if c.get("path") == path)
    # Either complete (if fallback fills) or honest partial with missing ranges.
    if not cov["coverage_complete"]:
        assert cov["missing_ranges"]
        assert all(isinstance(r, (list, tuple)) and len(r) == 2 for r in cov["missing_ranges"])
    contents = "\n".join(
        u.chunk.content for u in bundle.context.units if u.chunk.path == path
    )
    assert "def alpha" in contents and "def beta" in contents
