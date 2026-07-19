from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.entities import JobStatus
from app.models.job_stages import JobStage


class IndexingJobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    repository_id: UUID
    snapshot_id: UUID | None
    status: JobStatus
    stage: str
    progress_percentage: int = Field(ge=0, le=100)
    attempt_count: int = Field(ge=0)
    max_attempts: int = Field(ge=1)
    locked_by: str | None
    locked_until: datetime | None
    heartbeat_at: datetime | None
    error_code: str | None
    error_message: str | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class IndexingJobCreateDefaults(BaseModel):
    """Defaults applied when enqueueing a new indexing job."""

    status: JobStatus = JobStatus.QUEUED
    stage: JobStage = JobStage.QUEUED
    progress_percentage: int = 0
    attempt_count: int = 0
    max_attempts: int = 3
