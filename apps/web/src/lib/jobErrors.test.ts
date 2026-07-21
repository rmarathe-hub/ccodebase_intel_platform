import { describe, expect, it } from "vitest";
import { isCancellableStatus, jobErrorHint, jobErrorTitle } from "./jobErrors";

describe("jobErrors", () => {
  it("humanizes clone limit failures", () => {
    expect(jobErrorTitle("repo_too_large")).toMatch(/size limit/i);
    expect(jobErrorHint("repo_too_large")).toMatch(/GIT_CLONE_MAX_BYTES/i);
  });

  it("humanizes cancel", () => {
    expect(jobErrorTitle("cancelled")).toMatch(/cancelled/i);
    expect(isCancellableStatus("QUEUED")).toBe(true);
    expect(isCancellableStatus("SUCCEEDED")).toBe(false);
  });
});
