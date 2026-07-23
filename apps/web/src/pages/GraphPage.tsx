import {
  Background,
  Controls,
  MarkerType,
  MiniMap,
  ReactFlow,
  ReactFlowProvider,
  type Edge,
  type Node,
  type NodeMouseHandler,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { useQuery } from "@tanstack/react-query";
import { useCallback, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { PageShell } from "../components/PageShell";
import {
  fetchRepositories,
  fetchRepositoryCallGraph,
  fetchRepositoryDirectoryGraph,
  fetchRepositoryModuleGraph,
  fetchRepositoryPackageGraph,
  fetchRepositorySymbols,
} from "../lib/api";
import {
  layoutGraphPositions,
  shortLabel,
  type GraphType,
  type RepositoryGraphResponse,
} from "../lib/graphs";
import { useRepoQueryParam } from "../lib/useRepoQueryParam";

const GRAPH_TYPES: Array<{ id: GraphType; label: string }> = [
  { id: "modules", label: "Modules" },
  { id: "packages", label: "Packages" },
  { id: "directories", label: "Directories" },
  { id: "calls", label: "Calls" },
];

const selectClass =
  "rounded-md border border-[var(--border)] bg-[color-mix(in_srgb,var(--bg)_70%,black)] px-3 py-2 text-sm outline-none ring-[var(--accent)] focus:ring-2";

function nodeColor(supportLevel: string): string {
  if (supportLevel === "deep") return "#3d8bfd";
  if (supportLevel === "generic") return "#7a8aa0";
  if (supportLevel === "mixed") return "#c9a227";
  return "#5a6a7e";
}

function toFlowElements(graph: RepositoryGraphResponse): { nodes: Node[]; edges: Edge[] } {
  const positions = layoutGraphPositions(graph.nodes, graph.edges);
  const nodes: Node[] = graph.nodes.map((n) => {
    const pos = positions.get(n.id) ?? { x: 0, y: 0 };
    const isCenter = graph.center_symbol_id != null && n.symbol_id === graph.center_symbol_id;
    const clickable = Boolean(n.path);
    return {
      id: n.id,
      position: pos,
      data: {
        label: shortLabel(n.label),
        fullLabel: n.label,
        nodeType: n.node_type,
        supportLevel: n.support_level,
        language: n.language,
        path: n.path,
        symbolId: n.symbol_id,
        clickable,
      },
      style: {
        background: "color-mix(in srgb, var(--panel) 92%, black)",
        border: `1px solid ${isCenter ? "var(--accent)" : "var(--border)"}`,
        borderRadius: 8,
        color: "var(--text)",
        fontSize: 11,
        padding: "6px 10px",
        minWidth: 120,
        boxShadow: isCenter ? "0 0 0 1px var(--accent)" : undefined,
        cursor: clickable ? "pointer" : "default",
      },
    };
  });
  const edges: Edge[] = graph.edges.map((e, index) => ({
    id: `${e.source}->${e.target}:${e.relation_kind}:${index}`,
    source: e.source,
    target: e.target,
    label: e.relation_kind,
    animated: e.inferred,
    style: {
      stroke:
        e.confidence === "resolved"
          ? "#3d8bfd"
          : e.confidence === "ambiguous"
            ? "#c9a227"
            : "#7a8aa0",
    },
    markerEnd: { type: MarkerType.ArrowClosed, width: 14, height: 14 },
    labelStyle: { fill: "var(--muted)", fontSize: 10 },
  }));
  return { nodes, edges };
}

export function GraphPage() {
  const navigate = useNavigate();
  const reposQuery = useQuery({
    queryKey: ["repositories"],
    queryFn: () => fetchRepositories(50),
  });
  const { selectedId, selectRepository } = useRepoQueryParam(reposQuery.data?.[0]?.id || "");
  const [graphType, setGraphType] = useState<GraphType>("modules");
  const [language, setLanguage] = useState("all");
  const [supportLevel, setSupportLevel] = useState("all");
  const [confidence, setConfidence] = useState<"all" | "resolved" | "ambiguous" | "unresolved">(
    "all",
  );
  const [pathPrefix, setPathPrefix] = useState("");
  const [localImportsOnly, setLocalImportsOnly] = useState(true);
  const [includeFiles, setIncludeFiles] = useState(false);
  const [depth, setDepth] = useState(1);
  const [centerSymbolId, setCenterSymbolId] = useState("");
  const draggingRef = useRef(false);
  const [openError, setOpenError] = useState<string | null>(null);

  const symbolsQuery = useQuery({
    queryKey: ["graph-symbols", selectedId],
    queryFn: () =>
      fetchRepositorySymbols(selectedId, {
        kind: "function",
        limit: 100,
      }),
    enabled: Boolean(selectedId) && graphType === "calls",
  });

  const resolvedCenter =
    centerSymbolId ||
    symbolsQuery.data?.symbols.find((s) => s.kind === "function")?.id ||
    symbolsQuery.data?.symbols[0]?.id ||
    "";

  const graphQuery = useQuery({
    queryKey: [
      "repository-graph",
      selectedId,
      graphType,
      language,
      supportLevel,
      confidence,
      pathPrefix,
      localImportsOnly,
      includeFiles,
      depth,
      resolvedCenter,
    ],
    queryFn: async (): Promise<RepositoryGraphResponse> => {
      const common = {
        language: language === "all" ? undefined : language,
        support_level: supportLevel === "all" ? undefined : supportLevel,
        confidence: confidence === "all" ? undefined : confidence,
        path_prefix: pathPrefix.trim() || undefined,
        max_nodes: 150,
        max_edges: 300,
      };
      if (graphType === "modules") {
        return fetchRepositoryModuleGraph(selectedId, {
          ...common,
          local_imports_only: localImportsOnly,
        });
      }
      if (graphType === "packages") {
        return fetchRepositoryPackageGraph(selectedId, {
          ...common,
          local_imports_only: localImportsOnly,
        });
      }
      if (graphType === "directories") {
        return fetchRepositoryDirectoryGraph(selectedId, {
          support_level: common.support_level,
          confidence: common.confidence,
          path_prefix: common.path_prefix,
          include_files: includeFiles,
          max_nodes: common.max_nodes,
          max_edges: common.max_edges,
        });
      }
      if (!resolvedCenter) {
        return {
          repository_id: selectedId,
          snapshot_id: null,
          graph_type: "calls",
          node_count: 0,
          edge_count: 0,
          center_symbol_id: null,
          depth,
          filters: {},
          nodes: [],
          edges: [],
        };
      }
      return fetchRepositoryCallGraph(selectedId, {
        ...common,
        symbol_id: resolvedCenter,
        depth,
      });
    },
    enabled: Boolean(selectedId) && (graphType !== "calls" || Boolean(resolvedCenter) || symbolsQuery.isFetched),
  });

  const flow = useMemo(() => {
    if (!graphQuery.data) return { nodes: [] as Node[], edges: [] as Edge[] };
    return toFlowElements(graphQuery.data);
  }, [graphQuery.data]);

  const onNodeClick: NodeMouseHandler = useCallback(
    (_event, node) => {
      if (draggingRef.current) {
        draggingRef.current = false;
        return;
      }
      const data = node.data as {
        path?: string | null;
        symbolId?: string | null;
        clickable?: boolean;
      };
      if (!data.path) {
        setOpenError("This node has no file path to open.");
        return;
      }
      setOpenError(null);
      const q = new URLSearchParams({
        repo: selectedId,
        path: data.path,
      });
      if (data.symbolId) {
        q.set("symbol", data.symbolId);
        // Symbol nodes: jump near definition when viewer loads (line hint from API later).
        q.set("line", "1");
      }
      navigate(`/files/view?${q.toString()}`);
    },
    [navigate, selectedId],
  );

  const selectedRepo = useMemo(
    () => reposQuery.data?.find((repo) => repo.id === selectedId),
    [reposQuery.data, selectedId],
  );

  return (
    <div className="space-y-4">
      <PageShell
        title="Graph"
        description="Interactive structural graphs for the latest snapshot. Deep languages get module/package/call views; directories work for generic repos. Edges keep resolution confidence."
      />

      <section className="rounded-xl border border-[var(--border)] bg-[var(--panel)] p-6">
        <div className="flex flex-col gap-3">
          <div className="flex flex-col gap-3 lg:flex-row lg:items-end">
            <label className="flex min-w-0 flex-1 flex-col gap-1 text-sm">
              <span className="text-[var(--muted)]">Repository</span>
              <select
                className={selectClass}
                value={selectedId}
                onChange={(event) => selectRepository(event.target.value)}
                aria-label="Repository"
              >
                {(reposQuery.data ?? []).length === 0 && (
                  <option value="">No repositories imported yet</option>
                )}
                {(reposQuery.data ?? []).map((repo) => (
                  <option key={repo.id} value={repo.id}>
                    {repo.owner_name}/{repo.name}
                  </option>
                ))}
              </select>
            </label>
            <div className="flex flex-wrap gap-2" role="group" aria-label="Graph type">
              {GRAPH_TYPES.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  className={[
                    "rounded-md border px-3 py-1.5 text-sm",
                    graphType === item.id
                      ? "border-[var(--accent)] bg-[color-mix(in_srgb,var(--accent)_20%,transparent)]"
                      : "border-[var(--border)]",
                  ].join(" ")}
                  onClick={() => setGraphType(item.id)}
                >
                  {item.label}
                </button>
              ))}
            </div>
          </div>

          <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
            <label className="flex flex-col gap-1 text-sm">
              <span className="text-[var(--muted)]">Language</span>
              <select
                className={selectClass}
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                aria-label="Language"
              >
                <option value="all">All</option>
                <option value="python">Python</option>
                <option value="javascript">JavaScript</option>
                <option value="typescript">TypeScript</option>
                <option value="java">Java</option>
              </select>
            </label>
            <label className="flex flex-col gap-1 text-sm">
              <span className="text-[var(--muted)]">Support level</span>
              <select
                className={selectClass}
                value={supportLevel}
                onChange={(e) => setSupportLevel(e.target.value)}
                aria-label="Support level"
              >
                <option value="all">All</option>
                <option value="deep">Deep</option>
                <option value="generic">Generic</option>
                <option value="mixed">Mixed</option>
              </select>
            </label>
            <label className="flex flex-col gap-1 text-sm">
              <span className="text-[var(--muted)]">Confidence</span>
              <select
                className={selectClass}
                value={confidence}
                onChange={(e) =>
                  setConfidence(e.target.value as "all" | "resolved" | "ambiguous" | "unresolved")
                }
                aria-label="Confidence"
              >
                <option value="all">All</option>
                <option value="resolved">Resolved</option>
                <option value="ambiguous">Ambiguous</option>
                <option value="unresolved">Unresolved</option>
              </select>
            </label>
            <label className="flex flex-col gap-1 text-sm">
              <span className="text-[var(--muted)]">Path / directory prefix</span>
              <input
                className={selectClass}
                value={pathPrefix}
                onChange={(e) => setPathPrefix(e.target.value)}
                placeholder="e.g. src or docs"
                aria-label="Path prefix"
              />
            </label>
          </div>

          <div className="flex flex-wrap items-center gap-4 text-sm">
            {(graphType === "modules" || graphType === "packages") && (
              <label className="inline-flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={localImportsOnly}
                  onChange={(e) => setLocalImportsOnly(e.target.checked)}
                />
                Local imports only
              </label>
            )}
            {graphType === "directories" && (
              <label className="inline-flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={includeFiles}
                  onChange={(e) => setIncludeFiles(e.target.checked)}
                />
                Include files
              </label>
            )}
            {graphType === "calls" && (
              <>
                <label className="inline-flex items-center gap-2">
                  Depth
                  <select
                    className={selectClass}
                    value={depth}
                    onChange={(e) => setDepth(Number(e.target.value))}
                    aria-label="Call graph depth"
                  >
                    <option value={1}>1</option>
                    <option value={2}>2</option>
                    <option value={3}>3</option>
                  </select>
                </label>
                <label className="inline-flex min-w-[16rem] flex-1 flex-col gap-1">
                  <span className="text-[var(--muted)]">Center symbol</span>
                  <select
                    className={selectClass}
                    value={resolvedCenter}
                    onChange={(e) => setCenterSymbolId(e.target.value)}
                    aria-label="Center symbol"
                  >
                    {(symbolsQuery.data?.symbols ?? []).length === 0 && (
                      <option value="">No symbols yet</option>
                    )}
                    {(symbolsQuery.data?.symbols ?? []).map((sym) => (
                      <option key={sym.id} value={sym.id}>
                        {sym.qualified_name}
                      </option>
                    ))}
                  </select>
                </label>
              </>
            )}
          </div>
        </div>

        {openError && (
          <p className="mt-2 text-xs text-amber-300" role="status">
            {openError}
          </p>
        )}
        {selectedRepo && (
          <p className="mt-3 text-xs text-[var(--muted)]">
            {selectedRepo.owner_name}/{selectedRepo.name}
            {graphQuery.data?.snapshot_id
              ? ` · snapshot ${graphQuery.data.snapshot_id.slice(0, 8)}…`
              : ""}
            {graphQuery.data
              ? ` · ${graphQuery.data.node_count} nodes · ${graphQuery.data.edge_count} edges`
              : ""}
            {" · click a file/module node to open"}
          </p>
        )}
      </section>

      <section className="overflow-hidden rounded-xl border border-[var(--border)] bg-[var(--panel)]">
        {graphQuery.isLoading && (
          <p className="p-6 text-sm text-[var(--muted)]">Loading graph…</p>
        )}
        {graphQuery.isError && (
          <p className="p-6 text-sm text-red-400">
            {graphQuery.error instanceof Error
              ? graphQuery.error.message
              : "Failed to load graph"}
          </p>
        )}
        {graphQuery.data && (
          <div className="h-[560px] w-full" data-testid="graph-canvas">
            {graphQuery.data.node_count === 0 ? (
              <p className="p-6 text-sm text-[var(--muted)]">
                No graph nodes for the current filters.
                {graphType === "calls"
                  ? " Pick a center symbol after indexing a deep-language repository."
                  : " Try clearing filters or indexing a repository."}
              </p>
            ) : (
              <ReactFlowProvider>
                <ReactFlow
                  nodes={flow.nodes}
                  edges={flow.edges}
                  fitView
                  minZoom={0.2}
                  proOptions={{ hideAttribution: true }}
                  onNodeClick={onNodeClick}
                  onNodeDragStart={() => {
                    draggingRef.current = true;
                  }}
                  onNodeDragStop={() => {
                    // Allow click handler to see drag flag once, then clear.
                    window.setTimeout(() => {
                      draggingRef.current = false;
                    }, 0);
                  }}
                >
                  <Background color="#2a3648" gap={18} />
                  <Controls />
                  <MiniMap
                    nodeColor={(n) =>
                      nodeColor(
                        String((n.data as { supportLevel?: string }).supportLevel ?? "skip"),
                      )
                    }
                    maskColor="rgba(15,20,25,0.7)"
                  />
                </ReactFlow>
              </ReactFlowProvider>
            )}
          </div>
        )}
      </section>

      <p className="text-xs text-[var(--muted)]">
        Honesty: generic directory graphs never invent verified-deep call edges. Call graphs are
        deep-language only and retain resolution confidence on each edge.
      </p>
    </div>
  );
}
