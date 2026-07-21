import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import { JobProgress } from "./JobProgress";
import type { IndexingJob } from "../lib/jobs";

const baseJob: IndexingJob = {
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
};

describe("JobProgress", () => {
  it("renders all pipeline stages", () => {
    render(
      <MemoryRouter>
        <JobProgress job={baseJob} />
      </MemoryRouter>,
    );
    expect(screen.getByText("Queued")).toBeInTheDocument();
    expect(screen.getByText("Cloning")).toBeInTheDocument();
    expect(screen.getByText("Discovering files")).toBeInTheDocument();
    expect(screen.getByText("Parsing")).toBeInTheDocument();
    expect(screen.getByText("Building relationships")).toBeInTheDocument();
    expect(screen.getByText("Chunking")).toBeInTheDocument();
    expect(screen.getByText("Embedding")).toBeInTheDocument();
    expect(screen.getByText("Validating")).toBeInTheDocument();
    expect(screen.getByText("Ready")).toBeInTheDocument();
    expect(screen.getByText("10% complete")).toBeInTheDocument();
  });

  it("shows workspace links when Ready", () => {
    render(
      <MemoryRouter>
        <JobProgress
          job={{
            ...baseJob,
            status: "SUCCEEDED",
            stage: "completed",
            progress_percentage: 100,
          }}
          showWorkspaceLinks
        />
      </MemoryRouter>,
    );
    expect(screen.getByRole("link", { name: "Search" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Ask" })).toBeInTheDocument();
  });
});
