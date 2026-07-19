import { describe, expect, it } from "vitest";
import { symbolKindLabel } from "./symbols";

describe("symbolKindLabel", () => {
  it("labels known kinds", () => {
    expect(symbolKindLabel("class")).toBe("Class");
    expect(symbolKindLabel("function")).toBe("Function");
    expect(symbolKindLabel("method")).toBe("Method");
    expect(symbolKindLabel("import")).toBe("Import");
  });

  it("passes through unknown kinds", () => {
    expect(symbolKindLabel("heuristic")).toBe("heuristic");
  });
});
