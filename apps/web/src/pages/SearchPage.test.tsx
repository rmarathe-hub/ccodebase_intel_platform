// Search page: exact / semantic / hybrid chunk search UI.
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { SearchPage } from "./SearchPage";

vi.mock("../lib/api", () => ({
  fetchRepositories: vi.fn(async () => [
    {
      id: "repo-1",
      host: "github.com",
      owner_name: "rmarathe-hub",
      name: "demo-repo",
      default_branch: "main",
      clone_url: "https://github.com/rmarathe-hub/demo-repo.git",
      created_at: "2026-01-01T00:00:00Z",
      updated_at: "2026-01-01T00:00:00Z",
    },
  ]),
  fetchRepositoryChunksSearch: vi.fn(async () => ({
    repository_id: "repo-1",
    snapshot_id: "snap-1",
    query: "UserService",
    total: 1,
    limit: 50,
    offset: 0,
    search_mode: "exact",
    hits: [
      {
        id: "chunk-1",
        path: "src/UserService.py",
        language: "python",
        support_level: "deep",
        chunk_type: "function",
        start_line: 10,
        end_line: 20,
        content: "class UserService:\n    def get(self):\n        return 1\n",
        content_hash: "abc",
        extraction_method: "symbol",
        parser_name: "python-ast",
        parser_version: "1",
        verified_deep: true,
        llm_enriched: false,
        validation_status: null,
        semantic_label: null,
        concise_summary: null,
        parent_context: null,
        created_at: "2026-01-01T00:00:00Z",
        score: 1,
        score_breakdown: { exact: 1, semantic: 0, fused: 1 },
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

describe("SearchPage", () => {
  it("renders a working search form and results", async () => {
    wrap(<SearchPage />);

    expect(screen.getByRole("heading", { name: "Search" })).toBeInTheDocument();
    expect(screen.getByLabelText("Search query")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /search/i })).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText("Search query"), {
      target: { value: "UserService" },
    });
    fireEvent.click(screen.getByRole("button", { name: /search/i }));

    await waitFor(() => {
      expect(screen.getByText("src/UserService.py:10-20")).toBeInTheDocument();
    });
    expect(screen.getByText(/verified deep/i)).toBeInTheDocument();
    expect(
      screen.getByText(/Full Ask answers are Week 10/i),
    ).toBeInTheDocument();
  });
});
