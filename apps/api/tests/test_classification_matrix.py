"""Filesystem classification matrix for the language-support honesty contract.

Week 3 discovery is not implemented yet; this suite locks the extension →
support-level contract so classifiers cannot silently claim deep analysis.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from app.core.language_contract import (
    DEEP_LANGUAGES,
    EXTENSION_LANGUAGE,
    GENERIC_LANGUAGES,
    SupportLevel,
    claims_deep_analysis,
    support_level_for_extension,
    support_level_for_language,
)

DEEP_EXTS = sorted(ext for ext, lang in EXTENSION_LANGUAGE.items() if lang in DEEP_LANGUAGES)
GENERIC_EXTS = sorted(
    ext for ext, lang in EXTENSION_LANGUAGE.items() if lang in GENERIC_LANGUAGES
)

SKIP_EXTS = [
    ".exe",
    ".dll",
    ".so",
    ".dylib",
    ".bin",
    ".o",
    ".a",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".pdf",
    ".zip",
    ".tar",
    ".gz",
    ".tgz",
    ".7z",
    ".rar",
    ".wasm",
    ".class",
    ".jar",
    ".pyc",
    ".pyo",
    ".lock",  # unknown extension class → skip until policy maps lockfiles
    ".min.js.map",  # not a mapped extension
]


@pytest.mark.parametrize("ext", DEEP_EXTS)
def test_deep_extensions_never_skip(ext: str) -> None:
    assert support_level_for_extension(ext) is SupportLevel.DEEP
    lang = EXTENSION_LANGUAGE[ext]
    assert claims_deep_analysis(lang) is True


@pytest.mark.parametrize("ext", GENERIC_EXTS)
def test_generic_extensions_never_claim_deep(ext: str) -> None:
    assert support_level_for_extension(ext) is SupportLevel.GENERIC
    lang = EXTENSION_LANGUAGE[ext]
    assert claims_deep_analysis(lang) is False


@pytest.mark.parametrize("ext", SKIP_EXTS)
def test_binary_and_unknown_extensions_skip(ext: str) -> None:
    # Only the final suffix segment is considered by the contract helper.
    leaf = ext if ext.count(".") <= 1 else "." + ext.rsplit(".", 1)[-1]
    level = support_level_for_extension(leaf)
    if leaf in EXTENSION_LANGUAGE:
        pytest.skip(f"{leaf} is mapped")
    assert level is SupportLevel.SKIP


@pytest.mark.parametrize(
    "filename",
    [
        "Main.PY",
        "App.TSX",
        "index.Js",
        "Util.JAVA",
        "query.SQL",
        "README.MD",
        "config.YAML",
        "nested/dir/mod.py",
        "has space/file.go",
        "ユニコード/ファイル.rs",
        ".hidden/config.toml",
        "vendor/pkg/lib.js",  # classification by extension only (skip policy is Week 3)
        "dist/bundle.min.js",
        "a" * 80 + ".py",
    ],
)
def test_filename_extension_matrix(filename: str) -> None:
    suffix = Path(filename).suffix
    level = support_level_for_extension(suffix)
    assert level in {SupportLevel.DEEP, SupportLevel.GENERIC, SupportLevel.SKIP}
    if level is SupportLevel.GENERIC:
        assert claims_deep_analysis(EXTENSION_LANGUAGE[suffix.lower()]) is False


@pytest.mark.parametrize(
    ("content_kind", "ext"),
    [
        ("empty", ".py"),
        ("lf", ".py"),
        ("crlf", ".js"),
        ("bom", ".ts"),
        ("no_final_newline", ".java"),
        ("unicode", ".go"),
        ("null_byte", ".bin"),
    ],
)
def test_content_shapes_do_not_change_extension_contract(
    tmp_path: Path, content_kind: str, ext: str
) -> None:
    payloads = {
        "empty": b"",
        "lf": b"print(1)\n",
        "crlf": b"export const x = 1;\r\n",
        "bom": b"\xef\xbb\xbfexport const x = 1;\n",
        "no_final_newline": b"class A {}",
        "unicode": "package main\n// café\n".encode(),
        "null_byte": b"\x00\x01\x02\xff",
    }
    path = tmp_path / f"sample{ext}"
    path.write_bytes(payloads[content_kind])
    assert path.exists()
    # Contract is extension-based until Week 3 content sniffing exists.
    level = support_level_for_extension(ext)
    if ext == ".bin":
        assert level is SupportLevel.SKIP
    else:
        assert level in {SupportLevel.DEEP, SupportLevel.GENERIC}


@given(ext=st.sampled_from(sorted(EXTENSION_LANGUAGE)))
@settings(max_examples=40, deadline=None)
def test_property_mapped_extensions_never_skip(ext: str) -> None:
    assert support_level_for_extension(ext) is not SupportLevel.SKIP


@given(name=st.text(min_size=1, max_size=40))
@settings(max_examples=50, deadline=None)
def test_property_unknown_suffixes_are_skip_or_mapped(name: str) -> None:
    suffix = Path(f"x.{name}").suffix.lower()
    level = support_level_for_extension(suffix)
    if suffix in EXTENSION_LANGUAGE:
        assert level in {SupportLevel.DEEP, SupportLevel.GENERIC}
    else:
        # Empty or odd suffixes fall through to SKIP
        assert level is SupportLevel.SKIP or suffix in EXTENSION_LANGUAGE


def test_support_level_sets_cover_docs_lists() -> None:
    assert "python" in DEEP_LANGUAGES
    assert "java" in DEEP_LANGUAGES
    assert "typescript" in DEEP_LANGUAGES
    assert "javascript" in DEEP_LANGUAGES
    for lang in ("go", "rust", "sql", "shell", "html", "css", "documentation", "configuration"):
        assert lang in GENERIC_LANGUAGES
        assert support_level_for_language(lang) is SupportLevel.GENERIC
