from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.services.github_url import ParsedGitHubRepository, parse_github_repository_url


class RepositoryImportRequest(BaseModel):
    url: str = Field(min_length=1, description="Public GitHub HTTPS repository URL")
    branch: str | None = Field(
        default=None,
        max_length=200,
        description="Optional branch to clone (default: remote HEAD)",
    )

    @field_validator("url")
    @classmethod
    def validate_github_url(cls, value: str) -> str:
        parsed = parse_github_repository_url(value)
        return parsed.canonical_https_url

    @field_validator("branch")
    @classmethod
    def normalize_branch(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class ParsedRepositoryURL(BaseModel):
    owner: str
    name: str
    host: str
    clone_url: str
    canonical_https_url: str
    full_name: str

    @classmethod
    def from_parsed(cls, parsed: ParsedGitHubRepository) -> "ParsedRepositoryURL":
        return cls(
            owner=parsed.owner,
            name=parsed.name,
            host=parsed.host,
            clone_url=parsed.clone_url,
            canonical_https_url=parsed.canonical_https_url,
            full_name=parsed.full_name,
        )


class RepositoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    host: str
    owner_name: str
    name: str
    default_branch: str
    clone_url: str
