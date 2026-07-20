export type GraphType = "modules" | "packages" | "directories" | "calls";

export type GraphNode = {
  id: string;
  label: string;
  node_type: string;
  language: string | null;
  support_level: string;
  path: string | null;
  symbol_count: number;
  file_count: number;
  symbol_id: string | null;
  kind: string | null;
};

export type GraphEdge = {
  source: string;
  target: string;
  relation_kind: string;
  confidence: string;
  language: string | null;
  weight: number;
  inferred: boolean;
  line: number | null;
};

export type RepositoryGraphResponse = {
  repository_id: string;
  snapshot_id: string | null;
  graph_type: string;
  node_count: number;
  edge_count: number;
  center_symbol_id: string | null;
  depth: number | null;
  filters: Record<string, unknown>;
  nodes: GraphNode[];
  edges: GraphEdge[];
};

export type GraphQueryParams = {
  language?: string;
  support_level?: string;
  relation_kind?: string;
  confidence?: string;
  path_prefix?: string;
  local_imports_only?: boolean;
  include_files?: boolean;
  inferred?: boolean;
  max_nodes?: number;
  max_edges?: number;
  symbol_id?: string;
  depth?: number;
};

/** Deterministic layered layout from edge directions (no external layout lib). */
export function layoutGraphPositions(
  nodes: GraphNode[],
  edges: GraphEdge[],
): Map<string, { x: number; y: number }> {
  const ids = nodes.map((n) => n.id);
  const idSet = new Set(ids);
  const outgoing = new Map<string, string[]>();
  const indegree = new Map<string, number>();
  for (const id of ids) {
    outgoing.set(id, []);
    indegree.set(id, 0);
  }
  for (const edge of edges) {
    if (!idSet.has(edge.source) || !idSet.has(edge.target)) continue;
    outgoing.get(edge.source)?.push(edge.target);
    indegree.set(edge.target, (indegree.get(edge.target) ?? 0) + 1);
  }

  const layer = new Map<string, number>();
  const queue = ids.filter((id) => (indegree.get(id) ?? 0) === 0);
  for (const id of queue) layer.set(id, 0);
  let qi = 0;
  while (qi < queue.length) {
    const cur = queue[qi++]!;
    const curLayer = layer.get(cur) ?? 0;
    for (const next of outgoing.get(cur) ?? []) {
      const nextLayer = Math.max(layer.get(next) ?? 0, curLayer + 1);
      if (!layer.has(next) || nextLayer > (layer.get(next) ?? 0)) {
        layer.set(next, nextLayer);
      }
      const remaining = (indegree.get(next) ?? 1) - 1;
      indegree.set(next, remaining);
      if (remaining <= 0 && !queue.includes(next)) {
        queue.push(next);
      }
    }
  }
  for (const id of ids) {
    if (!layer.has(id)) layer.set(id, 0);
  }

  const byLayer = new Map<number, string[]>();
  for (const id of ids) {
    const L = layer.get(id) ?? 0;
    const list = byLayer.get(L) ?? [];
    list.push(id);
    byLayer.set(L, list);
  }

  const positions = new Map<string, { x: number; y: number }>();
  const xGap = 220;
  const yGap = 90;
  for (const [L, layerIds] of [...byLayer.entries()].sort((a, b) => a[0] - b[0])) {
    layerIds.sort();
    const offsetY = ((layerIds.length - 1) * yGap) / 2;
    layerIds.forEach((id, index) => {
      positions.set(id, { x: L * xGap, y: index * yGap - offsetY });
    });
  }
  return positions;
}

export function shortLabel(label: string, max = 28): string {
  if (label.length <= max) return label;
  return `…${label.slice(-(max - 1))}`;
}
