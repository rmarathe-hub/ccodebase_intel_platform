import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { PageShell } from "../components/PageShell";
import { fetchRepositories, fetchRepositoryFiles } from "../lib/api";
import { supportLevelLabel, type SupportLevel } from "../lib/files";

const LEVEL_FILTERS: Array<{ id: "all" | SupportLevel; label: string }> = [
  { id: "all", label: "All" },
  { id: "deep", label: "Deep" },
  { id: "generic", label: "Generic" },
  { id: "skip", label: "Skip" },
];

export function FilesPage() {
  const [repositoryId, setRepositoryId] = useState<string>("");
  const [level, setLevel] = useState<"all" | SupportLevel>("all");
  const [includeSkipped, setIncludeSkipped] = useState(true);
  const [pathPrefix, setPathPrefix] = useState("");

  const reposQuery = useQuery({
    queryKey: ["repositories"],
    queryFn: () => fetchRepositories(50),
  });

  const selectedId = repositoryId || reposQuery.data?.[0]?.id || "";

  const filesQuery = useQuery({
    queryKey: ["repository-files", selectedId, level, includeSkipped, pathPrefix],
    queryFn: () =>
      fetchRepositoryFiles(selectedId, {
        support_level: level === "all" ? undefined : level,
        include_skipped: includeSkipped,
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
        title="Files"
        description="Browse discovered files with honesty labels (deep / generic / skip). Python deep files may show parser_name=python-ast after the worker parsing stage."
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
            <span className="text-[var(--muted)]">Path prefix</span>
            <input
              className="rounded-md border border-[var(--border)] bg-[color-mix(in_srgb,var(--bg)_70%,black)] px-3 py-2 outline-none ring-[var(--accent)] focus:ring-2"
              value={pathPrefix}
              onChange={(event) => setPathPrefix(event.target.value)}
              placeholder="src/"
              aria-label="Path prefix"
            />
          </label>

          <label className="flex items-center gap-2 text-sm text-[var(--muted)]">
            <input
              type="checkbox"
              checked={includeSkipped}
              onChange={(event) => setIncludeSkipped(event.target.checked)}
            />
            Include skipped
          </label>
        </div>

        <div className="mt-4 flex flex-wrap gap-2">
          {LEVEL_FILTERS.map((item) => (
            <button
              key={item.id}
              type="button"
              className={[
                "rounded-md border px-3 py-1.5 text-sm",
                level === item.id
                  ? "border-[var(--accent)] bg-[color-mix(in_srgb,var(--accent)_20%,transparent)]"
                  : "border-[var(--border)]",
              ].join(" ")}
              onClick={() => setLevel(item.id)}
            >
              {item.label}
            </button>
          ))}
        </div>

        {selectedRepo && (
          <p className="mt-3 text-xs text-[var(--muted)]">
            Showing latest ready snapshot for {selectedRepo.owner_name}/{selectedRepo.name}
            {filesQuery.data?.snapshot_id
              ? ` · snapshot ${filesQuery.data.snapshot_id.slice(0, 8)}…`
              : " · no snapshot yet (import a repo and wait for the worker)"}
          </p>
        )}
      </section>

      <section className="overflow-hidden rounded-xl border border-[var(--border)] bg-[var(--panel)]">
        {reposQuery.isLoading || filesQuery.isLoading ? (
          <p className="p-6 text-sm text-[var(--muted)]">Loading files…</p>
        ) : reposQuery.isError ? (
          <p className="p-6 text-sm text-rose-300">{(reposQuery.error as Error).message}</p>
        ) : filesQuery.isError ? (
          <p className="p-6 text-sm text-rose-300">{(filesQuery.error as Error).message}</p>
        ) : !selectedId ? (
          <p className="p-6 text-sm text-[var(--muted)]">
            Import a repository from Jobs to populate this list.
          </p>
        ) : (filesQuery.data?.files.length ?? 0) === 0 ? (
          <p className="p-6 text-sm text-[var(--muted)]">
            No files matched. Run an import job or widen filters.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead className="border-b border-[var(--border)] text-xs uppercase tracking-wide text-[var(--muted)]">
                <tr>
                  <th className="px-4 py-3 font-medium">Path</th>
                  <th className="px-4 py-3 font-medium">Language</th>
                  <th className="px-4 py-3 font-medium">Level</th>
                  <th className="px-4 py-3 font-medium">Size</th>
                  <th className="px-4 py-3 font-medium">Skip reason</th>
                </tr>
              </thead>
              <tbody>
                {filesQuery.data?.files.map((file) => (
                  <tr key={file.id} className="border-b border-[var(--border)]/70">
                    <td className="max-w-[28rem] truncate px-4 py-2 font-mono text-xs">
                      {file.path}
                    </td>
                    <td className="px-4 py-2 text-[var(--muted)]">{file.language ?? "—"}</td>
                    <td className="px-4 py-2">
                      <span
                        className={[
                          "rounded px-2 py-0.5 text-xs",
                          file.support_level === "deep"
                            ? "bg-emerald-500/15 text-emerald-200"
                            : file.support_level === "generic"
                              ? "bg-sky-500/15 text-sky-200"
                              : "bg-zinc-500/20 text-zinc-300",
                        ].join(" ")}
                      >
                        {supportLevelLabel(file.support_level)}
                      </span>
                    </td>
                    <td className="px-4 py-2 text-[var(--muted)]">{file.size_bytes}</td>
                    <td className="px-4 py-2 text-[var(--muted)]">{file.skip_reason ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <p className="border-t border-[var(--border)] px-4 py-3 text-xs text-[var(--muted)]">
              Showing {filesQuery.data?.files.length ?? 0} of {filesQuery.data?.total ?? 0} files
            </p>
          </div>
        )}
      </section>
    </div>
  );
}
