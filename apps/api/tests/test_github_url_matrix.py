"""Broad parameterized GitHub URL validation matrix (security + acceptance)."""

from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from app.services.github_url import (
    GitHubURLValidationError,
    parse_github_repository_url,
)

RETAIL = "https://github.com/rmarathe-hub/retail-retention-revenue-intel"


@pytest.mark.parametrize(
    "url",
    [
        RETAIL,
        RETAIL + "/",
        RETAIL + ".git",
        RETAIL + ".git/",
        "https://www.github.com/rmarathe-hub/retail-retention-revenue-intel",
        "https://GITHUB.com/rmarathe-hub/retail-retention-revenue-intel",
        "  https://github.com/rmarathe-hub/retail-retention-revenue-intel  ",
        "https://github.com/a/b",
        "https://github.com/abc/def_ghi",
        "https://github.com/abc/def-ghi",
        "https://github.com/abc/def.ghi",
        "https://github.com/0user/repo0",
        "https://github.com/rmarathe-hub/ccodebase_intel_platform",
    ],
)
def test_accepts_valid_public_github_urls(url: str) -> None:
    parsed = parse_github_repository_url(url)
    assert parsed.host == "github.com"
    assert parsed.owner
    assert parsed.name
    assert parsed.clone_url.endswith(".git")
    assert parsed.canonical_https_url.startswith("https://github.com/")
    assert "/" in parsed.full_name


@pytest.mark.parametrize(
    ("url", "code"),
    [
        ("", "empty_url"),
        ("   ", "empty_url"),
        ("http://github.com/a/b", "unsupported_protocol"),
        ("ftp://github.com/a/b", "unsupported_protocol"),
        ("git://github.com/a/b", "unsupported_protocol"),
        ("git@github.com:a/b.git", "unsupported_protocol"),
        ("ssh://git@github.com/a/b.git", "unsupported_protocol"),
        ("file:///tmp/repo", "unsupported_protocol"),
        ("/tmp/repo", "local_path"),
        ("./repo", "local_path"),
        ("../repo", "local_path"),
        ("C:\\Users\\x\\repo", "local_path"),
        ("https://user:pass@github.com/a/b", "embedded_credentials"),
        ("https://token@github.com/a/b", "embedded_credentials"),
        ("https://gitlab.com/a/b", "invalid_host"),
        ("https://bitbucket.org/a/b", "invalid_host"),
        ("https://github.com.evil.com/a/b", "invalid_host"),
        ("https://notgithub.com/a/b", "invalid_host"),
        ("https://github.com", "malformed_repository"),
        ("https://github.com/", "malformed_repository"),
        ("https://github.com/onlyowner", "malformed_repository"),
        ("https://github.com/a/b/c", "malformed_repository"),
        ("https://github.com/a/b/c/d", "malformed_repository"),
        ("https://github.com/a/b?x=1", "malformed_url"),
        ("https://github.com/a/b#frag", "malformed_url"),
        ("https://github.com/a/b?ref=main", "malformed_url"),
        ("https://github.com/-bad/repo", "malformed_repository"),
        ("https://github.com/bad-/repo", "malformed_repository"),
        ("https://github.com/a/bad repo", "malformed_url"),
        ("https://github.com/a/b c", "malformed_url"),
        ("https://github.com/a/", "malformed_repository"),
        ("https://github.com//b", "malformed_repository"),
        ("javascript:alert(1)", "unsupported_protocol"),
        ("data:text/plain,hi", "unsupported_protocol"),
        ("https://github.com/a/..", "malformed_repository"),
        ("https://github.com/./b", "malformed_repository"),
        ("https://github.com/a/.", "malformed_repository"),
    ],
)
def test_rejects_dangerous_or_invalid_urls(url: str, code: str) -> None:
    with pytest.raises(GitHubURLValidationError) as exc:
        parse_github_repository_url(url)
    assert exc.value.code == code


@pytest.mark.parametrize(
    "payload",
    [
        "https://github.com/a/b;rm -rf /",
        "https://github.com/a/b$(whoami)",
        "https://github.com/a/b`id`",
        "https://github.com/a/b|cat /etc/passwd",
        "https://github.com/a/b&&reboot",
        "https://github.com/a/b\nDROP TABLE users;",
        "https://github.com/a/b%0Arm -rf",
        "https://github.com/a/../../etc/passwd",
        "https://github.com/a/b%2F%2E%2E",
    ],
)
def test_rejects_injection_like_urls(payload: str) -> None:
    with pytest.raises(GitHubURLValidationError):
        parse_github_repository_url(payload)


@given(
    owner=st.from_regex(r"[A-Za-z0-9](?:[A-Za-z0-9]|-(?=[A-Za-z0-9])){0,20}", fullmatch=True),
    name=st.from_regex(r"[A-Za-z0-9_.-]{1,40}", fullmatch=True),
)
@settings(max_examples=80, deadline=None)
def test_property_roundtrip_canonical_urls(owner: str, name: str) -> None:
    if name in {".", ".."}:
        return
    url = f"https://github.com/{owner}/{name}"
    parsed = parse_github_repository_url(url)
    assert parsed.owner == owner
    assert parsed.name == name
    again = parse_github_repository_url(parsed.canonical_https_url)
    assert again == parsed
    assert parse_github_repository_url(parsed.clone_url).name == name


@given(junk=st.text(min_size=0, max_size=80))
@settings(max_examples=60, deadline=None)
def test_property_random_strings_never_crash(junk: str) -> None:
    try:
        parse_github_repository_url(junk)
    except GitHubURLValidationError:
        return
