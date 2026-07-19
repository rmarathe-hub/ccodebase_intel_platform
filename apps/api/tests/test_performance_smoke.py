"""Performance smoke tests (marked slow; generous thresholds)."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from app.core.language_contract import support_level_for_extension
from app.services.github_url import parse_github_repository_url
from app.services.snapshots import count_files_excluding_git

pytestmark = pytest.mark.slow


def test_classify_large_extension_matrix_is_fast() -> None:
    extensions = [
        ".py",
        ".java",
        ".ts",
        ".tsx",
        ".js",
        ".jsx",
        ".go",
        ".rs",
        ".sql",
        ".md",
        ".yaml",
        ".exe",
        ".bin",
        ".png",
        ".unknown",
    ] * 200
    start = time.perf_counter()
    for ext in extensions:
        support_level_for_extension(ext)
    elapsed = time.perf_counter() - start
    assert elapsed < 2.0, f"classification took {elapsed:.3f}s"


def test_count_files_on_hundreds_of_paths(tmp_path: Path) -> None:
    for i in range(400):
        sub = tmp_path / f"d{i % 20}"
        sub.mkdir(exist_ok=True)
        (sub / f"f{i}.py").write_text(f"x={i}\n", encoding="utf-8")
    git = tmp_path / ".git"
    git.mkdir()
    (git / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    start = time.perf_counter()
    count = count_files_excluding_git(tmp_path)
    elapsed = time.perf_counter() - start
    assert count == 400
    assert elapsed < 5.0, f"file count took {elapsed:.3f}s"


def test_url_parse_throughput() -> None:
    urls = [
        "https://github.com/rmarathe-hub/retail-retention-revenue-intel",
        "https://github.com/rmarathe-hub/ccodebase_intel_platform.git",
        "https://github.com/abc/def-ghi",
    ] * 300
    start = time.perf_counter()
    for url in urls:
        parse_github_repository_url(url)
    elapsed = time.perf_counter() - start
    assert elapsed < 2.0, f"url parse took {elapsed:.3f}s"
