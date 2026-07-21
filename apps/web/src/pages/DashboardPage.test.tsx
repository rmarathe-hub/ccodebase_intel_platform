import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";
import { importRepository } from "../lib/api";
import { DashboardPage } from "./DashboardPage";

vi.mock("../lib/api", async () => {
  const actual = await vi.importActual<typeof import("../lib/api")>("../lib/api");
  return {
    ...actual,
    importRepository: vi.fn(async () => ({
      repository: {
        id: "repo-1",
        host: "github.com",
        owner_name: "rmarathe-hub",
        name: "demo-repo",
        default_branch: "main",
        clone_url: "https://github.com/rmarathe-hub/demo-repo.git",
      },
      job: {
        id: "job-1",
        repository_id: "repo-1",
        snapshot_id: null,
        status: "QUEUED",
        stage: "queued",
        progress_percentage: 0,
        attempt_count: 0,
        max_attempts: 3,
        locked_by: null,
        locked_until: null,
        heartbeat_at: null,
        error_code: null,
        error_message: null,
        started_at: null,
        completed_at: null,
        created_at: "2026-01-01T00:00:00Z",
        updated_at: "2026-01-01T00:00:00Z",
      },
      created_new_job: true,
    })),
    fetchJob: vi.fn(async () => ({
      id: "job-1",
      repository_id: "repo-1",
      snapshot_id: "snap-1",
      status: "SUCCEEDED",
      stage: "completed",
      progress_percentage: 100,
      attempt_count: 1,
      max_attempts: 3,
      locked_by: null,
      locked_until: null,
      heartbeat_at: null,
      error_code: null,
      error_message: null,
      started_at: null,
      completed_at: "2026-01-01T00:01:00Z",
      created_at: "2026-01-01T00:00:00Z",
      updated_at: "2026-01-01T00:01:00Z",
    })),
  };
});

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

describe("DashboardPage import UX", () => {
  it("starts indexing from a pasted URL and shows Ready workspace links", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ status: "ok" }),
      }),
    );

    wrap(<DashboardPage />);

    expect(screen.getByRole("heading", { name: "Dashboard" })).toBeInTheDocument();
    expect(screen.getByLabelText("Repository URL")).toBeInTheDocument();
    expect(screen.getByLabelText("Branch")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /start indexing/i })).toBeInTheDocument();

    const form = screen.getByLabelText("Repository URL").closest("form");
    expect(form).not.toBeNull();
    fireEvent.submit(form!);

    await waitFor(() => {
      expect(importRepository).toHaveBeenCalled();
    });

    await waitFor(() => {
      expect(screen.getByText(/Repository is Ready/i)).toBeInTheDocument();
    });
    expect(screen.getAllByRole("link", { name: "Search" }).length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByRole("link", { name: "Ask" }).length).toBeGreaterThanOrEqual(1);
  });
});
