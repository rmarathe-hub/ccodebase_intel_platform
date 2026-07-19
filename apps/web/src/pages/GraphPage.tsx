import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { PageShell } from "../components/PageShell";
import { fetchRepositories, fetchRepositoryCalls } from "../lib/api";
import { confidenceLabel } from "../lib/calls";

export function GraphPage() {
  const [repositoryId, setRepositoryId] = useState("");
  const [confidence, setConfidence] = useState<"all" | "resolved" | "ambiguous" | "unresolved">(
    "all",
  );

  const reposQuery = useQuery({
    queryKey: ["repositories"],
    queryFn: () => fetchRepositories(50),
  });
  const selectedId = repositoryId || reposQuery.data?.[0]?.id || "";

  const callsQuery = useQuery({
    queryKey: ["repository-calls", selectedId, confidence],
    queryFn: () =>
      fetchRepositoryCalls(selectedId, {
        confidence: confidence === "all" ? undefined : confidence,
        limit: 200,
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
        title="Graph"
        description="Call-site list for the latest snapshot. Full interactive graphs come later; this view verifies extracted callers/callees with resolution confidence."
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
          <div className="flex flex-wrap gap-2">
            {(["all", "resolved", "ambiguous", "unresolved"] as const).map((item) => (
              <button
                key={item}
                type="button"
                className={[
                  "rounded-md border px-3 py-1.5 text-sm capitalize",
                  confidence === item
                    ? "border-[var(--accent)] bg-[color-mix(in_srgb,var(--accent)_20%,transparent)]"
                    : "border-[var(--border)]",
                ].join(" ")}
                onClick={() => setConfidence(item)}
              >
                {item}
              </button>
            ))}
          </div>
        </div>
        {selectedRepo && (
          <p className="mt-3 text-xs text-[var(--muted)]">
            {selectedRepo.owner_name}/{selectedRepo.name}
            {callsQuery.data?.snapshot_id
              ? ` · snapshot ${callsQuery.data.snapshot_id.slice(0, 8)}…`
              : ""}
          </p>
        )}
      </section>

      <section className="rounded-xl border border-[var(--border)] bg-[var(--panel)] p-6">
        {callsQuery.isLoading && <p className="text-sm text-[var(--muted)]">Loading calls…</p>}
        {callsQuery.isError && (
          <p className="text-sm text-red-400">
            {callsQuery.error instanceof Error
              ? callsQuery.error.message
              : "Failed to load calls"}
          </p>
        )}
        {callsQuery.data && (
          <>
            <p className="mb-3 text-sm text-[var(--muted)]">
              {callsQuery.data.total} call site{callsQuery.data.total === 1 ? "" : "s"}
            </p>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[640px] text-left text-sm">
                <thead className="text-[var(--muted)]">
                  <tr className="border-b border-[var(--border)]">
                    <th className="py-2 pr-3 font-medium">Caller</th>
                    <th className="py-2 pr-3 font-medium">Expression</th>
                    <th className="py-2 pr-3 font-medium">Candidate</th>
                    <th className="py-2 pr-3 font-medium">Confidence</th>
                    <th className="py-2 font-medium">Location</th>
                  </tr>
                </thead>
                <tbody>
                  {callsQuery.data.calls.map((call) => (
                    <tr key={call.id} className="border-b border-[var(--border)]/60">
                      <td className="py-2 pr-3 font-mono text-xs">
                        {call.caller_qualified_name ?? "—"}
                      </td>
                      <td className="py-2 pr-3 font-mono text-xs">{call.qualified_expression}</td>
                      <td className="py-2 pr-3 font-mono text-xs">
                        {call.candidate_qualified_name ?? "—"}
                      </td>
                      <td className="py-2 pr-3 text-xs">{confidenceLabel(call.confidence)}</td>
                      <td className="py-2 font-mono text-xs text-[var(--muted)]">
                        {call.path}:{call.line}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {callsQuery.data.calls.length === 0 && (
              <p className="mt-3 text-sm text-[var(--muted)]">
                No call sites yet. Re-index a Python repository after call extraction is enabled.
              </p>
            )}
          </>
        )}
      </section>
    </div>
  );
}
