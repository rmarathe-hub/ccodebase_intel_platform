"""Week 3 Day 5 — golden discovery against the retail fixture (and offline shape)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from app.core.language_contract import SupportLevel
from app.services.discovery import discover_repository
from tests.helpers.retail_fixture import (
    ensure_retail_fixture,
    golden_json_path,
    retail_shape_golden_path,
    retail_shape_root,
)

pytestmark = pytest.mark.integration


def _load_golden(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _assert_matches_golden(repo_root: Path, golden: dict[str, Any]) -> None:
    result = discover_repository(repo_root)
    counts = golden["counts"]
    assert len(result.files) == counts["total"]
    assert result.deep_count == counts["deep"]
    assert result.generic_count == counts["generic"]
    assert result.skip_count == counts["skip"]
    assert result.truncated is counts["truncated"]

    by_path = {f.path: f for f in result.files}
    expected_files: list[dict[str, Any]] = golden["files"]
    assert [f.path for f in result.files] == [row["path"] for row in expected_files]

    for row in expected_files:
        actual = by_path[row["path"]]
        assert actual.support_level.value == row["support_level"], row["path"]
        assert actual.language == row["language"], row["path"]
        skip = actual.skip_reason.value if actual.skip_reason else None
        assert skip == row["skip_reason"], row["path"]
        assert actual.is_test_file is row["is_test_file"], row["path"]

    # Dual-run determinism (same tree → identical ordered paths).
    second = discover_repository(repo_root)
    assert [f.path for f in result.files] == [f.path for f in second.files]


def test_retail_shape_offline_golden() -> None:
    """Committed mini tree always runs — no network, no cache."""
    golden = _load_golden(retail_shape_golden_path())
    _assert_matches_golden(retail_shape_root(), golden)


def test_retail_fixture_golden_path() -> None:
    """Full retail demo repo vs committed golden (cached local clone preferred)."""
    fixture = ensure_retail_fixture(allow_clone=True)
    if fixture is None:
        pytest.skip(
            "Retail fixture unavailable (set CODEINTEL_RETAIL_FIXTURE or allow "
            "one-time clone into .cache/retail-retention-revenue-intel)"
        )

    golden = _load_golden(golden_json_path())
    _assert_matches_golden(fixture, golden)


def test_retail_fixture_key_paths_contract() -> None:
    """Spot-check policy-critical paths on the real fixture when present."""
    fixture = ensure_retail_fixture(allow_clone=True)
    if fixture is None:
        pytest.skip("Retail fixture unavailable")

    result = discover_repository(fixture)
    by_path = {f.path: f for f in result.files}

    assert by_path["scripts/load_to_postgres.py"].support_level is SupportLevel.DEEP
    assert by_path["scripts/load_to_postgres.py"].language == "python"
    assert by_path["tests/conftest.py"].is_test_file is True
    assert by_path["tests/conftest.py"].support_level is SupportLevel.DEEP
    assert by_path["README.md"].support_level is SupportLevel.GENERIC
    assert by_path["sql/01_schema.sql"].language == "sql"
    assert by_path["sql/01_schema.sql"].support_level is SupportLevel.GENERIC
    assert by_path[".env.example"].support_level is SupportLevel.SKIP
    assert by_path[".env.example"].skip_reason is not None
    assert by_path[".env.example"].skip_reason.value == "secret_path"

    # Deep must never include SQL / markdown.
    for f in result.files:
        if f.support_level is SupportLevel.DEEP:
            assert f.language == "python"
