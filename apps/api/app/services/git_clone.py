"""Secure shallow Git cloning for untrusted public repositories."""

from __future__ import annotations

import logging
import os
import secrets
import shutil
import subprocess
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


class GitCloneError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


@dataclass(frozen=True, slots=True)
class CloneResult:
    path: Path
    branch: str
    commit_sha: str
    bytes_on_disk: int


def _run_git(
    args: list[str],
    *,
    cwd: Path | None = None,
    timeout_seconds: int,
) -> subprocess.CompletedProcess[str]:
    env = {
        **os.environ,
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_CONFIG_NOSYSTEM": "1",
        "LC_ALL": "C",
    }
    try:
        return subprocess.run(
            ["git", *args],
            cwd=str(cwd) if cwd else None,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            env=env,
        )
    except subprocess.TimeoutExpired as exc:
        raise GitCloneError("clone_timeout", f"git {' '.join(args)} timed out") from exc
    except FileNotFoundError as exc:
        raise GitCloneError("git_missing", "git executable not found on PATH") from exc


def directory_size_bytes(root: Path) -> int:
    total = 0
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in filenames:
            path = Path(dirpath) / name
            try:
                total += path.stat().st_size
            except OSError:
                continue
    return total


def _resolve_head(repo_path: Path, *, timeout_seconds: int) -> tuple[str, str]:
    sha_proc = _run_git(
        ["rev-parse", "HEAD"],
        cwd=repo_path,
        timeout_seconds=timeout_seconds,
    )
    if sha_proc.returncode != 0:
        raise GitCloneError("clone_failed", sha_proc.stderr.strip() or "failed to resolve HEAD")
    commit_sha = sha_proc.stdout.strip()

    branch_proc = _run_git(
        ["rev-parse", "--abbrev-ref", "HEAD"],
        cwd=repo_path,
        timeout_seconds=timeout_seconds,
    )
    branch = branch_proc.stdout.strip() if branch_proc.returncode == 0 else "HEAD"
    if branch == "HEAD":
        # Detached HEAD after shallow clone — use remote default symbolic name if present.
        branch = "main"
    return branch, commit_sha


@contextmanager
def secure_clone(
    clone_url: str,
    *,
    timeout_seconds: int = 120,
    max_bytes: int = 50 * 1024 * 1024,
    base_dir: str | Path | None = None,
) -> Iterator[CloneResult]:
    """Shallow-clone a repository into a randomized temp directory, then clean up.

    Safeguards:
    - depth-1 shallow clone
    - no submodule recursion
    - clone timeout
    - repository size limit after clone
    - no package install / no code execution
    - always deletes the temp directory on exit
    """
    parent = Path(base_dir) if base_dir else Path(tempfile.gettempdir()) / "codeintel-clones"
    parent.mkdir(parents=True, exist_ok=True)

    token = secrets.token_hex(8)
    work_dir = Path(tempfile.mkdtemp(prefix=f"repo-{token}-", dir=str(parent)))
    repo_path = work_dir / "repo"

    try:
        # --depth 1: shallow
        # --single-branch: default branch only
        # --no-recurse-submodules: never fetch submodule contents
        proc = _run_git(
            [
                "clone",
                "--depth",
                "1",
                "--single-branch",
                "--no-recurse-submodules",
                "--",
                clone_url,
                str(repo_path),
            ],
            timeout_seconds=timeout_seconds,
        )
        if proc.returncode != 0:
            detail = (proc.stderr or proc.stdout or "git clone failed").strip()
            raise GitCloneError("clone_failed", detail)

        size = directory_size_bytes(repo_path)
        if size > max_bytes:
            raise GitCloneError(
                "repo_too_large",
                f"Repository size {size} bytes exceeds limit of {max_bytes} bytes",
            )

        branch, commit_sha = _resolve_head(repo_path, timeout_seconds=min(30, timeout_seconds))
        logger.info(
            "Cloned %s at %s (%s bytes) into %s",
            clone_url,
            commit_sha[:12],
            size,
            repo_path,
        )
        yield CloneResult(
            path=repo_path,
            branch=branch,
            commit_sha=commit_sha,
            bytes_on_disk=size,
        )
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)
