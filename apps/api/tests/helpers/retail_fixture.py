"""Resolve a local checkout of the retail demo fixture for golden tests.

Preference order (no clone-on-every-test):
1. ``CODEINTEL_RETAIL_FIXTURE`` — absolute path to an existing clone
2. Repo-local cache at ``.cache/retail-retention-revenue-intel``
3. One-time shallow clone into that cache (network; opt-in via fixture)

The golden JSON committed under ``tests/fixtures/`` is the source of truth for
classification expectations; content hashes are intentionally omitted so
upstream doc edits do not flake the suite.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

RETAIL_CLONE_URL = (
    "https://github.com/rmarathe-hub/retail-retention-revenue-intel.git"
)
RETAIL_CACHE_DIRNAME = "retail-retention-revenue-intel"
ENV_FIXTURE_PATH = "CODEINTEL_RETAIL_FIXTURE"


def repo_root() -> Path:
    """``codebase_intel_platform`` root (``apps/api/tests/helpers`` → four up)."""
    return Path(__file__).resolve().parents[4]


def default_cache_path() -> Path:
    return repo_root() / ".cache" / RETAIL_CACHE_DIRNAME


def fixtures_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "fixtures"


def golden_json_path() -> Path:
    return fixtures_dir() / "retail_retention_golden.json"


def retail_shape_root() -> Path:
    """Always-available offline mini tree mirroring retail classification shape."""
    return fixtures_dir() / "retail_shape"


def retail_shape_golden_path() -> Path:
    return fixtures_dir() / "retail_shape_golden.json"


def _looks_like_fixture(path: Path) -> bool:
    return path.is_dir() and (path / "README.md").is_file() and (path / "scripts").is_dir()


def resolve_existing_retail_fixture() -> Path | None:
    """Return a usable fixture path without network I/O, or None."""
    env = os.environ.get(ENV_FIXTURE_PATH, "").strip()
    if env:
        candidate = Path(env).expanduser().resolve()
        if _looks_like_fixture(candidate):
            return candidate
        return None

    cached = default_cache_path()
    if _looks_like_fixture(cached):
        return cached.resolve()
    return None


def ensure_retail_fixture(*, allow_clone: bool = True) -> Path | None:
    """Return fixture root, cloning once into ``.cache`` when allowed.

    Returns ``None`` when the fixture is unavailable (offline / clone failed).
    """
    existing = resolve_existing_retail_fixture()
    if existing is not None:
        return existing

    if not allow_clone:
        return None

    cache = default_cache_path()
    cache.parent.mkdir(parents=True, exist_ok=True)
    if cache.exists():
        # Incomplete previous clone — remove and retry.
        if not _looks_like_fixture(cache):
            subprocess.run(["rm", "-rf", str(cache)], check=False)
        else:
            return cache.resolve()

    try:
        subprocess.run(
            [
                "git",
                "clone",
                "--depth",
                "1",
                RETAIL_CLONE_URL,
                str(cache),
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except (OSError, subprocess.SubprocessError):
        return None

    if _looks_like_fixture(cache):
        return cache.resolve()
    return None
