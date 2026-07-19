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
