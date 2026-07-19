from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.entities import SnapshotStatus
from app.schemas.jobs import IndexingJobRead
from app.schemas.repositories import RepositoryRead


class SnapshotRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    repository_id: UUID
    branch: str
    commit_sha: str
    file_count: int = Field(ge=0)
    status: SnapshotStatus
    created_at: datetime


class RepositoryImportResponse(BaseModel):
    repository: RepositoryRead
    job: IndexingJobRead
    created_new_job: bool
