import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";
import { askRepository } from "../lib/api";
import { AskPage } from "./AskPage";

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
  fetchAskBudget: vi.fn(async () => ({
    requests_used: 1,
    requests_limit: 40,
    tokens_used: 0,
    tokens_limit: 200000,
    estimated_cost_usd: 0,
    cost_limit_usd: 2,
    exhausted: false,
    skipped_reason: null,
    remaining_requests: 39,
  })),
  askRepository: vi.fn(async () => ({
    repository_id: "repo-1",
    snapshot_id: "snap-1",
    question: "how does greeting work?",
    answer:
      "Based on retrieved repository evidence for: how does greeting work?\n\n- pkg/helpers.ts:1-10 (seed): export function greet()",
    status: "ok",
    citations: [
      {
        path: "pkg/helpers.ts",
        start_line: 1,
        end_line: 10,
        chunk_id: "chunk-1",
        valid: true,
        reason: "ok",
        raw: "pkg/helpers.ts:1-10",
      },
    ],
    evidence: [
      {
        chunk_id: "chunk-1",
        path: "pkg/helpers.ts",
        start_line: 1,
        end_line: 10,
        support_level: "deep",
        role: "seed",
        depth: 0,
        citation: "pkg/helpers.ts:1-10",
      },
    ],
    analysis: {
      kind: "natural_language",
      rewrite_applied: true,
      retrieval_queries: ["how does greeting work?", "greeting"],
      identifiers: [],
      paths: [],
    },
    validation: {
      ok: true,
      valid_count: 1,
      dropped_count: 0,
      errors: [],
    },
    context_depth: 1,
    context_tokens_used: 120,
    context_token_budget: 6000,
    ranked_chunk_ids: ["chunk-1"],
    model_provenance: { provider: "mock", mode: "deterministic" },
    cached: false,
    notes: [],
    budget: {
      requests_used: 2,
      requests_limit: 40,
      tokens_used: 0,
      tokens_limit: 200000,
      estimated_cost_usd: 0,
      cost_limit_usd: 2,
      exhausted: false,
      skipped_reason: null,
      remaining_requests: 38,
    },
  })),
}));

function wrap(ui: ReactNode) {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter>{ui}</MemoryRouter>
    </QueryClientProvider>,
  );
}

afterEach(() => {
  vi.clearAllMocks();
});

describe("AskPage", () => {
  it("renders ask form and shows validated answer", async () => {
    wrap(<AskPage />);

    expect(screen.getByRole("heading", { name: "Ask" })).toBeInTheDocument();
    expect(screen.getByLabelText("Ask question")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /^ask$/i })).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByLabelText("Repository")).toHaveValue("repo-1");
    });

    fireEvent.change(screen.getByLabelText("Ask question"), {
      target: { value: "how does greeting work?" },
    });

    const form = screen.getByLabelText("Ask question").closest("form");
    expect(form).not.toBeNull();
    fireEvent.submit(form!);

    await waitFor(() => {
      expect(askRepository).toHaveBeenCalled();
    });
    await waitFor(() => {
      expect(screen.getAllByText("pkg/helpers.ts:1-10").length).toBeGreaterThanOrEqual(1);
    });
    expect(screen.getByText("validated")).toBeInTheDocument();
    expect(screen.getByText(/Based on retrieved repository evidence/i)).toBeInTheDocument();
    expect(screen.getByText(/kind=natural_language/i)).toBeInTheDocument();
    expect(screen.getByText(/Prefer Search for cheap deterministic/i)).toBeInTheDocument();
    expect(screen.getByText(/Per-repo Ask budget/i)).toBeInTheDocument();
  });
});
