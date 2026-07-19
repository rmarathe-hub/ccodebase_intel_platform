// Frontend API client URL construction and error handling.
import { afterEach, describe, expect, it, vi } from "vitest";
import {
  apiBase,
  fetchRepositories,
  fetchRepositoryCalls,
  fetchRepositoryFiles,
  fetchRepositorySymbols,
  fetchSymbolCallees,
  fetchSymbolCallers,
  importRepository,
  retryJob,
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
