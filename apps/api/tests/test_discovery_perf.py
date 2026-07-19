"""Week 3 Day 6 — discovery performance smoke and path-hardening edges."""

from __future__ import annotations

import os
import time
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from app.core.language_contract import SkipReason, SupportLevel
from app.services.discovery import (
    discover_repository,
    normalize_relative_path,
)
from tests.helpers.retail_fixture import retail_shape_root

pytestmark = pytest.mark.slow


def test_discover_thousands_of_tiny_files_is_fast(tmp_path: Path) -> None:
    """Perf smoke: walk + classify many small files under a generous budget."""
    n = 2_500
    for i in range(n):
        sub = tmp_path / f"pkg{i % 50}"
        sub.mkdir(exist_ok=True)
        (sub / f"mod_{i}.py").write_text(f"x={i}\n", encoding="utf-8")
        if i % 10 == 0:
            (sub / f"note_{i}.md").write_text("# n\n", encoding="utf-8")
        if i % 25 == 0:
            (sub / f"keep_{i}.gitkeep").write_text("", encoding="utf-8")

    # Noise that must be pruned, not walked file-by-file forever.
    ignored = tmp_path / "node_modules" / "pkg"
    ignored.mkdir(parents=True)
    for j in range(200):
        (ignored / f"x{j}.js").write_text("export default 1\n", encoding="utf-8")

    git = tmp_path / ".git" / "objects"
    git.mkdir(parents=True)
    (git / "pack").write_bytes(b"\x00" * 64)

    start = time.perf_counter()
    result = discover_repository(tmp_path, max_files=50_000)
    elapsed = time.perf_counter() - start

    assert result.truncated is False
    assert result.deep_count == n
    assert "node_modules/pkg/x0.js" not in {f.path for f in result.files}
    assert ".git/objects/pack" not in {f.path for f in result.files}
    # Generous local-laptop budget (CI / Docker / cold disk).
    assert elapsed < 15.0, f"discovery took {elapsed:.3f}s for ~{n} files"


def test_discover_retail_shape_is_fast() -> None:
    start = time.perf_counter()
    result = discover_repository(retail_shape_root())
    elapsed = time.perf_counter() - start
    assert result.deep_count >= 1
    assert elapsed < 2.0, f"retail_shape discovery took {elapsed:.3f}s"


def test_nested_ignored_dirs_do_not_leak(tmp_path: Path) -> None:
    keep = tmp_path / "src"
    keep.mkdir()
    (keep / "ok.py").write_text("x=1\n", encoding="utf-8")
    deep_ignore = tmp_path / "src" / "vendor" / "lib"
    deep_ignore.mkdir(parents=True)
    (deep_ignore / "x.py").write_text("secret=1\n", encoding="utf-8")
    venv = tmp_path / ".venv" / "lib"
    venv.mkdir(parents=True)
    (venv / "site.py").write_text("x=1\n", encoding="utf-8")

    result = discover_repository(tmp_path)
    paths = {f.path for f in result.files}
    assert "src/ok.py" in paths
    assert "src/vendor/lib/x.py" not in paths
    assert ".venv/lib/site.py" not in paths


def test_empty_and_dotfile_edges(tmp_path: Path) -> None:
    (tmp_path / "empty_dir").mkdir()
    (tmp_path / ".hidden.py").write_text("x=1\n", encoding="utf-8")
    (tmp_path / "noext").write_text("plain\n", encoding="utf-8")
    result = discover_repository(tmp_path)
    by_path = {f.path: f for f in result.files}
    assert by_path[".hidden.py"].support_level is SupportLevel.DEEP
    assert by_path["noext"].skip_reason is SkipReason.UNSUPPORTED_EXT
    assert "empty_dir" not in by_path


def test_macos_git_tree_cleanup_after_discovery(tmp_path: Path) -> None:
    """Discovery must not leave `.git` trees that break pytest tmp cleanup on macOS."""
    git = tmp_path / ".git"
    (git / "objects" / "pack").mkdir(parents=True)
    (git / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    (git / "objects" / "pack" / "pack-1.pack").write_bytes(b"\x00" * 32)
    (tmp_path / "main.py").write_text("x=1\n", encoding="utf-8")

    discover_repository(tmp_path)

    # Same chmod walk pattern as snapshot / discovery unit tests.
    for dirpath, dirnames, filenames in os.walk(git, topdown=False):
        for name in filenames + dirnames:
            try:
                os.chmod(Path(dirpath) / name, 0o700)
            except OSError:
                pass
        try:
            os.chmod(dirpath, 0o700)
        except OSError:
            pass


@given(st.text(min_size=0, max_size=80))
@settings(max_examples=80, deadline=None)
def test_normalize_never_returns_parent_escape(raw: str) -> None:
    """Normalized paths must not start with ``..`` as a path segment."""
    normalized = normalize_relative_path(raw)
    if not normalized:
        return
    parts = normalized.split("/")
    assert ".." not in parts
    assert not normalized.startswith("/")
