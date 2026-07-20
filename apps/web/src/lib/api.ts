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

export function fetchRepositorySymbols(
  repositoryId: string,
  params: {
    kind?: string;
    path_prefix?: string;
    name_contains?: string;
    framework_role?: string;
    is_local_import?: boolean;
    limit?: number;
    offset?: number;
  } = {},
) {
  const query = new URLSearchParams();
  if (params.kind) query.set("kind", params.kind);
  if (params.path_prefix) query.set("path_prefix", params.path_prefix);
  if (params.name_contains) query.set("name_contains", params.name_contains);
  if (params.framework_role) query.set("framework_role", params.framework_role);
  if (params.is_local_import != null) {
    query.set("is_local_import", String(params.is_local_import));
  }
  if (params.limit != null) query.set("limit", String(params.limit));
  if (params.offset != null) query.set("offset", String(params.offset));
  const suffix = query.toString() ? `?${query.toString()}` : "";
  return request<import("./symbols").SymbolListResponse>(
    `/api/v1/repositories/${repositoryId}/symbols${suffix}`,
  );
}

export function fetchRepositoryCalls(
  repositoryId: string,
  params: {
    confidence?: string;
    caller_contains?: string;
    path_prefix?: string;
    limit?: number;
    offset?: number;
  } = {},
) {
  const query = new URLSearchParams();
  if (params.confidence) query.set("confidence", params.confidence);
  if (params.caller_contains) query.set("caller_contains", params.caller_contains);
  if (params.path_prefix) query.set("path_prefix", params.path_prefix);
  if (params.limit != null) query.set("limit", String(params.limit));
  if (params.offset != null) query.set("offset", String(params.offset));
  const suffix = query.toString() ? `?${query.toString()}` : "";
  return request<import("./calls").SymbolCallListResponse>(
    `/api/v1/repositories/${repositoryId}/calls${suffix}`,
  );
}

export function fetchSymbolCallers(repositoryId: string, symbolId: string, limit = 100) {
  return request<import("./calls").SymbolNeighborsResponse>(
    `/api/v1/repositories/${repositoryId}/symbols/${symbolId}/callers?limit=${limit}`,
  );
}

export function fetchSymbolCallees(repositoryId: string, symbolId: string, limit = 100) {
  return request<import("./calls").SymbolNeighborsResponse>(
    `/api/v1/repositories/${repositoryId}/symbols/${symbolId}/callees?limit=${limit}`,
  );
}

function graphQuery(params: import("./graphs").GraphQueryParams): string {
  const query = new URLSearchParams();
  if (params.language) query.set("language", params.language);
  if (params.support_level) query.set("support_level", params.support_level);
  if (params.relation_kind) query.set("relation_kind", params.relation_kind);
  if (params.confidence) query.set("confidence", params.confidence);
  if (params.path_prefix) query.set("path_prefix", params.path_prefix);
  if (params.local_imports_only != null) {
    query.set("local_imports_only", String(params.local_imports_only));
  }
  if (params.include_files != null) query.set("include_files", String(params.include_files));
  if (params.inferred != null) query.set("inferred", String(params.inferred));
  if (params.max_nodes != null) query.set("max_nodes", String(params.max_nodes));
  if (params.max_edges != null) query.set("max_edges", String(params.max_edges));
  if (params.symbol_id) query.set("symbol_id", params.symbol_id);
  if (params.depth != null) query.set("depth", String(params.depth));
  const suffix = query.toString() ? `?${query.toString()}` : "";
  return suffix;
}

export function fetchRepositoryModuleGraph(
  repositoryId: string,
  params: import("./graphs").GraphQueryParams = {},
) {
  return request<import("./graphs").RepositoryGraphResponse>(
    `/api/v1/repositories/${repositoryId}/graph/modules${graphQuery(params)}`,
  );
}

export function fetchRepositoryPackageGraph(
  repositoryId: string,
  params: import("./graphs").GraphQueryParams = {},
) {
  return request<import("./graphs").RepositoryGraphResponse>(
    `/api/v1/repositories/${repositoryId}/graph/packages${graphQuery(params)}`,
  );
}

export function fetchRepositoryDirectoryGraph(
  repositoryId: string,
  params: import("./graphs").GraphQueryParams = {},
) {
  return request<import("./graphs").RepositoryGraphResponse>(
    `/api/v1/repositories/${repositoryId}/graph/directories${graphQuery(params)}`,
  );
}

export function fetchRepositoryCallGraph(
  repositoryId: string,
  params: import("./graphs").GraphQueryParams & { symbol_id: string },
) {
  return request<import("./graphs").RepositoryGraphResponse>(
    `/api/v1/repositories/${repositoryId}/graph/calls${graphQuery(params)}`,
  );
}
