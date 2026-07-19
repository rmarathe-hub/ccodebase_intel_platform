"""Tests for secure Git cloning."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from app.services.git_clone import (
    CloneResult,
    GitCloneError,
    directory_size_bytes,
    secure_clone,
)


def test_directory_size_bytes(tmp_path: Path) -> None:
    file_a = tmp_path / "a.txt"
    file_a.write_text("hello", encoding="utf-8")
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "b.txt").write_text("world!", encoding="utf-8")
    assert directory_size_bytes(tmp_path) == len("hello") + len("world!")


def test_secure_clone_success(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    calls: list[list[str]] = []

    def fake_run_git(args: list[str], *, cwd=None, timeout_seconds: int):
        calls.append(args)
        result = MagicMock()
        result.returncode = 0
        if args[:1] == ["clone"]:
            repo_path = Path(args[-1])
            repo_path.mkdir(parents=True, exist_ok=True)
            (repo_path / "README.md").write_text("demo", encoding="utf-8")
            result.stdout = ""
            result.stderr = ""
        elif args == ["rev-parse", "HEAD"]:
            result.stdout = "abc123def456\n"
            result.stderr = ""
        elif args == ["rev-parse", "--abbrev-ref", "HEAD"]:
            result.stdout = "main\n"
            result.stderr = ""
        else:
            result.stdout = ""
            result.stderr = ""
        return result

    monkeypatch.setattr("app.services.git_clone._run_git", fake_run_git)

    url = "https://github.com/rmarathe-hub/retail-retention-revenue-intel.git"
    with secure_clone(url, base_dir=tmp_path, timeout_seconds=10, max_bytes=1024) as cloned:
        assert isinstance(cloned, CloneResult)
        assert cloned.commit_sha == "abc123def456"
        assert cloned.branch == "main"
        assert cloned.path.exists()
        assert "clone" in calls[0][0]
        assert "--depth" in calls[0]
        assert "1" in calls[0]
        assert "--no-recurse-submodules" in calls[0]

    # Cleanup removes the randomized work directory.
    assert list(tmp_path.glob("repo-*")) == []


def test_secure_clone_rejects_oversized_repo(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    def fake_run_git(args: list[str], *, cwd=None, timeout_seconds: int):
        result = MagicMock()
        result.returncode = 0
        result.stdout = ""
        result.stderr = ""
        if args[:1] == ["clone"]:
            repo_path = Path(args[-1])
            repo_path.mkdir(parents=True, exist_ok=True)
            (repo_path / "big.bin").write_bytes(b"x" * 100)
        return result

    monkeypatch.setattr("app.services.git_clone._run_git", fake_run_git)

    with pytest.raises(GitCloneError) as exc:
        with secure_clone(
            "https://github.com/rmarathe-hub/retail-retention-revenue-intel.git",
            base_dir=tmp_path,
            max_bytes=10,
        ):
            pass
    assert exc.value.code == "repo_too_large"
    assert list(tmp_path.glob("repo-*")) == []


def test_secure_clone_timeout(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    def fake_run_git(args: list[str], *, cwd=None, timeout_seconds: int):
        raise GitCloneError("clone_timeout", "git clone timed out")

    monkeypatch.setattr("app.services.git_clone._run_git", fake_run_git)

    with pytest.raises(GitCloneError) as exc:
        with secure_clone(
            "https://github.com/rmarathe-hub/retail-retention-revenue-intel.git",
            base_dir=tmp_path,
        ):
            pass
    assert exc.value.code == "clone_timeout"
