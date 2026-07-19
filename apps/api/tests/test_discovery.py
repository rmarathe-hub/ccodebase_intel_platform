"""Unit tests for Week 3 discovery walker and classification."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from app.core.language_contract import SkipReason, SupportLevel
from app.services.discovery import (
    classify_file,
    count_lines,
    discover_repository,
    is_probably_binary,
    looks_like_test_path,
    normalize_relative_path,
)


def test_normalize_relative_path() -> None:
    assert normalize_relative_path("./src/main.py") == "src/main.py"
    assert normalize_relative_path("\\src\\main.py") == "src/main.py"
    assert normalize_relative_path("/abs/not") == "abs/not"


def test_count_lines_variants() -> None:
    assert count_lines(b"") == 0
    assert count_lines(b"one") == 1
    assert count_lines(b"a\nb\n") == 2
    assert count_lines(b"a\nb") == 2


def test_binary_sniff() -> None:
    assert is_probably_binary(b"hello\nworld") is False
    assert is_probably_binary(b"\x00\x01\x02\x03") is True
    assert is_probably_binary(bytes(range(256))) is True


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("tests/test_foo.py", True),
        ("src/foo_test.py", True),
        ("src/foo.test.ts", True),
        ("src/main.py", False),
    ],
)
def test_test_path_heuristic(path: str, expected: bool) -> None:
    assert looks_like_test_path(path) is expected


def test_classify_python_deep() -> None:
    content = b"def hello():\n    return 1\n"
    result = classify_file(
        relative_path="src/hello.py",
        size_bytes=len(content),
        sample=content,
        full_content=content,
        is_symlink=False,
        max_file_bytes=10_000,
    )
    assert result.support_level is SupportLevel.DEEP
    assert result.language == "python"
    assert result.skip_reason is None
    assert result.content_hash is not None
    assert result.line_count == 2


def test_classify_go_generic_never_deep() -> None:
    content = b"package main\n"
    result = classify_file(
        relative_path="cmd/main.go",
        size_bytes=len(content),
        sample=content,
        full_content=content,
        is_symlink=False,
        max_file_bytes=10_000,
    )
    assert result.support_level is SupportLevel.GENERIC
    assert result.language == "go"


def test_classify_secret_env() -> None:
    result = classify_file(
        relative_path=".env",
        size_bytes=10,
        sample=b"SECRET=1\n",
        full_content=b"SECRET=1\n",
        is_symlink=False,
        max_file_bytes=10_000,
    )
    assert result.support_level is SupportLevel.SKIP
    assert result.skip_reason is SkipReason.SECRET_PATH


def test_classify_ignored_dir() -> None:
    result = classify_file(
        relative_path="node_modules/leftpad/index.js",
        size_bytes=10,
        sample=b"module.exports=1\n",
        full_content=b"module.exports=1\n",
        is_symlink=False,
        max_file_bytes=10_000,
    )
    assert result.support_level is SupportLevel.SKIP
    assert result.skip_reason is SkipReason.IGNORED_DIR


def test_classify_oversized() -> None:
    result = classify_file(
        relative_path="big.py",
        size_bytes=5_000,
        sample=b"x",
        full_content=None,
        is_symlink=False,
        max_file_bytes=100,
    )
    assert result.skip_reason is SkipReason.OVERSIZED


def test_classify_symlink() -> None:
    result = classify_file(
        relative_path="link.py",
        size_bytes=0,
        sample=None,
        full_content=None,
        is_symlink=True,
        max_file_bytes=10_000,
    )
    assert result.skip_reason is SkipReason.SYMLINK


def test_discover_repository_matrix(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# hi\n", encoding="utf-8")
    src = tmp_path / "src"
    src.mkdir()
    (src / "app.py").write_text("print(1)\n", encoding="utf-8")
    (src / "util.go").write_text("package util\n", encoding="utf-8")
    (src / "App.JAVA").write_text("class App {}\n", encoding="utf-8")
    (src / "weird.unknown").write_text("x\n", encoding="utf-8")
    (tmp_path / ".env").write_text("K=V\n", encoding="utf-8")
    (tmp_path / "logo.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 20)

    vendor = tmp_path / "node_modules" / "pkg"
    vendor.mkdir(parents=True)
    (vendor / "index.js").write_text("export default 1\n", encoding="utf-8")

    git = tmp_path / ".git"
    git.mkdir()
    (git / "config").write_text("x", encoding="utf-8")

    nested = tmp_path / "has space"
    nested.mkdir()
    (nested / "ユニコード.py").write_text("x=1\n", encoding="utf-8")

    result = discover_repository(tmp_path, max_file_bytes=10_000, max_files=1000)

    by_path = {f.path: f for f in result.files}
    assert "src/app.py" in by_path
    assert by_path["src/app.py"].support_level is SupportLevel.DEEP
    assert by_path["src/util.go"].support_level is SupportLevel.GENERIC
    assert by_path["src/App.JAVA"].language == "java"
    assert by_path["src/App.JAVA"].support_level is SupportLevel.DEEP
    assert by_path["README.md"].support_level is SupportLevel.GENERIC
    assert by_path["src/weird.unknown"].skip_reason is SkipReason.UNSUPPORTED_EXT
    assert by_path[".env"].skip_reason is SkipReason.SECRET_PATH
    assert by_path["logo.png"].skip_reason is SkipReason.BINARY
    assert by_path["has space/ユニコード.py"].support_level is SupportLevel.DEEP

    # Ignored trees should not appear (pruned) or appear as skip if walked.
    assert "node_modules/pkg/index.js" not in by_path
    assert ".git/config" not in by_path

    assert result.deep_count >= 3
    assert result.generic_count >= 2
    assert result.truncated is False


def test_discover_does_not_follow_symlink_escape(tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    secret = outside / "secret.py"
    secret.write_text("SECRET=1\n", encoding="utf-8")

    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "ok.py").write_text("print(1)\n", encoding="utf-8")
    link = repo / "escape.py"
    try:
        link.symlink_to(secret)
    except OSError:
        pytest.skip("symlinks not supported")

    result = discover_repository(repo)
    by_path = {f.path: f for f in result.files}
    assert by_path["ok.py"].support_level is SupportLevel.DEEP
    assert by_path["escape.py"].skip_reason is SkipReason.SYMLINK
    # Ensure we did not index outside content as a deep file under escape path.
    assert by_path["escape.py"].content_hash is None


def test_discover_max_files_truncation(tmp_path: Path) -> None:
    for i in range(20):
        (tmp_path / f"f{i}.py").write_text(f"x={i}\n", encoding="utf-8")
    result = discover_repository(tmp_path, max_files=5)
    assert result.truncated is True
    assert len(result.files) == 5


def test_discover_crlf_and_bom(tmp_path: Path) -> None:
    (tmp_path / "a.py").write_bytes(b"\xef\xbb\xbfprint(1)\r\n")
    (tmp_path / "b.js").write_bytes(b"export const x = 1;\r\n")
    result = discover_repository(tmp_path)
    by_path = {f.path: f for f in result.files}
    assert by_path["a.py"].support_level is SupportLevel.DEEP
    assert by_path["b.js"].support_level is SupportLevel.DEEP
    assert by_path["a.py"].line_count == 1


def test_discover_deterministic_ordering(tmp_path: Path) -> None:
    for name in ("c.py", "a.py", "b.py"):
        (tmp_path / name).write_text("x=1\n", encoding="utf-8")
    first = discover_repository(tmp_path)
    second = discover_repository(tmp_path)
    assert [f.path for f in first.files] == [f.path for f in second.files]
    assert [f.path for f in first.files] == sorted(f.path for f in first.files)


def test_chmod_cleanup_for_git_like_tree(tmp_path: Path) -> None:
    """Ensure discovery does not leave unreadable trees that break pytest tmp cleanup."""
    git = tmp_path / ".git"
    git.mkdir()
    (git / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    (tmp_path / "main.py").write_text("x=1\n", encoding="utf-8")
    discover_repository(tmp_path)
    # Make writable for macOS tmp cleanup (same pattern as snapshot tests).
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
