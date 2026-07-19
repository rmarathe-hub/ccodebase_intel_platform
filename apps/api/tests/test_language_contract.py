"""Language-support honesty contract tests (docs ↔ code)."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.core.language_contract import (
    DEEP_LANGUAGES,
    EXTENSION_LANGUAGE,
    GENERIC_LANGUAGES,
    SupportLevel,
    claims_deep_analysis,
    support_level_for_extension,
    support_level_for_language,
)

ROOT = Path(__file__).resolve().parents[3]
# mutmut copies tests under apps/api/mutants/; walk up to find the real repo docs.
if not (ROOT / "docs" / "language-support.md").is_file():
    for candidate in Path(__file__).resolve().parents:
        if (candidate / "docs" / "language-support.md").is_file():
            ROOT = candidate
            break
LANG_DOC = ROOT / "docs" / "language-support.md"


def test_language_support_doc_exists() -> None:
    assert LANG_DOC.is_file()
    text = LANG_DOC.read_text(encoding="utf-8")
    required_tokens = (
        "Python",
        "Java",
        "TypeScript",
        "JavaScript",
        "DEEP",
        "GENERIC",
        "deep",
        "generic",
    )
    for required in required_tokens:
        assert required in text


@pytest.mark.parametrize("language", sorted(DEEP_LANGUAGES))
def test_deep_languages_claim_deep(language: str) -> None:
    assert support_level_for_language(language) is SupportLevel.DEEP
    assert claims_deep_analysis(language) is True


@pytest.mark.parametrize("language", sorted(GENERIC_LANGUAGES))
def test_generic_languages_do_not_claim_deep(language: str) -> None:
    assert support_level_for_language(language) is SupportLevel.GENERIC
    assert claims_deep_analysis(language) is False


@pytest.mark.parametrize(
    "language",
    ["cobol", "fortran", "haskell", "elixir", "unknown", "", "  ", "PYTHON3"],
)
def test_unknown_languages_are_skip_or_normalized(language: str) -> None:
    level = support_level_for_language(language)
    if language.strip().lower() in DEEP_LANGUAGES | GENERIC_LANGUAGES:
        assert level is not SupportLevel.SKIP
    else:
        assert level is SupportLevel.SKIP
        assert claims_deep_analysis(language) is False


@pytest.mark.parametrize(
    ("ext", "expected"),
    [
        (".py", SupportLevel.DEEP),
        (".java", SupportLevel.DEEP),
        (".ts", SupportLevel.DEEP),
        (".tsx", SupportLevel.DEEP),
        (".js", SupportLevel.DEEP),
        (".jsx", SupportLevel.DEEP),
        (".go", SupportLevel.GENERIC),
        (".rs", SupportLevel.GENERIC),
        (".sql", SupportLevel.GENERIC),
        (".md", SupportLevel.GENERIC),
        (".yaml", SupportLevel.GENERIC),
        (".yml", SupportLevel.GENERIC),
        (".exe", SupportLevel.SKIP),
        (".bin", SupportLevel.SKIP),
        (".png", SupportLevel.SKIP),
        (".jpg", SupportLevel.SKIP),
        (".zip", SupportLevel.SKIP),
        (".pdf", SupportLevel.SKIP),
        (".wasm", SupportLevel.SKIP),
        ("py", SupportLevel.DEEP),  # without dot
        (".PY", SupportLevel.DEEP),
        (".JsX", SupportLevel.DEEP),
    ],
)
def test_extension_support_levels(ext: str, expected: SupportLevel) -> None:
    assert support_level_for_extension(ext) is expected


def test_every_mapped_extension_resolves_known_language() -> None:
    for ext, language in EXTENSION_LANGUAGE.items():
        assert ext.startswith(".")
        level = support_level_for_language(language)
        assert level in {SupportLevel.DEEP, SupportLevel.GENERIC}


def test_deep_and_generic_disjoint() -> None:
    assert DEEP_LANGUAGES.isdisjoint(GENERIC_LANGUAGES)
