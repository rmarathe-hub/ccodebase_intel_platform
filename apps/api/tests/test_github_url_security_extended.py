"""Additional GitHub URL security / rejection matrix (extends Week 2 coverage)."""

from __future__ import annotations

import pytest

from app.services.github_url import GitHubURLValidationError, parse_github_repository_url


@pytest.mark.parametrize(
    "url",
    [
        "https://github.com/rmarathe-hub/retail-retention-revenue-intel",
        "https://github.com/rmarathe-hub/retail-retention-revenue-intel.git",
        "https://github.com/rmarathe-hub/retail-retention-revenue-intel/",
        "https://www.github.com/rmarathe-hub/retail-retention-revenue-intel",
        "https://github.com/owner-name/repo.name",
        "https://github.com/Owner123/Repo_name-1",
    ],
)
def test_accepts_extended_valid_urls(url: str) -> None:
    parsed = parse_github_repository_url(url)
    assert parsed.owner
    assert parsed.name
    assert parsed.clone_url.startswith("https://")
    assert "github.com" in parsed.clone_url
    assert parsed.clone_url.endswith(".git")


@pytest.mark.parametrize(
    ("url", "code"),
    [
        ("http://github.com/a/b", "unsupported_protocol"),
        ("ssh://git@github.com/a/b.git", "unsupported_protocol"),
        ("git://github.com/a/b", "unsupported_protocol"),
        ("file:///tmp/repo", "unsupported_protocol"),
        ("https://github.com.evil.com/a/b", "invalid_host"),
        ("https://github.com.attacker.tld/a/b", "invalid_host"),
        ("https://notgithub.com/a/b", "invalid_host"),
        ("https://127.0.0.1/a/b", "invalid_host"),
        ("https://localhost/a/b", "invalid_host"),
        ("https://[::1]/a/b", "invalid_host"),
        ("https://192.168.1.1/a/b", "invalid_host"),
        ("https://10.0.0.1/a/b", "invalid_host"),
        ("https://user:pass@github.com/a/b", "embedded_credentials"),
        ("https://github.com/a/b?ref=main", "malformed_url"),
        ("https://github.com/a/b#frag", "malformed_url"),
        ("https://github.com/a/b/tree/main", "malformed_repository"),
        ("https://github.com/a/b/blob/main/x.py", "malformed_repository"),
        ("https://github.com/a/b/issues/1", "malformed_repository"),
        ("https://github.com/a/b/pull/1", "malformed_repository"),
        ("https://github.com/a/b/releases/tag/v1", "malformed_repository"),
        ("https://github.com//b", "malformed_repository"),
        ("https://github.com/a/", "malformed_repository"),
        ("https://github.com/a/b/c", "malformed_repository"),
        ("https://github.com/a/b%2f../x", "malformed_repository"),
        ("https://github.com/a/b;rm -rf /", "malformed_url"),
        ("https://github.com/a/b$(whoami)", "malformed_repository"),
        ("https://github.com/a/b`id`", "malformed_repository"),
        ("https://github.com/a/" + ("b" * 300), "malformed_repository"),
        ("", "empty_url"),
        ("   ", "empty_url"),
        ("./local", "local_path"),
        ("/abs/path", "local_path"),
    ],
)
def test_rejects_extended_invalid_urls(url: str, code: str) -> None:
    with pytest.raises(GitHubURLValidationError) as exc:
        parse_github_repository_url(url)
    assert exc.value.code == code
    # Embedded credentials must not echo the password into the message.
    if code == "embedded_credentials":
        assert "pass" not in str(exc.value).lower()


def test_trailing_newline_is_stripped_and_accepted() -> None:
    """url.strip() removes trailing whitespace before validation."""
    parsed = parse_github_repository_url(
        "https://github.com/rmarathe-hub/retail-retention-revenue-intel\n"
    )
    assert parsed.owner == "rmarathe-hub"
