// Graph page: call-site table honesty (not an interactive diagram).
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { GraphPage } from "./GraphPage";

vi.mock("../lib/api", () => ({
  fetchRepositories: vi.fn(async () => [
    {
      id: "repo-1",
      host: "github.com",
      owner_name: "rmarathe-hub",
      name: "retail-retention-revenue-intel",
      default_branch: "main",
      clone_url: "https://github.com/rmarathe-hub/retail-retention-revenue-intel.git",
      created_at: "2026-01-01T00:00:00Z",
      updated_at: "2026-01-01T00:00:00Z",
    },
  ]),
  fetchRepositoryCalls: vi.fn(async () => ({
    repository_id: "repo-1",
    snapshot_id: "snap-1",
    total: 1,
    limit: 200,
    offset: 0,
    calls: [
      {
        id: "c1",
        source_file_id: "f1",
        path: "svc.py",
        caller_symbol_id: "s1",
        caller_qualified_name: "svc.main",
        raw_callee: "helper",
        qualified_expression: "helper",
        line: 4,
        candidate_qualified_name: "svc.helper",
        confidence: "resolved",
        language: "python",
        created_at: "2026-01-01T00:00:00Z",
      },
    ],
  })),
}));

function wrap(ui: ReactNode) {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(<QueryClientProvider client={client}>{ui}</QueryClientProvider>);
}

afterEach(() => {
  vi.clearAllMocks();
});

describe("GraphPage", () => {
  it("renders call-site verification table, not a canvas diagram", async () => {
    wrap(<GraphPage />);
    expect(screen.getByRole("heading", { name: "Graph" })).toBeInTheDocument();
    expect(screen.getByText(/call-site list/i)).toBeInTheDocument();
    expect(screen.queryByRole("img")).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: "resolved" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "ambiguous" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "unresolved" })).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText("svc.main")).toBeInTheDocument();
    });
    expect(screen.getByText("helper")).toBeInTheDocument();
  });
});
