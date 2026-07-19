"""Configuration and settings matrix."""

from __future__ import annotations

import pytest

from app.core.config import Settings


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("http://localhost:5173", ["http://localhost:5173"]),
        (
            "http://localhost:5173,http://127.0.0.1:5173",
            ["http://localhost:5173", "http://127.0.0.1:5173"],
        ),
        (
            " http://a.com , http://b.com ",
            ["http://a.com", "http://b.com"],
        ),
        ("", []),
        (",,,", []),
    ],
)
def test_cors_parsing_matrix(raw: str, expected: list[str]) -> None:
    assert Settings(cors_origins=raw).cors_origin_list == expected


def test_defaults_are_local_first() -> None:
    settings = Settings(
        app_env="local",
        database_url="postgresql+psycopg://codeintel:codeintel@localhost:5434/codeintel",
        cors_origins="http://localhost:5173",
    )
    assert settings.app_env == "local"
    assert "localhost" in settings.database_url or "postgres" in settings.database_url
    assert settings.job_lease_seconds > 0
    assert settings.git_clone_timeout_seconds > 0
    assert settings.git_clone_max_bytes > 0
    assert "azure" not in settings.database_url.lower()
    assert settings.llm_enrichment_enabled is False
    assert settings.llm_provider == "none"
    assert settings.llm_enrichment_active is False
    assert settings.llm_temperature == 0.0
    assert settings.llm_kill_switch is False


def test_llm_enrichment_active_requires_opt_in() -> None:
    off = Settings(llm_enrichment_enabled=True, llm_provider="none")
    assert off.llm_enrichment_active is False
    killed = Settings(
        llm_enrichment_enabled=True,
        llm_provider="openai",
        llm_kill_switch=True,
    )
    assert killed.llm_enrichment_active is False
    on = Settings(llm_enrichment_enabled=True, llm_provider="openai")
    assert on.llm_enrichment_active is True


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("job_lease_seconds", 1),
        ("job_lease_seconds", 3600),
        ("job_retry_delay_seconds", 0),
        ("git_clone_timeout_seconds", 5),
        ("git_clone_max_bytes", 1024),
        ("worker_poll_interval_seconds", 0.1),
    ],
)
def test_numeric_settings_accept_bounds(field: str, value: float) -> None:
    settings = Settings(**{field: value})  # type: ignore[arg-type]
    assert getattr(settings, field) == value
