import { describe, expect, it } from "vitest";
import { citationLabel, searchModeLabel, type ChunkSearchHit } from "./chunks";

describe("chunks helpers", () => {
  it("labels search modes", () => {
    expect(searchModeLabel("exact")).toBe("Exact");
    expect(searchModeLabel("semantic")).toBe("Semantic");
    expect(searchModeLabel("rrf")).toBe("RRF");
    expect(searchModeLabel("rerank")).toBe("Rerank");
  });

  it("formats citations as path:start-end", () => {
    const hit = {
      path: "pkg/service.py",
      start_line: 4,
      end_line: 12,
    } as ChunkSearchHit;
    expect(citationLabel(hit)).toBe("pkg/service.py:4-12");
  });
});
