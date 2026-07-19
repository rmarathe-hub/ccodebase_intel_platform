from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SourceFileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    snapshot_id: UUID
    path: str
    size_bytes: int
    line_count: int | None
    content_hash: str | None
    language: str | None
    support_level: str
    parser_name: str | None
    parser_version: str | None
    skip_reason: str | None
    is_test_file: bool
    is_generated: bool
    is_vendor: bool
    is_binary: bool
    created_at: datetime


class SourceFileListResponse(BaseModel):
    repository_id: UUID
    snapshot_id: UUID | None
    total: int
    limit: int
    offset: int
    files: list[SourceFileRead]


class RepositoryListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    host: str
    owner_name: str
    name: str
    default_branch: str
    clone_url: str
    created_at: datetime


class RepositoryFilesQuery(BaseModel):
    support_level: str | None = Field(default=None, description="deep | generic | skip")
    path_prefix: str | None = None
    include_skipped: bool = True
    limit: int = Field(default=100, ge=1, le=500)
    offset: int = Field(default=0, ge=0)
