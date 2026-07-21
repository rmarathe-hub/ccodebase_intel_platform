import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { ImportRepositoryPanel } from "../components/ImportRepositoryPanel";
import { PageShell } from "../components/PageShell";
import { fetchRepositories } from "../lib/api";

const apiBase = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function fetchHealth(): Promise<{ status: string }> {
  const response = await fetch(`${apiBase}/health`);
  if (!response.ok) {
    throw new Error(`Health check failed (${response.status})`);
  }
  return response.json() as Promise<{ status: string }>;
}

export function DashboardPage() {
  const health = useQuery({
    queryKey: ["health"],
    queryFn: fetchHealth,
    retry: false,
  });

  const reposQuery = useQuery({
    queryKey: ["repositories"],
    queryFn: () => fetchRepositories(12),
  });

  return (
    <div className="space-y-4">
      <PageShell
        title="Dashboard"
        description="Paste a public GitHub URL, watch indexing stages through Ready, then explore Search, Ask, Graph, Symbols, and Files."
      />

      <div className="rounded-xl border border-[var(--border)] bg-[var(--panel)] p-4 text-sm">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <p className="text-[var(--muted)]">API health · {apiBase}</p>
          {health.isLoading && <p>Checking…</p>}
          {health.isError && (
            <p className="text-amber-300">
              Unreachable — start the API (and worker) before importing.
            </p>
          )}
          {health.data && (
            <p className="text-emerald-300">Status: {health.data.status}</p>
          )}
        </div>
      </div>

      <ImportRepositoryPanel showWorkspaceLinksOnReady />

      <section className="rounded-xl border border-[var(--border)] bg-[var(--panel)] p-6">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h3 className="text-lg font-semibold">Previously indexed</h3>
          <Link className="text-sm text-[var(--accent)] underline" to="/repositories">
            View all
          </Link>
        </div>
        {reposQuery.isLoading && (
          <p className="mt-3 text-sm text-[var(--muted)]">Loading…</p>
        )}
        {reposQuery.data && reposQuery.data.length === 0 && (
          <p className="mt-3 text-sm text-[var(--muted)]">
            No repositories yet — start an import above.
          </p>
        )}
        {reposQuery.data && reposQuery.data.length > 0 && (
          <ul className="mt-3 divide-y divide-[var(--border)]">
            {reposQuery.data.map((repo) => (
              <li key={repo.id}>
                <Link
                  to={`/repositories/${repo.id}`}
                  className="flex items-center justify-between gap-3 py-2.5 text-sm hover:text-[var(--accent)]"
                >
                  <span>
                    {repo.owner_name}/{repo.name}
                    <span className="ml-2 text-xs text-[var(--muted)]">
                      {repo.default_branch || "default"}
                    </span>
                  </span>
                  <span className="text-xs text-[var(--muted)]">Open</span>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="rounded-xl border border-[var(--border)] bg-[var(--panel)] p-6 text-sm text-[var(--muted)]">
        <p className="font-medium text-[var(--text)]">What happens next</p>
        <ol className="mt-2 list-decimal space-y-1 pl-5">
          <li>Worker clones the repo (depth-1, no submodules / no code execution).</li>
          <li>
            Stages: Cloning → Discovering → Parsing → Relationships → Chunking → Embedding →
            Validating → Ready.
          </li>
          <li>
            Deep languages (Python / Java / JS-TS) get symbols and calls; other languages stay
            generic with honest citations.
          </li>
          <li>
            When Ready, open{" "}
            <Link className="text-[var(--accent)] underline" to="/search">
              Search
            </Link>{" "}
            or{" "}
            <Link className="text-[var(--accent)] underline" to="/ask">
              Ask
            </Link>
            .
          </li>
        </ol>
        <p className="mt-3 text-xs">
          Job history, cancel, and retries live on the{" "}
          <Link className="text-[var(--accent)] underline" to="/jobs">
            Jobs
          </Link>{" "}
          page.
        </p>
      </section>
    </div>
  );
}
