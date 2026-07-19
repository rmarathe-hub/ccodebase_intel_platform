"""Contract helpers added for Week 3 discovery."""

from __future__ import annotations

import pytest

from app.core.language_contract import (
    SkipReason,
    is_secret_basename,
    language_for_path,
    path_has_ignored_directory,
)


@pytest.mark.parametrize(
    ("path", "language"),
    [
        ("src/main.py", "python"),
        ("App.TSX", "typescript"),
        ("Makefile", "configuration"),
        ("Dockerfile", "configuration"),
        ("README", "documentation"),
        ("noext", None),
        ("x.unknown", None),
    ],
)
def test_language_for_path(path: str, language: str | None) -> None:
    assert language_for_path(path) == language


@pytest.mark.parametrize(
    ("name", "secret"),
    [
        (".env", True),
        (".env.local", True),
        ("id_rsa", True),
        ("cert.pem", True),
        ("main.py", False),
        ("env.txt", False),
    ],
)
def test_secret_basenames(name: str, secret: bool) -> None:
    assert is_secret_basename(name) is secret


@pytest.mark.parametrize(
    ("path", "ignored"),
    [
        ("node_modules/x/y.js", True),
        ("src/vendor/lib.go", True),
        ("src/main.py", False),
        (".git/config", True),
    ],
)
def test_ignored_directory_detection(path: str, ignored: bool) -> None:
    assert path_has_ignored_directory(path) is ignored


def test_skip_reason_values_stable() -> None:
    assert SkipReason.BINARY.value == "binary"
    assert SkipReason.SECRET_PATH.value == "secret_path"
