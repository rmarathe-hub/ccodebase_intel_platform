"""Validate and parse public GitHub repository HTTPS URLs."""

from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import unquote, urlparse

ALLOWED_HOSTS = frozenset({"github.com", "www.github.com"})

# GitHub owner/repo naming rules (simplified, security-focused).
_OWNER_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9]|-(?=[A-Za-z0-9])){0,38}$")
_REPO_RE = re.compile(r"^[A-Za-z0-9_.-]{1,100}$")


class GitHubURLValidationError(ValueError):
    """Raised when a repository URL is rejected."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


@dataclass(frozen=True, slots=True)
class ParsedGitHubRepository:
    owner: str
    name: str
    host: str = "github.com"

    @property
    def clone_url(self) -> str:
        return f"https://{self.host}/{self.owner}/{self.name}.git"

    @property
    def canonical_https_url(self) -> str:
        return f"https://{self.host}/{self.owner}/{self.name}"

    @property
    def full_name(self) -> str:
        return f"{self.owner}/{self.name}"


def parse_github_repository_url(raw_url: str) -> ParsedGitHubRepository:
    """Parse a public GitHub HTTPS repository URL.

    Accepted form:
      https://github.com/{owner}/{repository}

    Optional trailing `.git` and `/` are allowed.
    """
    if raw_url is None:
        raise GitHubURLValidationError("empty_url", "Repository URL is required")

    url = raw_url.strip()
    if not url:
        raise GitHubURLValidationError("empty_url", "Repository URL is required")

    if any(ch.isspace() for ch in url):
        raise GitHubURLValidationError(
            "malformed_url",
            "Repository URL must not contain whitespace",
        )

    # Explicitly reject local / file / git protocol / ssh-style inputs.
    lowered = url.lower()
    if lowered.startswith(("file:", "git@", "ssh:", "git://")):
        raise GitHubURLValidationError(
            "unsupported_protocol",
            "Only HTTPS GitHub URLs are supported",
        )
    if url.startswith("/") or url.startswith("./") or url.startswith("../"):
        raise GitHubURLValidationError("local_path", "Local filesystem paths are not allowed")
    if re.match(r"^[A-Za-z]:[\\/]", url):
        raise GitHubURLValidationError("local_path", "Local filesystem paths are not allowed")

    parsed = urlparse(url)

    if parsed.scheme.lower() != "https":
        raise GitHubURLValidationError(
            "unsupported_protocol",
            "Only HTTPS GitHub URLs are supported",
        )

    if parsed.username or parsed.password:
        raise GitHubURLValidationError(
            "embedded_credentials",
            "URLs must not include embedded credentials",
        )

    host = (parsed.hostname or "").lower()
    if host not in ALLOWED_HOSTS:
        raise GitHubURLValidationError(
            "invalid_host",
            "Only github.com repository URLs are supported",
        )

    if parsed.query or parsed.fragment:
        raise GitHubURLValidationError(
            "malformed_url",
            "Repository URL must not include query parameters or fragments",
        )

    path = unquote(parsed.path or "").strip("/")
    if not path:
        raise GitHubURLValidationError("malformed_repository", "Repository path is missing")

    parts = [part for part in path.split("/") if part]
    if len(parts) != 2:
        raise GitHubURLValidationError(
            "malformed_repository",
            "Repository URL must be https://github.com/{owner}/{repository}",
        )

    owner, repo = parts
    if repo.endswith(".git"):
        repo = repo[: -len(".git")]

    if not owner or not repo:
        raise GitHubURLValidationError("malformed_repository", "Owner and repository are required")

    if not _OWNER_RE.fullmatch(owner):
        raise GitHubURLValidationError("malformed_repository", "Invalid GitHub owner name")

    if not _REPO_RE.fullmatch(repo) or repo in {".", ".."}:
        raise GitHubURLValidationError("malformed_repository", "Invalid GitHub repository name")

    return ParsedGitHubRepository(owner=owner, name=repo, host="github.com")
