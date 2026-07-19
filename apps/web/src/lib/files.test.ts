import { describe, expect, it } from "vitest";
import { supportLevelLabel } from "./files";

describe("files helpers", () => {
  it("labels support levels for UI", () => {
    expect(supportLevelLabel("deep")).toBe("Deep");
    expect(supportLevelLabel("generic")).toBe("Generic");
    expect(supportLevelLabel("skip")).toBe("Skip");
    expect(supportLevelLabel("other")).toBe("other");
  });
});
