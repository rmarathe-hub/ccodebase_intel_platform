import { describe, expect, it } from "vitest";
import { layoutGraphPositions, shortLabel, type GraphEdge, type GraphNode } from "./graphs";

describe("graphs helpers", () => {
  it("layouts nodes by edge layers", () => {
    const nodes: GraphNode[] = [
      {
        id: "a",
        label: "a",
        node_type: "module",
        language: "python",
        support_level: "deep",
        path: null,
        symbol_count: 0,
        file_count: 0,
        symbol_id: null,
        kind: null,
      },
      {
        id: "b",
        label: "b",
        node_type: "module",
        language: "python",
        support_level: "deep",
        path: null,
        symbol_count: 0,
        file_count: 0,
        symbol_id: null,
        kind: null,
      },
    ];
    const edges: GraphEdge[] = [
      {
        source: "a",
        target: "b",
        relation_kind: "imports",
        confidence: "resolved",
        language: "python",
        weight: 1,
        inferred: false,
        line: null,
      },
    ];
    const pos = layoutGraphPositions(nodes, edges);
    expect(pos.get("a")?.x).toBe(0);
    expect(pos.get("b")?.x).toBeGreaterThan(0);
  });

  it("shortens long labels", () => {
    expect(shortLabel("short")).toBe("short");
    expect(shortLabel("com.example.demo.user.UserServiceImpl", 20).startsWith("…")).toBe(true);
  });
});
