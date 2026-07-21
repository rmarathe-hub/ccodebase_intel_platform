import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import { JobProgress } from "./JobProgress";
import type { IndexingJob } from "../lib/jobs";

function job(overrides: Partial<IndexingJob> = {}): IndexingJob {
  return {
    id: "11111111-1111-1111-1111-111111111111",
    repository_id: "22222222-2222-2222-2222-222222222222",
    snapshot_id: null,
    status: "RUNNING",
    stage: "cloning",
    progress_percentage: 10,
    attempt_count: 1,
    max_attempts: 3,
    locked_by: "worker-1",
    locked_until: null,
    heartbeat_at: null,
    error_code: null,
    error_message: null,
    started_at: null,
    completed_at: null,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    ...overrides,
  };
}

describe("JobProgress states", () => {
  it("shows failure details when the job failed", () => {
    render(
      <MemoryRouter>
        <JobProgress
          job={job({
            status: "FAILED",
            stage: "cloning",
            progress_percentage: 10,
            error_code: "clone_failed",
            error_message: "remote rejected",
          })}
        />
      </MemoryRouter>,
    );
    expect(screen.getByText(/clone failed/i)).toBeInTheDocument();
    expect(screen.getByText(/remote rejected/i)).toBeInTheDocument();
  });

  it("shows humanized clone size limit guidance", () => {
    render(
      <MemoryRouter>
        <JobProgress
          job={job({
            status: "FAILED",
            error_code: "repo_too_large",
            error_message: "Repository size 999 exceeds limit",
          })}
        />
      </MemoryRouter>,
    );
    expect(screen.getByText(/exceeds clone size limit/i)).toBeInTheDocument();
    expect(screen.getByText(/GIT_CLONE_MAX_BYTES/i)).toBeInTheDocument();
  });

  it("exposes cancel control for running jobs", () => {
    const onCancel = vi.fn();
    render(
      <MemoryRouter>
        <JobProgress job={job({ status: "RUNNING" })} onCancel={onCancel} />
      </MemoryRouter>,
    );
    fireEvent.click(screen.getByRole("button", { name: /cancel indexing/i }));
    expect(onCancel).toHaveBeenCalledWith(job().id);
  });

  it("renders ready progress", () => {
    render(
      <MemoryRouter>
        <JobProgress
          job={job({
            status: "SUCCEEDED",
            stage: "completed",
            progress_percentage: 100,
          })}
        />
      </MemoryRouter>,
    );
    expect(screen.getByText("100% complete")).toBeInTheDocument();
    expect(screen.getAllByText("Ready").length).toBeGreaterThanOrEqual(1);
  });

  it("handles long unicode repository error messages", () => {
    const message = "失敗: " + "パス/".repeat(40);
    render(
      <MemoryRouter>
        <JobProgress
          job={job({
            status: "FAILED",
            error_code: "clone_failed",
            error_message: message,
          })}
        />
      </MemoryRouter>,
    );
    expect(screen.getByText(new RegExp("失敗"))).toBeInTheDocument();
  });
});
