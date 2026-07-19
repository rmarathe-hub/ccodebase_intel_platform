export type SupportLevel = "deep" | "generic" | "skip";

export type JobStatus = "QUEUED" | "RUNNING" | "SUCCEEDED" | "FAILED" | "CANCELLED";

export interface HealthResponse {
  status: string;
}

export interface ReadyResponse {
  status: string;
  database: boolean;
}
