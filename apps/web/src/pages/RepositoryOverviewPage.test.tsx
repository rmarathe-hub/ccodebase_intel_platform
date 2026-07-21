import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";
import { reindexRepository } from "../lib/api";
import { RepositoryOverviewPage } from "./RepositoryOverviewPage";

vi.mock("../lib/api", async () => {
  const actual = await vi.importActual<typeof import("../lib/api")>("../lib/api");
  return {
    ...actual,
    fetchRepositories: vi.fn(async () => [
      {
        id: "repo-a",
        host: "github.com",
        owner_name: "acme",
        name: "alpha",
        default_branch: "main",
        clone_url: "https://github.com/acme/alpha.git",
        created_at: "2026-01-01T00:00:00Z",
      },
      {
        id: "repo-b",
        host: "github.com",
        owner_name: "acme",
        name: "beta",
        default_branch: "develop",
        clone_url: "https://github.com/acme/beta.git",
        created_at: "2026-01-02T00:00:00Z",
      },
    ]),
    fetchRepositorySummary: vi.fn(async () => ({
      repository_id: "repo-a",
      snapshot_id: "snap-1",
      deterministic_summary: {
        language_mix: { python: 10, go: 2 },
        support_level_mix: { deep: 10, generic: 2, skip: 1 },
        important_directories: ["src"],
        test_directories: ["tests"],
        documentation_directories: ["docs"],
        build_systems: [],
        configuration_files: [],
        documentation_files: [],
        entry_point_candidates: [],
        chunk_counts: {},
        parser_coverage: {},
        skipped_file_counts: {},
        file_count: 13,
      },
      llm_summary: null,
      llm_summary_status: "skipped",
      evidence: [],
      model_provenance: null,
    })),
    fetchRepositoryJobs: vi.fn(async () => [
      {
        id: "job-1",
        repository_id: "repo-a",
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
      },
    ]),
    reindexRepository: vi.fn(async () => ({
      repository: {
        id: "repo-a",
        host: "github.com",
        owner_name: "acme",
        name: "alpha",
        default_branch: "main",
        clone_url: "https://github.com/acme/alpha.git",
      },
      job: {
        id: "job-2",
        repository_id: "repo-a",
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
        created_at: "2026-01-01T00:02:00Z",
        updated_at: "2026-01-01T00:02:00Z",
      },
      created_new_job: true,
    })),
  };
});

function wrap(ui: ReactNode, initial = "/repositories/repo-a") {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={[initial]}>
        <Routes>
          <Route path="/repositories" element={ui} />
          <Route path="/repositories/:id" element={ui} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

afterEach(() => {
  vi.clearAllMocks();
});

describe("RepositoryOverviewPage", () => {
  it("lists repos, shows support honesty, and queues re-index", async () => {
    wrap(<RepositoryOverviewPage />);

    await waitFor(() => {
      expect(screen.getAllByText(/acme\/alpha/).length).toBeGreaterThanOrEqual(1);
    });
    expect(screen.getAllByText(/acme\/beta/).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText(/Partial support/i)).toBeInTheDocument();
    expect(screen.getByText("Deep")).toBeInTheDocument();
    expect(screen.getByText("Generic")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: /re-index/i }));
    await waitFor(() => {
      expect(reindexRepository).toHaveBeenCalled();
    });
  });

  it("switches repository via list selection", async () => {
    wrap(<RepositoryOverviewPage />);
    await waitFor(() => {
      expect(screen.getByRole("button", { name: /acme\/beta/i })).toBeInTheDocument();
    });
    fireEvent.click(screen.getByRole("button", { name: /acme\/beta/i }));
    await waitFor(() => {
      expect(screen.getByRole("button", { name: /acme\/beta/i }).className).toMatch(
        /accent/,
      );
    });
  });
});
