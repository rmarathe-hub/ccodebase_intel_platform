import { describe, expect, it } from "vitest";
import { isTerminalStatus, stageIndex, JOB_STAGES, type JobStatus } from "./jobs";

describe("jobs helpers", () => {
  it("maps every pipeline stage to a stable index", () => {
    expect(JOB_STAGES).toHaveLength(9);
    expect(stageIndex("queued")).toBe(0);
    expect(stageIndex("cloning")).toBe(1);
    expect(stageIndex("completed")).toBe(8);
    expect(stageIndex("unknown-stage")).toBe(0);
  });

  it.each([
    ["SUCCEEDED", true],
    ["FAILED", true],
    ["CANCELLED", true],
    ["QUEUED", false],
    ["RUNNING", false],
  ] as Array<[JobStatus, boolean]>)("isTerminalStatus(%s) === %s", (status, expected) => {
    expect(isTerminalStatus(status)).toBe(expected);
  });

  it("keeps stage labels aligned with the Week 2 UI contract", () => {
    expect(JOB_STAGES.map((s) => s.label)).toEqual([
      "Queued",
      "Cloning",
      "Discovering files",
      "Parsing",
      "Building relationships",
      "Chunking",
      "Embedding",
      "Validating",
      "Ready",
    ]);
  });
});
