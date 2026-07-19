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

export interface RepositorySummary {
  id: string;
  host: string;
  owner_name: string;
  name: string;
  default_branch: string;
  clone_url: string;
}

export interface RepositoryImportResponse {
  repository: RepositorySummary;
  job: IndexingJob;
  created_new_job: boolean;
}

export const JOB_STAGES: Array<{ id: JobStage; label: string }> = [
  { id: "queued", label: "Queued" },
  { id: "cloning", label: "Cloning" },
  { id: "discovering_files", label: "Discovering files" },
  { id: "parsing", label: "Parsing" },
  { id: "building_relationships", label: "Building relationships" },
  { id: "chunking", label: "Chunking" },
  { id: "embedding", label: "Embedding" },
  { id: "validating", label: "Validating" },
  { id: "completed", label: "Completed" },
];

export function stageIndex(stage: string): number {
  const index = JOB_STAGES.findIndex((item) => item.id === stage);
  return index >= 0 ? index : 0;
}

export function isTerminalStatus(status: JobStatus): boolean {
  return status === "SUCCEEDED" || status === "FAILED" || status === "CANCELLED";
}
