import { describe, expect, it } from "vitest";
import { askCitationLabel, askStatusLabel } from "./ask";

describe("ask helpers", () => {
  it("formats citation labels", () => {
    expect(askCitationLabel({ path: "a.py", start_line: 1, end_line: 3 })).toBe("a.py:1-3");
  });

  it("labels known statuses", () => {
    expect(askStatusLabel("ok")).toBe("OK");
    expect(askStatusLabel("ask_disabled")).toBe("Ask disabled");
    expect(askStatusLabel("partial")).toMatch(/Partial/i);
  });
});
