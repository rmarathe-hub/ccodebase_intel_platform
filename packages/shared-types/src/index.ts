export type SupportLevel = "deep" | "generic" | "skip";

export type JobStatus = "QUEUED" | "RUNNING" | "SUCCEEDED" | "FAILED" | "CANCELLED";

export type JobStage =
  | "queued"
  | "cloning"
  | "discovering_files"
  | "parsing"
  | "building_relationships"
  | "chunking"
  | "embedding"
  | "validating"
  | "completed";

export interface HealthResponse {
  status: string;
}

export interface ReadyResponse {
  status: string;
  database: boolean;
}

export interface ParsedGitHubRepository {
  owner: string;
  name: string;
  host: string;
  clone_url: string;
  canonical_https_url: string;
  full_name: string;
}

export interface IndexingJob {
  id: string;
  repository_id: string;
  snapshot_id: string | null;
  status: JobStatus;
  stage: JobStage | string;
  progress_percentage: number;
  attempt_count: number;
  max_attempts: number;
  locked_by: string | null;
  locked_until: string | null;
  heartbeat_at: string | null;
  error_code: string | null;
  error_message: string | null;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface RepositoryImportRequest {
  url: string;
}

export interface RepositoryImportResponse {
  repository: {
    id: string;
    host: string;
    owner_name: string;
    name: string;
    default_branch: string;
    clone_url: string;
  };
  job: IndexingJob;
  created_new_job: boolean;
}

export const JOB_STAGE_LABELS = [
  "Queued",
  "Cloning",
  "Discovering files",
  "Parsing",
  "Building relationships",
  "Chunking",
  "Embedding",
  "Validating",
  "Completed",
] as const;
