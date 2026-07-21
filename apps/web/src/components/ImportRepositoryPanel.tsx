import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import type { FormEvent } from "react";
import { JobProgress } from "./JobProgress";
import { fetchJob, importRepository } from "../lib/api";
import { isTerminalStatus, type IndexingJob, type RepositorySummary } from "../lib/jobs";

const DEMO_URL = "https://github.com/rmarathe-hub/retail-retention-revenue-intel";

type ImportRepositoryPanelProps = {
  title?: string;
  description?: string;
  showDemoHint?: boolean;
  showWorkspaceLinksOnReady?: boolean;
  onImported?: (result: {
    repository: RepositorySummary;
    job: IndexingJob;
    created_new_job: boolean;
  }) => void;
};

export function ImportRepositoryPanel({
  title = "Import a public GitHub repository",
  description = "Paste an HTTPS URL, optionally choose a branch, then watch Cloning → … → Ready.",
  showDemoHint = true,
  showWorkspaceLinksOnReady = true,
  onImported,
}: ImportRepositoryPanelProps) {
  const queryClient = useQueryClient();
  const [url, setUrl] = useState(DEMO_URL);
  const [branch, setBranch] = useState("");
  const [activeJobId, setActiveJobId] = useState<string | null>(null);
  const [repository, setRepository] = useState<RepositorySummary | null>(null);

  const jobQuery = useQuery({
    queryKey: ["job", activeJobId],
    queryFn: () => fetchJob(activeJobId!),
    enabled: Boolean(activeJobId),
    refetchInterval: (query) => {
      const job = query.state.data;
      if (!job) return 1500;
      return isTerminalStatus(job.status) ? false : 1500;
    },
  });

  const importMutation = useMutation({
    mutationFn: () => importRepository(url.trim(), branch.trim() || undefined),
    onSuccess: (result) => {
      setActiveJobId(result.job.id);
      setRepository(result.repository);
      void queryClient.invalidateQueries({ queryKey: ["jobs"] });
      void queryClient.invalidateQueries({ queryKey: ["repositories"] });
      onImported?.(result);
    },
  });

  const job: IndexingJob | undefined = jobQuery.data;

  const repoLabel = useMemo(() => {
    if (!repository) return undefined;
    const branchLabel = repository.default_branch
      ? ` · ${repository.default_branch}`
      : "";
    return `${repository.owner_name}/${repository.name}${branchLabel}`;
  }, [repository]);

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!url.trim()) return;
    importMutation.mutate();
  }

  return (
    <div className="space-y-4">
      <section className="rounded-xl border border-[var(--border)] bg-[var(--panel)] p-6">
        <h3 className="text-lg font-semibold">{title}</h3>
        <p className="mt-1 text-sm text-[var(--muted)]">{description}</p>
        {showDemoHint && (
          <p className="mt-2 text-xs text-[var(--muted)]">
            Public GitHub HTTPS only. Demo URL is prefilled — replace it with any public repo.
          </p>
        )}

        <form className="mt-4 flex flex-col gap-3" onSubmit={onSubmit}>
          <label className="flex flex-col gap-1 text-sm">
            <span className="text-[var(--muted)]">Repository URL</span>
            <input
              className="rounded-md border border-[var(--border)] bg-[color-mix(in_srgb,var(--bg)_70%,black)] px-3 py-2 text-sm outline-none ring-[var(--accent)] focus:ring-2"
              value={url}
              onChange={(event) => setUrl(event.target.value)}
              placeholder="https://github.com/owner/repo"
              aria-label="Repository URL"
              name="repository_url"
            />
          </label>

          <label className="flex flex-col gap-1 text-sm">
            <span className="text-[var(--muted)]">Branch (optional)</span>
            <input
              className="rounded-md border border-[var(--border)] bg-[color-mix(in_srgb,var(--bg)_70%,black)] px-3 py-2 text-sm outline-none ring-[var(--accent)] focus:ring-2"
              value={branch}
              onChange={(event) => setBranch(event.target.value)}
              placeholder="Leave empty for remote default"
              aria-label="Branch"
              name="branch"
            />
          </label>

          <div className="flex flex-wrap items-center gap-3">
            <button
              type="submit"
              className="rounded-md bg-[var(--accent)] px-4 py-2 text-sm font-medium text-white disabled:opacity-60"
              disabled={importMutation.isPending || !url.trim()}
            >
              {importMutation.isPending ? "Starting…" : "Start indexing"}
            </button>
            {importMutation.data && !importMutation.data.created_new_job && (
              <p className="text-xs text-amber-200">
                An indexing job is already active for this repository — showing live progress.
              </p>
            )}
          </div>
        </form>

        {importMutation.isError && (
          <p className="mt-3 text-sm text-rose-300">
            {(importMutation.error as Error).message}
          </p>
        )}
      </section>

      {activeJobId && (
        <section className="rounded-xl border border-[var(--border)] bg-[var(--panel)] p-6">
          {jobQuery.isLoading && !job ? (
            <p className="text-sm text-[var(--muted)]">Loading job progress…</p>
          ) : jobQuery.isError ? (
            <p className="text-sm text-rose-300">{(jobQuery.error as Error).message}</p>
          ) : job ? (
            <JobProgress
              job={job}
              repositoryLabel={repoLabel}
              showWorkspaceLinks={showWorkspaceLinksOnReady}
            />
          ) : null}
        </section>
      )}
    </div>
  );
}
