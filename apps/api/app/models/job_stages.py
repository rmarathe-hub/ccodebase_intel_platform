"""Indexing job stage constants and helpers."""

from __future__ import annotations

import enum


class JobStage(enum.StrEnum):
    QUEUED = "queued"
    CLONING = "cloning"
    DISCOVERING_FILES = "discovering_files"
    PARSING = "parsing"
    BUILDING_RELATIONSHIPS = "building_relationships"
    CHUNKING = "chunking"
    EMBEDDING = "embedding"
    VALIDATING = "validating"
    COMPLETED = "completed"


JOB_STAGE_LABELS: dict[JobStage, str] = {
    JobStage.QUEUED: "Queued",
    JobStage.CLONING: "Cloning",
    JobStage.DISCOVERING_FILES: "Discovering files",
    JobStage.PARSING: "Parsing",
    JobStage.BUILDING_RELATIONSHIPS: "Building relationships",
    JobStage.CHUNKING: "Chunking",
    JobStage.EMBEDDING: "Embedding",
    JobStage.VALIDATING: "Validating",
    JobStage.COMPLETED: "Completed",
}


JOB_STAGE_PROGRESS: dict[JobStage, int] = {
    JobStage.QUEUED: 0,
    JobStage.CLONING: 10,
    JobStage.DISCOVERING_FILES: 25,
    JobStage.PARSING: 45,
    JobStage.BUILDING_RELATIONSHIPS: 60,
    JobStage.CHUNKING: 75,
    JobStage.EMBEDDING: 90,
    JobStage.VALIDATING: 95,
    JobStage.COMPLETED: 100,
}
