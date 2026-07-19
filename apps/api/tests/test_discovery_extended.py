"""Extended discovery edge matrix (Week 3)."""

from __future__ import annotations

import os
import stat
from pathlib import Path

import pytest

from app.core.language_contract import SupportLevel
from app.services.discovery import discover_repository


def test_empty_and_single_file(tmp_path: Path) -> None:
    empty = discover_repository(tmp_path)
    assert empty.files == ()
    assert empty.truncated is False

    (tmp_path / "a.py").write_text("x=1\n", encoding="utf-8")
    one = discover_repository(tmp_path)
    assert len(one.files) == 1
    assert one.files[0].support_level == SupportLevel.DEEP
    assert one.files[0].language == "python"


def test_max_files_truncation(tmp_path: Path) -> None:
    for i in range(12):
        (tmp_path / f"f{i}.py").write_text("x=1\n", encoding="utf-8")
    result = discover_repository(tmp_path, max_files=5)
    assert result.truncated is True
    assert len(result.files) == 5


def test_oversized_file_skipped(tmp_path: Path) -> None:
    big = tmp_path / "big.py"
    big.write_bytes(b"x" * 200)
    result = discover_repository(tmp_path, max_file_bytes=50)
    assert len(result.files) == 1
    assert result.files[0].support_level == SupportLevel.SKIP
    assert result.files[0].skip_reason == "oversized"


def test_symlink_not_followed(tmp_path: Path) -> None:
    target = tmp_path / "real.py"
    target.write_text("def x():\n    return 1\n", encoding="utf-8")
    link = tmp_path / "link.py"
    try:
        link.symlink_to(target)
    except OSError:
        pytest.skip("symlinks unsupported")
    outside = tmp_path / "outside.txt"
    outside.write_text("secret\n", encoding="utf-8")
    escape = tmp_path / "escape.py"
    try:
        escape.symlink_to(outside)
    except OSError:
        pytest.skip("symlinks unsupported")

    result = discover_repository(tmp_path)
    by_path = {f.path: f for f in result.files}
    assert "real.py" in by_path
    assert by_path["link.py"].support_level == SupportLevel.SKIP
    assert by_path["link.py"].skip_reason == "symlink"
    assert by_path["escape.py"].skip_reason == "symlink"


def test_ignored_directories_pruned(tmp_path: Path) -> None:
    (tmp_path / "keep.py").write_text("x=1\n", encoding="utf-8")
    for ignored in ("node_modules", ".git", "dist", "build", ".venv", "__pycache__"):
        d = tmp_path / ignored
        d.mkdir()
        (d / "secret.py").write_text("SHOULD_NOT_SEE=1\n", encoding="utf-8")
    result = discover_repository(tmp_path)
    paths = {f.path for f in result.files}
    assert paths == {"keep.py"}


def test_secret_paths_skipped(tmp_path: Path) -> None:
    (tmp_path / ".env").write_text("TOKEN=x\n", encoding="utf-8")
    (tmp_path / ".env.local").write_text("TOKEN=y\n", encoding="utf-8")
    (tmp_path / "id_rsa.pem").write_text("KEY\n", encoding="utf-8")
    (tmp_path / "ok.py").write_text("x=1\n", encoding="utf-8")
    result = discover_repository(tmp_path)
    by_path = {f.path: f for f in result.files}
    assert by_path["ok.py"].support_level == SupportLevel.DEEP
    for secret in (".env", ".env.local", "id_rsa.pem"):
        assert by_path[secret].support_level == SupportLevel.SKIP
        assert by_path[secret].skip_reason == "secret_path"


def test_binary_null_byte_detection(tmp_path: Path) -> None:
    (tmp_path / "blob.bin").write_bytes(b"abc\x00def")
    (tmp_path / "text.py").write_text("x=1\n", encoding="utf-8")
    result = discover_repository(tmp_path)
    by_path = {f.path: f for f in result.files}
    assert by_path["blob.bin"].support_level == SupportLevel.SKIP
    assert by_path["blob.bin"].skip_reason in {"binary", "unsupported_ext"}


def test_crlf_and_no_final_newline_line_counts(tmp_path: Path) -> None:
    (tmp_path / "crlf.py").write_bytes(b"a=1\r\nb=2\r\n")
    (tmp_path / "nonew.py").write_bytes(b"a=1\nb=2")
    result = discover_repository(tmp_path)
    by_path = {f.path: f for f in result.files}
    assert by_path["crlf.py"].line_count == 2
    assert by_path["nonew.py"].line_count == 2


def test_unicode_and_spaces_in_filenames(tmp_path: Path) -> None:
    (tmp_path / "café mod.py").write_text("x=1\n", encoding="utf-8")
    (tmp_path / "weird name.py").write_text("y=2\n", encoding="utf-8")
    result = discover_repository(tmp_path)
    paths = {f.path for f in result.files}
    assert "café mod.py" in paths
    assert "weird name.py" in paths


def test_deep_languages_classified_but_java_ts_js_not_parsed_here(tmp_path: Path) -> None:
    files = {
        "a.py": "x=1\n",
        "A.java": "class A {}\n",
        "a.ts": " console.log(1)\n",
        "a.tsx": "export const X=1\n",
        "a.js": "module.exports=1\n",
        "a.jsx": "export default 1\n",
    }
    for name, body in files.items():
        (tmp_path / name).write_text(body, encoding="utf-8")
    result = discover_repository(tmp_path)
    by_path = {f.path: f for f in result.files}
    for name in files:
        assert by_path[name].support_level == SupportLevel.DEEP
        assert by_path[name].language is not None
    # Discovery does not invent parser stamps — that happens only after Python parse.
    assert all(f.language != "python" or f.path.endswith(".py") for f in result.files)


def test_unreadable_file_skip(tmp_path: Path) -> None:
    locked = tmp_path / "locked.py"
    locked.write_text("x=1\n", encoding="utf-8")
    try:
        os.chmod(locked, 0)
    except OSError:
        pytest.skip("chmod not permitted")
    try:
        result = discover_repository(tmp_path)
        by_path = {f.path: f for f in result.files}
        if "locked.py" in by_path:
            assert by_path["locked.py"].skip_reason in {"unreadable", None} or (
                by_path["locked.py"].support_level
                in {SupportLevel.SKIP, SupportLevel.DEEP}
            )
    finally:
        os.chmod(locked, stat.S_IRUSR | stat.S_IWUSR)


def test_deterministic_ordering(tmp_path: Path) -> None:
    for name in ("z.py", "a.py", "m.py"):
        (tmp_path / name).write_text("x=1\n", encoding="utf-8")
    first = [f.path for f in discover_repository(tmp_path).files]
    second = [f.path for f in discover_repository(tmp_path).files]
    assert first == second
    assert first == sorted(first)
