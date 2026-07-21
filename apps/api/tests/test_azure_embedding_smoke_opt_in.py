"""Opt-in live Azure embedding smoke — skipped unless RUN_AZURE_INTEGRATION_TESTS=true."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "test_azure_embedding.py"


@pytest.mark.network
def test_azure_embedding_smoke_opt_in() -> None:
    if os.environ.get("RUN_AZURE_INTEGRATION_TESTS", "").strip().lower() not in {
        "1",
        "true",
        "yes",
    }:
        pytest.skip("Set RUN_AZURE_INTEGRATION_TESTS=true to run live Azure embedding smoke")

    env = os.environ.copy()
    env["RUN_AZURE_INTEGRATION_TESTS"] = "true"
    proc = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=str(SCRIPT.parent.parent),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    # Never echo full stdout in assertion messages if it somehow leaked secrets —
    # script is designed to print only sanitized lines.
    assert proc.returncode == 0, proc.stdout + "\n" + proc.stderr
    assert "AZURE_EMBEDDING_SMOKE_TEST=PASS" in proc.stdout
    assert "sk-" not in proc.stdout.lower()
    assert "api_key" not in proc.stdout.lower()
