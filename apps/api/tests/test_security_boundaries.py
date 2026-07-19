"""Security boundary tests for clone, paths, and public errors."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from app.services.git_clone import GitCloneError, secure_clone
from app.services.github_url import GitHubURLValidationError, parse_github_repository_url


@pytest.mark.parametrize(
    "url",
    [
        "https://user:ghp_secrettoken123@github.com/a/b",
        "https://x-access-token:secret@github.com/a/b",
        "https://oauth2:secret@github.com/a/b",
    ],
)
def test_embedded_tokens_rejected(url: str) -> None:
    with pytest.raises(GitHubURLValidationError) as exc:
        parse_github_repository_url(url)
    assert exc.value.code == "embedded_credentials"
    assert "secret" not in str(exc.value).lower() or "credential" in str(exc.value).lower()


def test_clone_args_never_enable_submodules(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    seen: list[list[str]] = []

    def fake_run(args: list[str], *, cwd=None, timeout_seconds: int):
        seen.append(args)
        result = MagicMock()
        result.returncode = 0
        result.stdout = "deadbeef\n" if "rev-parse" in args else ""
        result.stderr = ""
        if args[:1] == ["clone"]:
            Path(args[-1]).mkdir(parents=True, exist_ok=True)
            (Path(args[-1]) / "f.txt").write_text("ok", encoding="utf-8")
        if args == ["rev-parse", "--abbrev-ref", "HEAD"]:
            result.stdout = "main\n"
        return result

    monkeypatch.setattr("app.services.git_clone._run_git", fake_run)
    with secure_clone(
        "https://github.com/rmarathe-hub/retail-retention-revenue-intel.git",
        base_dir=tmp_path,
        max_bytes=10_000,
    ):
        pass
    clone_args = next(args for args in seen if args and args[0] == "clone")
    assert "--no-recurse-submodules" in clone_args
    assert "--depth" in clone_args
    assert "1" in clone_args
    assert "--recurse-submodules" not in clone_args


def test_clone_cleanup_after_failure(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    def boom(args: list[str], *, cwd=None, timeout_seconds: int):
        raise GitCloneError("clone_failed", "simulated failure")

    monkeypatch.setattr("app.services.git_clone._run_git", boom)
    with pytest.raises(GitCloneError):
        with secure_clone(
            "https://github.com/rmarathe-hub/retail-retention-revenue-intel.git",
            base_dir=tmp_path,
        ):
            pass
    assert list(tmp_path.glob("repo-*")) == []


def test_clone_size_limit_enforced(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    def fake_run(args: list[str], *, cwd=None, timeout_seconds: int):
        result = MagicMock()
        result.returncode = 0
        result.stdout = ""
        result.stderr = ""
        if args[:1] == ["clone"]:
            repo = Path(args[-1])
            repo.mkdir(parents=True, exist_ok=True)
            (repo / "big.bin").write_bytes(b"x" * 5000)
        return result

    monkeypatch.setattr("app.services.git_clone._run_git", fake_run)
    with pytest.raises(GitCloneError) as exc:
        with secure_clone(
            "https://github.com/rmarathe-hub/retail-retention-revenue-intel.git",
            base_dir=tmp_path,
            max_bytes=100,
        ):
            pass
    assert exc.value.code == "repo_too_large"
    assert list(tmp_path.glob("repo-*")) == []


@pytest.mark.parametrize(
    "name",
    [
        "normal.py",
        "has space.py",
        "ユニコード.py",
        "a" * 120 + ".py",
        "..sneaky.py",
        ".hidden",
        "semi;colon.py",
        "quote\"name.py",
    ],
)
def test_snapshot_file_counter_handles_odd_names(tmp_path: Path, name: str) -> None:
    from app.services.snapshots import count_files_excluding_git

    target = tmp_path / name
    try:
        target.write_text("x", encoding="utf-8")
    except OSError:
        pytest.skip("filesystem rejected filename")
    # Create a fake git dir without relying on nested protected cleanup paths
    git_marker = tmp_path / ".git"
    git_marker.mkdir()
    (git_marker / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    count = count_files_excluding_git(tmp_path)
    assert count >= 1
    assert (git_marker / "HEAD").exists()
