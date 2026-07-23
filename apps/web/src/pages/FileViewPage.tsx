import { useQuery } from "@tanstack/react-query";
import { useMemo } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { PageShell } from "../components/PageShell";
import { fetchRepositories, fetchRepositoryFileContent } from "../lib/api";

export function FileViewPage() {
  const [params] = useSearchParams();
  const repoId = params.get("repo") || "";
  const path = params.get("path") || "";
  const lineParam = params.get("line");
  const symbolId = params.get("symbol");
  const focusLine = lineParam ? Number(lineParam) : null;

  const reposQuery = useQuery({
    queryKey: ["repositories"],
    queryFn: () => fetchRepositories(50),
  });

  const contentQuery = useQuery({
    queryKey: ["file-content", repoId, path],
    queryFn: () => fetchRepositoryFileContent(repoId, path),
    enabled: Boolean(repoId && path),
  });

  const selectedRepo = useMemo(
    () => reposQuery.data?.find((repo) => repo.id === repoId),
    [reposQuery.data, repoId],
  );

  const lines = useMemo(() => {
    const text = contentQuery.data?.content ?? "";
    return text.length ? text.split("\n") : [];
  }, [contentQuery.data?.content]);

  return (
    <div className="space-y-4">
      <PageShell
        title="File viewer"
        description="Indexed chunk content for a repository-relative path. Opened from Graph node clicks."
      />

      <section className="rounded-xl border border-[var(--border)] bg-[var(--panel)] p-4 text-sm">
        <div className="flex flex-wrap items-center gap-3">
          <Link
            to={`/graph?repo=${encodeURIComponent(repoId)}`}
            className="text-[var(--accent)] underline-offset-2 hover:underline"
          >
            ← Back to Graph
          </Link>
          {selectedRepo && (
            <span className="text-[var(--muted)]">
              {selectedRepo.owner_name}/{selectedRepo.name}
            </span>
          )}
          {path && <span className="font-mono text-[var(--text)]">{path}</span>}
          {symbolId && (
            <span className="text-xs text-[var(--muted)]">symbol {symbolId.slice(0, 8)}…</span>
          )}
        </div>
      </section>

      {!repoId || !path ? (
        <p className="text-sm text-[var(--muted)]">
          Missing repo or path. Open a file from the Graph page.
        </p>
      ) : contentQuery.isLoading ? (
        <p className="text-sm text-[var(--muted)]">Loading file…</p>
      ) : contentQuery.isError ? (
        <p className="text-sm text-red-400">
          {contentQuery.error instanceof Error
            ? contentQuery.error.message
            : "Failed to load file"}
        </p>
      ) : contentQuery.data && !contentQuery.data.indexed ? (
        <p className="text-sm text-[var(--muted)]">
          {contentQuery.data.message || "File not indexed in the latest ready snapshot."}
        </p>
      ) : (
        <section className="overflow-hidden rounded-xl border border-[var(--border)] bg-[var(--panel)]">
          <div className="border-b border-[var(--border)] px-4 py-2 text-xs text-[var(--muted)]">
            {contentQuery.data?.language ?? "unknown"} ·{" "}
            {contentQuery.data?.support_level ?? "n/a"}
            {contentQuery.data?.coverage_complete === false
              ? " · coverage partial"
              : " · coverage complete"}
            {contentQuery.data?.chunks?.length
              ? ` · ${contentQuery.data.chunks.length} chunks`
              : ""}
          </div>
          <pre className="max-h-[70vh] overflow-auto p-0 text-[12px] leading-5">
            <code>
              {lines.map((line, index) => {
                const lineNo = index + 1;
                const focused =
                  focusLine != null && !Number.isNaN(focusLine) && lineNo === focusLine;
                return (
                  <div
                    key={lineNo}
                    id={`L${lineNo}`}
                    className={[
                      "flex gap-3 px-4",
                      focused
                        ? "bg-[color-mix(in_srgb,var(--accent)_22%,transparent)]"
                        : "hover:bg-[color-mix(in_srgb,var(--bg)_50%,transparent)]",
                    ].join(" ")}
                  >
                    <span className="w-10 shrink-0 select-none text-right text-[var(--muted)]">
                      {lineNo}
                    </span>
                    <span className="whitespace-pre-wrap break-all text-[var(--text)]">
                      {line || " "}
                    </span>
                  </div>
                );
              })}
            </code>
          </pre>
        </section>
      )}
    </div>
  );
}
