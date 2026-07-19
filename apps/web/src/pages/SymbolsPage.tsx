import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { PageShell } from "../components/PageShell";
import { fetchRepositories, fetchRepositorySymbols } from "../lib/api";
import { symbolKindLabel, type SymbolKind } from "../lib/symbols";

const KIND_FILTERS: Array<{ id: "all" | SymbolKind; label: string }> = [
  { id: "all", label: "All" },
  { id: "class", label: "Classes" },
  { id: "function", label: "Functions" },
  { id: "method", label: "Methods" },
  { id: "import", label: "Imports" },
];

export function SymbolsPage() {
  const [repositoryId, setRepositoryId] = useState<string>("");
  const [kind, setKind] = useState<"all" | SymbolKind>("all");
  const [nameContains, setNameContains] = useState("");
  const [pathPrefix, setPathPrefix] = useState("");

  const reposQuery = useQuery({
    queryKey: ["repositories"],
    queryFn: () => fetchRepositories(50),
  });

  const selectedId = repositoryId || reposQuery.data?.[0]?.id || "";

  const symbolsQuery = useQuery({
    queryKey: ["repository-symbols", selectedId, kind, nameContains, pathPrefix],
    queryFn: () =>
      fetchRepositorySymbols(selectedId, {
        kind: kind === "all" ? undefined : kind,
        name_contains: nameContains.trim() || undefined,
        path_prefix: pathPrefix.trim() || undefined,
        limit: 200,
        offset: 0,
      }),
    enabled: Boolean(selectedId),
  });

  const selectedRepo = useMemo(
    () => reposQuery.data?.find((repo) => repo.id === selectedId),
    [reposQuery.data, selectedId],
  );

  return (
    <div className="space-y-4">
      <PageShell
        title="Symbols"
        description="Browse verified Python symbols with qualified names, signatures, decorators, and docstrings from python-ast. Framework detection, import/call graphs, and Java/TS parsers are not shipped yet."
      />

      <section className="rounded-xl border border-[var(--border)] bg-[var(--panel)] p-6">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-end">
          <label className="flex min-w-0 flex-1 flex-col gap-1 text-sm">
            <span className="text-[var(--muted)]">Repository</span>
            <select
              className="rounded-md border border-[var(--border)] bg-[color-mix(in_srgb,var(--bg)_70%,black)] px-3 py-2 outline-none ring-[var(--accent)] focus:ring-2"
              value={selectedId}
              onChange={(event) => setRepositoryId(event.target.value)}
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

          <label className="flex min-w-0 flex-1 flex-col gap-1 text-sm">
            <span className="text-[var(--muted)]">Name contains</span>
            <input
              className="rounded-md border border-[var(--border)] bg-[color-mix(in_srgb,var(--bg)_70%,black)] px-3 py-2 outline-none ring-[var(--accent)] focus:ring-2"
              value={nameContains}
              onChange={(event) => setNameContains(event.target.value)}
              placeholder="load_"
              aria-label="Name contains"
            />
          </label>

          <label className="flex min-w-0 flex-1 flex-col gap-1 text-sm">
            <span className="text-[var(--muted)]">Path prefix</span>
            <input
              className="rounded-md border border-[var(--border)] bg-[color-mix(in_srgb,var(--bg)_70%,black)] px-3 py-2 outline-none ring-[var(--accent)] focus:ring-2"
              value={pathPrefix}
              onChange={(event) => setPathPrefix(event.target.value)}
              placeholder="scripts/"
              aria-label="Path prefix"
            />
          </label>
        </div>

        <div className="mt-4 flex flex-wrap gap-2">
          {KIND_FILTERS.map((item) => (
            <button
              key={item.id}
              type="button"
              className={[
                "rounded-md border px-3 py-1.5 text-sm",
                kind === item.id
                  ? "border-[var(--accent)] bg-[color-mix(in_srgb,var(--accent)_20%,transparent)]"
                  : "border-[var(--border)]",
              ].join(" ")}
              onClick={() => setKind(item.id)}
            >
              {item.label}
            </button>
          ))}
        </div>

        {selectedRepo && (
          <p className="mt-3 text-xs text-[var(--muted)]">
            Verified deep symbols only · {selectedRepo.owner_name}/{selectedRepo.name}
            {symbolsQuery.data?.snapshot_id
              ? ` · snapshot ${symbolsQuery.data.snapshot_id.slice(0, 8)}…`
              : " · no snapshot yet"}
          </p>
        )}
      </section>

      <section className="rounded-xl border border-[var(--border)] bg-[var(--panel)] p-6">
        {symbolsQuery.isLoading && <p className="text-sm text-[var(--muted)]">Loading symbols…</p>}
        {symbolsQuery.isError && (
          <p className="text-sm text-red-400">
            {symbolsQuery.error instanceof Error
              ? symbolsQuery.error.message
              : "Failed to load symbols"}
          </p>
        )}
        {symbolsQuery.data && (
          <>
            <p className="mb-3 text-sm text-[var(--muted)]">
              {symbolsQuery.data.total} symbol{symbolsQuery.data.total === 1 ? "" : "s"}
            </p>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[640px] text-left text-sm">
                <thead className="text-[var(--muted)]">
                  <tr className="border-b border-[var(--border)]">
                    <th className="py-2 pr-3 font-medium">Kind</th>
                    <th className="py-2 pr-3 font-medium">Qualified name</th>
                    <th className="py-2 pr-3 font-medium">Path</th>
                    <th className="py-2 pr-3 font-medium">Lines</th>
                    <th className="py-2 font-medium">Details</th>
                  </tr>
                </thead>
                <tbody>
                  {symbolsQuery.data.symbols.map((sym) => (
                    <tr key={sym.id} className="border-b border-[var(--border)]/60 align-top">
                      <td className="py-2 pr-3">
                        {symbolKindLabel(sym.kind)}
                        {sym.is_async ? (
                          <span className="ml-1 text-xs text-[var(--muted)]">async</span>
                        ) : null}
                      </td>
                      <td className="py-2 pr-3 font-mono text-xs">{sym.qualified_name}</td>
                      <td className="py-2 pr-3 font-mono text-xs">{sym.path}</td>
                      <td className="py-2 pr-3 tabular-nums">
                        {sym.start_line}–{sym.end_line}
                      </td>
                      <td className="py-2 text-xs text-[var(--muted)]">
                        <div className="font-mono">{sym.signature ?? "—"}</div>
                        {sym.decorators.length > 0 && (
                          <div className="mt-1">@{sym.decorators.join(" @")}</div>
                        )}
                        {sym.docstring && (
                          <div className="mt-1 line-clamp-2 italic">{sym.docstring}</div>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {symbolsQuery.data.symbols.length === 0 && (
              <p className="mt-3 text-sm text-[var(--muted)]">
                No symbols yet. Import a Python repo and wait for the worker to finish parsing.
              </p>
            )}
          </>
        )}
      </section>
    </div>
  );
}
