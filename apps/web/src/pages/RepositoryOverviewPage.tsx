import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { JobProgress } from "../components/JobProgress";
import { PageShell } from "../components/PageShell";
import {
  CleanupAllRepositoriesButton,
  CleanupTestRepositoriesButton,
  RepositoryCardActions,
} from "../components/RepositoryCardActions";
import {
  cancelJob,
  fetchRepositories,
  fetchRepositoryJobs,
  fetchRepositorySummary,
} from "../lib/api";
import { supportLevelLabel } from "../lib/files";
import { isTerminalStatus } from "../lib/jobs";

function workspaceLink(path: string, repositoryId: string): string {
  return `${path}?repo=${encodeURIComponent(repositoryId)}`;
}

export function RepositoryOverviewPage() {
  const { id } = useParams<{ id?: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const reposQuery = useQuery({
    queryKey: ["repositories"],
    queryFn: () => fetchRepositories(200),
  });

  const selectedId = id || reposQuery.data?.[0]?.id || "";

  const selectedRepo = useMemo(
    () => reposQuery.data?.find((repo) => repo.id === selectedId),
    [reposQuery.data, selectedId],
  );

  const summaryQuery = useQuery({
    queryKey: ["repository-summary", selectedId],
    queryFn: () => fetchRepositorySummary(selectedId),
    enabled: Boolean(selectedId),
  });

  const jobsQuery = useQuery({
    queryKey: ["repository-jobs", selectedId],
    queryFn: () => fetchRepositoryJobs(selectedId),
    enabled: Boolean(selectedId),
    refetchInterval: (query) => {
      const jobs = query.state.data ?? [];
      return jobs.some((job) => !isTerminalStatus(job.status)) ? 2000 : false;
    },
  });

  const latestJob = jobsQuery.data?.[0];

  const cancelMutation = useMutation({
    mutationFn: (jobId: string) => cancelJob(jobId),
    onSuccess: (job) => {
      void queryClient.invalidateQueries({ queryKey: ["job", job.id] });
      void queryClient.invalidateQueries({ queryKey: ["repository-jobs", selectedId] });
      void queryClient.invalidateQueries({ queryKey: ["jobs"] });
    },
  });

  const det = summaryQuery.data?.deterministic_summary;
  const supportMix = det?.support_level_mix ?? {};
  const languageMix = det?.language_mix ?? {};
  const hasPartialSupport =
    (supportMix.generic ?? 0) > 0 || (supportMix.skip ?? 0) > 0;

  return (
    <div className="space-y-4">
      <PageShell
        title="Repository overview"
        description="Switch between previously indexed repositories, force re-index after pipeline fixes, or delete unused imports."
      />

      <section className="rounded-xl border border-[var(--border)] bg-[var(--panel)] p-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h3 className="text-lg font-semibold">Indexed repositories</h3>
          <div className="flex flex-wrap items-center gap-3">
            <CleanupTestRepositoriesButton />
            <CleanupAllRepositoriesButton />
            <Link className="text-sm text-[var(--accent)] underline" to="/">
              Import another
            </Link>
          </div>
        </div>

        {reposQuery.isLoading && (
          <p className="mt-3 text-sm text-[var(--muted)]">Loading repositories…</p>
        )}
        {reposQuery.isError && (
          <p className="mt-3 text-sm text-amber-300">Could not load repositories.</p>
        )}
        {reposQuery.data && reposQuery.data.length === 0 && (
          <p className="mt-3 text-sm text-[var(--muted)]">
            No repositories yet.{" "}
            <Link className="text-[var(--accent)] underline" to="/">
              Paste a GitHub URL on the Dashboard
            </Link>
            .
          </p>
        )}
        {reposQuery.data && reposQuery.data.length > 0 && (
          <ul className="mt-4 divide-y divide-[var(--border)]">
            {reposQuery.data.map((repo) => {
              const active = repo.id === selectedId;
              return (
                <li
                  key={repo.id}
                  className={[
                    "flex flex-wrap items-center justify-between gap-3 py-3 px-1",
                    active
                      ? "bg-[color-mix(in_srgb,var(--accent)_10%,transparent)]"
                      : "",
                  ].join(" ")}
                >
                  <button
                    type="button"
                    className="min-w-0 flex-1 text-left hover:text-[var(--accent)]"
                    onClick={() => navigate(`/repositories/${repo.id}`)}
                  >
                    <p className="font-medium">
                      {repo.owner_name}/{repo.name}
                    </p>
                    <p className="mt-1 text-xs text-[var(--muted)]">
                      {repo.default_branch || "default"} · {repo.host}
                      {active ? " · Selected" : ""}
                    </p>
                  </button>
                  <RepositoryCardActions repo={repo} compact />
                </li>
              );
            })}
          </ul>
        )}
      </section>

      {selectedRepo && (
        <section className="rounded-xl border border-[var(--border)] bg-[var(--panel)] p-6 space-y-4">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <h3 className="text-lg font-semibold">
                {selectedRepo.owner_name}/{selectedRepo.name}
              </h3>
              <p className="mt-1 text-sm text-[var(--muted)]">
                Branch {selectedRepo.default_branch || "(remote default)"} ·{" "}
                <a
                  className="text-[var(--accent)] underline"
                  href={selectedRepo.clone_url.replace(/\.git$/, "")}
                  target="_blank"
                  rel="noreferrer"
                >
                  GitHub
                </a>
              </p>
            </div>
            <RepositoryCardActions repo={selectedRepo} />
          </div>

          <p className="text-xs text-[var(--muted)]">
            Re-index may skip work when the commit is unchanged. Force Re-index always rebuilds
            chunks and embeddings.
          </p>

          {summaryQuery.isLoading && (
            <p className="text-sm text-[var(--muted)]">Loading summary…</p>
          )}
          {summaryQuery.data && !det && (
            <p className="text-sm text-amber-200">
              No ready snapshot yet. Wait for indexing to finish, or start a re-index.
            </p>
          )}

          {det && (
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="rounded-lg border border-[var(--border)] p-4">
                <p className="text-xs tracking-[0.18em] text-[var(--muted)] uppercase">
                  Support mix
                </p>
                <ul className="mt-2 space-y-1 text-sm">
                  {Object.entries(supportMix).map(([level, count]) => (
                    <li key={level} className="flex justify-between gap-2">
                      <span>{supportLevelLabel(level)}</span>
                      <span className="font-mono text-[var(--muted)]">{count}</span>
                    </li>
                  ))}
                </ul>
                {hasPartialSupport && (
                  <p className="mt-3 text-xs text-amber-200">
                    Partial support: generic and skipped files stay honest — Search/Ask cite
                    them without inventing deep call graphs.
                  </p>
                )}
              </div>
              <div className="rounded-lg border border-[var(--border)] p-4">
                <p className="text-xs tracking-[0.18em] text-[var(--muted)] uppercase">
                  Languages ({det.file_count} files)
                </p>
                <ul className="mt-2 max-h-40 space-y-1 overflow-auto text-sm">
                  {Object.entries(languageMix)
                    .sort((a, b) => b[1] - a[1])
                    .map(([lang, count]) => (
                      <li key={lang} className="flex justify-between gap-2">
                        <span>{lang}</span>
                        <span className="font-mono text-[var(--muted)]">{count}</span>
                      </li>
                    ))}
                </ul>
              </div>
            </div>
          )}

          <div className="flex flex-wrap gap-2">
            {(
              [
                ["/search", "Search"],
                ["/ask", "Ask"],
                ["/graph", "Graph"],
                ["/symbols", "Symbols"],
                ["/files", "Files"],
              ] as const
            ).map(([path, label]) => (
              <Link
                key={path}
                to={workspaceLink(path, selectedRepo.id)}
                className="rounded-md border border-[var(--border)] px-3 py-1.5 text-sm hover:border-[var(--accent)]"
              >
                {label}
              </Link>
            ))}
          </div>

          {latestJob && (
            <div className="border-t border-[var(--border)] pt-4">
              <JobProgress
                job={latestJob}
                repositoryLabel={`${selectedRepo.owner_name}/${selectedRepo.name}`}
                showWorkspaceLinks
                onCancel={(jobId) => cancelMutation.mutate(jobId)}
                cancelPending={cancelMutation.isPending}
              />
            </div>
          )}
        </section>
      )}
    </div>
  );
}
