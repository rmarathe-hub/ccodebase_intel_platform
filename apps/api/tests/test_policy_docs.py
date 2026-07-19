"""Week 0 cost/policy/deployment safeguard validation tests."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
if not (ROOT / "docs" / "deployment" / "cost-policy.md").is_file():
    for candidate in Path(__file__).resolve().parents:
        if (candidate / "docs" / "deployment" / "cost-policy.md").is_file():
            ROOT = candidate
            break


REQUIRED_DOCS = [
    "docs/deployment/cost-policy.md",
    "docs/deployment/shutdown-checklist.md",
    "docs/deployment/calendar-reminders.md",
    "docs/deployment/reminders.ics",
    "docs/language-support.md",
    "docs/week-0.md",
    "docs/week-7.md",
    "docs/product-requirements.md",
    "docs/system-architecture.md",
    "docs/security-model.md",
    "docs/non-goals.md",
    "docs/indexing-pipeline.md",
]


@pytest.mark.parametrize("rel", REQUIRED_DOCS)
def test_required_week0_docs_exist(rel: str) -> None:
    path = ROOT / rel
    assert path.is_file(), f"missing {rel}"
    assert path.stat().st_size > 50


def test_cost_policy_hard_limits() -> None:
    text = (ROOT / "docs/deployment/cost-policy.md").read_text(encoding="utf-8")
    for needle in (
        "Maximum deployment duration",
        "7 days",
        "Maximum intended spend",
        "$10",
        "Paid Redis",
        "prohibited",
        "Kubernetes",
        "rg-codeintel-demo",
        "$0",
        "LLM_ENRICHMENT_ENABLED",
        "opt-in",
    ):
        assert needle in text


def test_language_support_forbids_regex_structure() -> None:
    text = (ROOT / "docs/language-support.md").read_text(encoding="utf-8")
    assert "Forbidden" in text or "forbidden" in text.lower()
    assert "regex" in text.lower()
    assert "verified_deep" in text
    assert "generic_structure" in text
    assert "symbol-aware" in text.lower()


def test_shutdown_checklist_items() -> None:
    text = (ROOT / "docs/deployment/shutdown-checklist.md").read_text(encoding="utf-8")
    for needle in (
        "Revoke AI API key",
        "Delete Azure resource group",
        "Check billing after 24 hours",
        "Check billing after 7 days",
        "Supabase",
    ):
        assert needle in text


def test_reminders_ics_is_parseable_calendar() -> None:
    text = (ROOT / "docs/deployment/reminders.ics").read_text(encoding="utf-8")
    assert "BEGIN:VCALENDAR" in text
    assert "END:VCALENDAR" in text
    assert text.count("BEGIN:VEVENT") >= 5
    assert "codeintel" in text.lower() or "Codeintel" in text


def test_compose_has_no_redis_or_k8s() -> None:
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    assert "redis" not in compose.lower()
    assert "kubernetes" not in compose.lower()
    assert "postgres" in compose.lower()
    assert "pgvector" in compose.lower()


def test_pyproject_has_no_paid_cloud_sdks() -> None:
    """Cloud infra SDKs stay out of main deps; LLM SDKs only as optional extras."""
    text = (ROOT / "apps/api/pyproject.toml").read_text(encoding="utf-8")
    # Split main project table from optional-dependencies if present.
    main = text
    optional = ""
    if "[project.optional-dependencies]" in text:
        main, optional = text.split("[project.optional-dependencies]", 1)
    for banned in ("boto3", "azure-", "google-cloud"):
        assert banned not in main
        assert banned not in optional
    # openai / anthropic must not be required runtime deps; optional extras OK later.
    for llm in ("openai", "anthropic"):
        assert llm not in main


def test_gitignore_excludes_env_secrets() -> None:
    text = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert ".env" in text
    assert "node_modules" in text
    assert ".venv" in text


def test_no_hardcoded_azure_keys_in_source() -> None:
    pattern = re.compile(r"(AZURE_[A-Z0-9_]*(KEY|SECRET|PASSWORD)\s*=\s*['\"][^'\"]+['\"])")
    offenders: list[str] = []
    for path in (ROOT / "apps").rglob("*"):
        if path.suffix not in {".py", ".ts", ".tsx", ".yml", ".yaml", ".env", ".md"}:
            continue
        if "node_modules" in path.parts or ".venv" in path.parts:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except OSError:
            continue
        if pattern.search(content):
            offenders.append(str(path))
    assert offenders == []
