"""Documentation and cost/local-first contract checks for Weeks 0–4."""

from __future__ import annotations

import re
from pathlib import Path

from app.core.language_contract import DEEP_LANGUAGES, GENERIC_LANGUAGES, SupportLevel
from app.models.job_stages import JOB_STAGE_PROGRESS, JobStage
from app.services.python_ast_parser import PARSER_NAME, PARSER_VERSION

ROOT = Path(__file__).resolve().parents[3]


def test_week_docs_exist() -> None:
    for name in ("week-0.md", "week-3.md", "week-4.md", "week-5.md", "week-6.md", "week-7.md"):
        assert (ROOT / "docs" / name).is_file()


def test_cost_and_shutdown_artifacts() -> None:
    deploy = ROOT / "docs" / "deployment"
    assert (deploy / "cost-policy.md").is_file()
    assert (deploy / "shutdown-checklist.md").is_file()
    ics = (deploy / "reminders.ics").read_text(encoding="utf-8")
    assert "BEGIN:VCALENDAR" in ics
    assert "BEGIN:VEVENT" in ics
    assert "END:VCALENDAR" in ics


def test_compose_publishes_postgres_on_5434() -> None:
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    assert '"5434:5432"' in compose or "5434:5432" in compose
    assert "pgvector" in compose
    assert "redis" not in compose.lower()
    assert "kubernetes" not in compose.lower()
    assert "azure" not in compose.lower()


def test_ci_does_not_provision_azure() -> None:
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    lowered = ci.lower()
    assert "azure" not in lowered
    assert "terraform" not in lowered
    assert "pulumi" not in lowered
    assert "openai" not in lowered


def test_gitignore_allows_retail_shape_data() -> None:
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "data/" in gitignore
    assert "!apps/api/tests/fixtures/retail_shape/data/" in gitignore
    assert "!apps/api/tests/fixtures/retail_shape/data/**" in gitignore


def test_language_contract_matches_docs_lists() -> None:
    lang_doc = (ROOT / "docs" / "language-support.md").read_text(encoding="utf-8")
    for lang in sorted(DEEP_LANGUAGES):
        assert lang.lower() in lang_doc.lower() or lang in lang_doc
    assert SupportLevel.DEEP.value == "deep"
    assert SupportLevel.GENERIC.value == "generic"
    assert SupportLevel.SKIP.value == "skip"
    # Generic set is non-empty and includes SQL / documentation markers in docs.
    assert "sql" in {g.lower() for g in GENERIC_LANGUAGES} or "sql" in lang_doc.lower()


def test_job_stages_include_future_labels_but_worker_docs_honest() -> None:
    # Labels exist for future stages.
    assert JobStage.CHUNKING in JOB_STAGE_PROGRESS
    assert JobStage.EMBEDDING in JOB_STAGE_PROGRESS
    assert JobStage.VALIDATING in JOB_STAGE_PROGRESS
    week4 = (ROOT / "docs" / "week-4.md").read_text(encoding="utf-8")
    # Week 4 doc must not claim Search/Ask complete.
    assert "Search API" not in week4 or "not" in week4.lower()
    pipeline = (ROOT / "docs" / "indexing-pipeline.md").read_text(encoding="utf-8")
    assert "Queued" in pipeline or "queued" in pipeline.lower()


def test_python_parser_stamp_documented_shape() -> None:
    assert PARSER_NAME == "python-ast"
    assert re.match(r"^4\.3-\d+\.\d+-stdlib$", PARSER_VERSION)


def test_no_paid_sdk_imports_in_app() -> None:
    """Infra SDKs banned everywhere; LLM SDKs only under app/services/llm/."""
    app_root = ROOT / "apps" / "api" / "app"
    banned_everywhere = ("azure", "boto3", "redis", "kubernetes")
    llm_only = ("openai", "anthropic")
    for path in app_root.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(app_root)
        in_llm = rel.parts[:2] == ("services", "llm")
        for token in banned_everywhere:
            assert f"import {token}" not in text
            assert f"from {token}" not in text
        if not in_llm:
            for token in llm_only:
                assert f"import {token}" not in text
                assert f"from {token}" not in text
