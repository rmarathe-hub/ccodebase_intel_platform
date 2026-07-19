const apiBase = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${apiBase}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed (${response.status})`);
  }
  return response.json() as Promise<T>;
}

export { apiBase };

export function importRepository(url: string) {
  return request<import("./jobs").RepositoryImportResponse>("/api/v1/repositories/import", {
    method: "POST",
    body: JSON.stringify({ url }),
  });
}

export function fetchJob(jobId: string) {
  return request<import("./jobs").IndexingJob>(`/api/v1/jobs/${jobId}`);
}

export function fetchJobs(limit = 50) {
  return request<import("./jobs").IndexingJob[]>(`/api/v1/jobs?limit=${limit}`);
}

export function retryJob(jobId: string) {
  return request<import("./jobs").IndexingJob>(`/api/v1/jobs/${jobId}/retry`, {
    method: "POST",
  });
}

export function fetchRepositories(limit = 50) {
  return request<import("./files").RepositoryListItem[]>(`/api/v1/repositories?limit=${limit}`);
}

export function fetchRepositoryFiles(
  repositoryId: string,
  params: {
    support_level?: string;
    path_prefix?: string;
    include_skipped?: boolean;
    limit?: number;
    offset?: number;
  } = {},
) {
  const query = new URLSearchParams();
  if (params.support_level) query.set("support_level", params.support_level);
  if (params.path_prefix) query.set("path_prefix", params.path_prefix);
  if (params.include_skipped === false) query.set("include_skipped", "false");
  if (params.limit != null) query.set("limit", String(params.limit));
  if (params.offset != null) query.set("offset", String(params.offset));
  const suffix = query.toString() ? `?${query.toString()}` : "";
  return request<import("./files").SourceFileListResponse>(
    `/api/v1/repositories/${repositoryId}/files${suffix}`,
  );
}
