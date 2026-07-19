import pytest

from app.services.github_url import (
    GitHubURLValidationError,
    ParsedGitHubRepository,
    parse_github_repository_url,
)

# Primary fixture repository for import / deep-Python demos.
RETAIL_REPO_URL = "https://github.com/rmarathe-hub/retail-retention-revenue-intel"


def test_accepts_primary_fixture_repository() -> None:
    parsed = parse_github_repository_url(RETAIL_REPO_URL)
    assert parsed == ParsedGitHubRepository(
        owner="rmarathe-hub",
        name="retail-retention-revenue-intel",
        host="github.com",
    )
    assert parsed.clone_url == (
        "https://github.com/rmarathe-hub/retail-retention-revenue-intel.git"
    )
    assert parsed.full_name == "rmarathe-hub/retail-retention-revenue-intel"


@pytest.mark.parametrize(
    "url",
    [
        RETAIL_REPO_URL,
        RETAIL_REPO_URL + "/",
        RETAIL_REPO_URL + ".git",
        "https://www.github.com/rmarathe-hub/retail-retention-revenue-intel",
        "  https://github.com/rmarathe-hub/retail-retention-revenue-intel  ",
    ],
)
def test_accepts_normalized_github_https_urls(url: str) -> None:
    parsed = parse_github_repository_url(url)
    assert parsed.owner == "rmarathe-hub"
    assert parsed.name == "retail-retention-revenue-intel"
    assert parsed.canonical_https_url == RETAIL_REPO_URL


@pytest.mark.parametrize(
    ("url", "code"),
    [
        ("", "empty_url"),
        ("   ", "empty_url"),
        ("http://github.com/rmarathe-hub/retail-retention-revenue-intel", "unsupported_protocol"),
        ("git://github.com/rmarathe-hub/retail-retention-revenue-intel", "unsupported_protocol"),
        (
            "git@github.com:rmarathe-hub/retail-retention-revenue-intel.git",
            "unsupported_protocol",
        ),
        (
            "ssh://git@github.com/rmarathe-hub/retail-retention-revenue-intel.git",
            "unsupported_protocol",
        ),
        ("file:///tmp/repo", "unsupported_protocol"),
        ("/tmp/retail-retention-revenue-intel", "local_path"),
        ("./local-repo", "local_path"),
        ("../local-repo", "local_path"),
        (
            "https://user:token@github.com/rmarathe-hub/retail-retention-revenue-intel",
            "embedded_credentials",
        ),
        ("https://gitlab.com/rmarathe-hub/retail-retention-revenue-intel", "invalid_host"),
        (
            "https://github.com.evil.com/rmarathe-hub/retail-retention-revenue-intel",
            "invalid_host",
        ),
        ("https://github.com/rmarathe-hub", "malformed_repository"),
        (
            "https://github.com/rmarathe-hub/retail-retention-revenue-intel/extra",
            "malformed_repository",
        ),
        ("https://github.com/rmarathe-hub/retail-retention-revenue-intel?x=1", "malformed_url"),
        ("https://github.com/rmarathe-hub/retail-retention-revenue-intel#frag", "malformed_url"),
        ("https://github.com/-bad/retail-retention-revenue-intel", "malformed_repository"),
        ("https://github.com/rmarathe-hub/bad repo", "malformed_url"),
    ],
)
def test_rejects_invalid_urls(url: str, code: str) -> None:
    with pytest.raises(GitHubURLValidationError) as exc:
        parse_github_repository_url(url)
    assert exc.value.code == code


def test_import_request_schema_uses_validator() -> None:
    from app.schemas.repositories import RepositoryImportRequest

    req = RepositoryImportRequest(url=RETAIL_REPO_URL + ".git")
    assert req.url == RETAIL_REPO_URL
