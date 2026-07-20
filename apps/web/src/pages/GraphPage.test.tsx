// Graph page: interactive React Flow canvas with graph-type filters.
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { afterEach, beforeAll, describe, expect, it, vi } from "vitest";
import { GraphPage } from "./GraphPage";

beforeAll(() => {
  class ResizeObserverStub {
    observe() {}
    unobserve() {}
    disconnect() {}
  }
  vi.stubGlobal("ResizeObserver", ResizeObserverStub);
});

vi.mock("@xyflow/react", () => ({
  ReactFlow: ({ children }: { children?: ReactNode }) => (
    <div data-testid="react-flow-mock">{children}</div>
  ),
  ReactFlowProvider: ({ children }: { children?: ReactNode }) => <>{children}</>,
  Background: () => null,
  Controls: () => null,
  MiniMap: () => null,
  MarkerType: { ArrowClosed: "arrowclosed" },
}));

vi.mock("../lib/api", () => ({
  fetchRepositories: vi.fn(async () => [
    {
      id: "repo-1",
      host: "github.com",
      owner_name: "rmarathe-hub",
      name: "retail-retention-revenue-intel",
      default_branch: "main",
      clone_url: "https://github.com/rmarathe-hub/retail-retention-revenue-intel.git",
      created_at: "2026-01-01T00:00:00Z",
      updated_at: "2026-01-01T00:00:00Z",
    },
  ]),
  fetchRepositoryModuleGraph: vi.fn(async () => ({
    repository_id: "repo-1",
    snapshot_id: "snap-1",
    graph_type: "modules",
    node_count: 2,
    edge_count: 1,
    center_symbol_id: null,
    depth: null,
    filters: { local_imports_only: true },
    nodes: [
      {
        id: "pkg.a",
        label: "pkg.a",
        node_type: "module",
        language: "python",
        support_level: "deep",
        path: "pkg/a.py",
        symbol_count: 2,
        file_count: 0,
        symbol_id: null,
        kind: null,
      },
      {
        id: "pkg.b",
        label: "pkg.b",
        node_type: "module",
        language: "python",
        support_level: "deep",
        path: "pkg/b.py",
        symbol_count: 1,
        file_count: 0,
        symbol_id: null,
        kind: null,
      },
    ],
    edges: [
      {
        source: "pkg.a",
        target: "pkg.b",
        relation_kind: "imports",
        confidence: "resolved",
        language: "python",
        weight: 1,
        inferred: false,
        line: null,
      },
    ],
  })),
  fetchRepositoryPackageGraph: vi.fn(async () => ({
    repository_id: "repo-1",
    snapshot_id: "snap-1",
    graph_type: "packages",
    node_count: 0,
    edge_count: 0,
    center_symbol_id: null,
    depth: null,
    filters: {},
    nodes: [],
    edges: [],
  })),
  fetchRepositoryDirectoryGraph: vi.fn(async () => ({
    repository_id: "repo-1",
    snapshot_id: "snap-1",
    graph_type: "directories",
    node_count: 0,
    edge_count: 0,
    center_symbol_id: null,
    depth: null,
    filters: {},
    nodes: [],
    edges: [],
  })),
  fetchRepositoryCallGraph: vi.fn(async () => ({
    repository_id: "repo-1",
    snapshot_id: "snap-1",
    graph_type: "calls",
    node_count: 0,
    edge_count: 0,
    center_symbol_id: null,
    depth: 1,
    filters: {},
    nodes: [],
    edges: [],
  })),
  fetchRepositorySymbols: vi.fn(async () => ({
    repository_id: "repo-1",
    snapshot_id: "snap-1",
    total: 0,
    limit: 100,
    offset: 0,
    symbols: [],
  })),
}));

function wrap(ui: ReactNode) {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(<QueryClientProvider client={client}>{ui}</QueryClientProvider>);
}

afterEach(() => {
  vi.clearAllMocks();
});

describe("GraphPage", () => {
  it("renders interactive graph canvas with type filters", async () => {
    wrap(<GraphPage />);
    expect(screen.getByRole("heading", { name: "Graph" })).toBeInTheDocument();
    expect(screen.getByText(/interactive structural graphs/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Modules" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Packages" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Directories" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Calls" })).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByTestId("graph-canvas")).toBeInTheDocument();
    });
    expect(screen.getByTestId("react-flow-mock")).toBeInTheDocument();
    expect(screen.getByLabelText("Language")).toBeInTheDocument();
    expect(screen.getByLabelText("Support level")).toBeInTheDocument();
  });
});
