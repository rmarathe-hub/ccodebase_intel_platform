// Frontend API client URL construction and error handling.
import { afterEach, describe, expect, it, vi } from "vitest";
import {
  apiBase,
  fetchRepositories,
  fetchRepositoryCalls,
  fetchRepositoryChunksSearch,
  fetchRepositoryDirectoryGraph,
  fetchRepositoryFiles,
  fetchRepositoryModuleGraph,
  fetchRepositorySymbols,
  fetchSymbolCallees,
  fetchSymbolCallers,
  importRepository,
  reindexRepository,
  retryJob,
  cancelJob,
} from "./api";

afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe("api client", () => {
  it("exposes a default api base", () => {
    expect(apiBase).toMatch(/^https?:\/\//);
  });

  it("posts import payloads", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ repository: { id: "r1" }, job: { id: "j1" }, created_new_job: true }),
    });
    vi.stubGlobal("fetch", fetchMock);

    await importRepository("https://github.com/rmarathe-hub/retail-retention-revenue-intel");
    expect(fetchMock).toHaveBeenCalledOnce();
    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url).toContain("/api/v1/repositories/import");
    expect(init.method).toBe("POST");
    expect(JSON.parse(String(init.body))).toEqual({
      url: "https://github.com/rmarathe-hub/retail-retention-revenue-intel",
    });
  });

  it("posts import payloads with optional branch", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ repository: { id: "r1" }, job: { id: "j1" }, created_new_job: true }),
    });
    vi.stubGlobal("fetch", fetchMock);

    await importRepository(
      "https://github.com/rmarathe-hub/retail-retention-revenue-intel",
      "develop",
    );
    expect(JSON.parse(String(fetchMock.mock.calls[0]?.[1]?.body))).toEqual({
      url: "https://github.com/rmarathe-hub/retail-retention-revenue-intel",
      branch: "develop",
    });
  });

  it("builds files query strings", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ files: [], total: 0 }),
    });
    vi.stubGlobal("fetch", fetchMock);

    await fetchRepositoryFiles("repo-1", {
      support_level: "deep",
      path_prefix: "src",
      include_skipped: false,
      limit: 10,
      offset: 5,
    });
    const [url] = fetchMock.mock.calls[0] as [string];
    expect(url).toContain("/api/v1/repositories/repo-1/files?");
    expect(url).toContain("support_level=deep");
    expect(url).toContain("path_prefix=src");
    expect(url).toContain("include_skipped=false");
    expect(url).toContain("limit=10");
    expect(url).toContain("offset=5");
  });

  it("builds symbols and calls query strings", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ symbols: [], calls: [], total: 0 }),
    });
    vi.stubGlobal("fetch", fetchMock);

    await fetchRepositorySymbols("repo-1", {
      kind: "function",
      framework_role: "fastapi_route",
      is_local_import: true,
    });
    const symbolsUrl = String(fetchMock.mock.calls.at(0)?.[0] ?? "");
    expect(symbolsUrl).toContain("framework_role=fastapi_route");
    expect(symbolsUrl).toContain("is_local_import=true");

    await fetchRepositoryCalls("repo-1", { confidence: "resolved", caller_contains: "main" });
    const callsUrl = String(fetchMock.mock.calls.at(1)?.[0] ?? "");
    expect(callsUrl).toContain("confidence=resolved");
    expect(callsUrl).toContain("caller_contains=main");
  });

  it("builds neighbor endpoints", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ calls: [], total: 0, direction: "callers" }),
    });
    vi.stubGlobal("fetch", fetchMock);
    await fetchSymbolCallers("r", "s", 25);
    await fetchSymbolCallees("r", "s", 25);
    expect(String(fetchMock.mock.calls.at(0)?.[0] ?? "")).toContain(
      "/symbols/s/callers?limit=25",
    );
    expect(String(fetchMock.mock.calls.at(1)?.[0] ?? "")).toContain(
      "/symbols/s/callees?limit=25",
    );
  });

  it("builds graph query strings", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ nodes: [], edges: [], node_count: 0, edge_count: 0 }),
    });
    vi.stubGlobal("fetch", fetchMock);

    await fetchRepositoryModuleGraph("repo-1", {
      language: "python",
      local_imports_only: true,
      max_nodes: 50,
    });
    const modulesUrl = String(fetchMock.mock.calls.at(0)?.[0] ?? "");
    expect(modulesUrl).toContain("/graph/modules?");
    expect(modulesUrl).toContain("language=python");
    expect(modulesUrl).toContain("local_imports_only=true");
    expect(modulesUrl).toContain("max_nodes=50");

    await fetchRepositoryDirectoryGraph("repo-1", {
      path_prefix: "docs",
      include_files: true,
    });
    const dirsUrl = String(fetchMock.mock.calls.at(1)?.[0] ?? "");
    expect(dirsUrl).toContain("/graph/directories?");
    expect(dirsUrl).toContain("path_prefix=docs");
    expect(dirsUrl).toContain("include_files=true");
  });

  it("builds chunk search query strings", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ hits: [], total: 0, search_mode: "hybrid" }),
    });
    vi.stubGlobal("fetch", fetchMock);

    await fetchRepositoryChunksSearch("repo-1", {
      q: "UserService",
      search_mode: "hybrid",
      language: "python",
      path_prefix: "src",
      support_level: "deep",
      limit: 25,
    });
    const [url] = fetchMock.mock.calls[0] as [string];
    expect(url).toContain("/api/v1/repositories/repo-1/chunks/search?");
    expect(url).toContain("q=UserService");
    expect(url).toContain("search_mode=hybrid");
    expect(url).toContain("language=python");
    expect(url).toContain("path_prefix=src");
    expect(url).toContain("support_level=deep");
    expect(url).toContain("limit=25");
  });

  it("posts ask payloads", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        repository_id: "repo-1",
        snapshot_id: "snap-1",
        question: "hello",
        answer: "hi",
        status: "ok",
        citations: [],
        evidence: [],
        analysis: null,
        validation: { ok: true, valid_count: 0, dropped_count: 0, errors: [] },
        context_depth: 1,
        context_tokens_used: 0,
        context_token_budget: 6000,
        ranked_chunk_ids: [],
        model_provenance: null,
        cached: false,
        notes: [],
      }),
    });
    vi.stubGlobal("fetch", fetchMock);

    const { askRepository } = await import("./api");
    await askRepository("repo-1", {
      question: "how does greeting work?",
      apply_rerank: true,
      expand: false,
    });
    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url).toContain("/api/v1/repositories/repo-1/ask");
    expect(init.method).toBe("POST");
    expect(JSON.parse(String(init.body))).toEqual({
      question: "how does greeting work?",
      apply_rerank: true,
      expand: false,
    });
  });

  it("posts cancel and reindex", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ id: "j1", status: "CANCELLED" }),
    });
    vi.stubGlobal("fetch", fetchMock);

    await cancelJob("j1");
    expect(String(fetchMock.mock.calls[0]?.[0])).toContain("/api/v1/jobs/j1/cancel");
    expect((fetchMock.mock.calls[0]?.[1] as RequestInit).method).toBe("POST");

    fetchMock.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        repository: { id: "r1" },
        job: { id: "j2" },
        created_new_job: true,
      }),
    });
    await reindexRepository("r1");
    expect(String(fetchMock.mock.calls[1]?.[0])).toContain("/api/v1/repositories/r1/reindex");
  });

  it("throws on non-ok responses without inventing success", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
        text: async () => "boom",
      }),
    );
    await expect(fetchRepositories()).rejects.toThrow(/boom|500/);
    await expect(retryJob("j1")).rejects.toThrow();
  });
});
