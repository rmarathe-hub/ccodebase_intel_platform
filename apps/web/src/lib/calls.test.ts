import { describe, expect, it } from "vitest";
import { confidenceLabel } from "./calls";

describe("confidenceLabel", () => {
  it("labels confidence values", () => {
    expect(confidenceLabel("resolved")).toBe("Resolved");
    expect(confidenceLabel("ambiguous")).toBe("Ambiguous");
    expect(confidenceLabel("unresolved")).toBe("Unresolved");
  });
});
