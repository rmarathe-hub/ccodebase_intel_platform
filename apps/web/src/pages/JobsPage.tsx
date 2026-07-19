import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import type { FormEvent } from "react";
import { JobProgress } from "../components/JobProgress";
import { PageShell } from "../components/PageShell";
import { fetchJob, fetchJobs, importRepository, retryJob } from "../lib/api";
import { isTerminalStatus, type IndexingJob } from "../lib/jobs";

const DEMO_URL = "https://github.com/rmarathe-hub/retail-retention-revenue-intel";

export function JobsPage() {
  const queryClient = useQueryClient();
  const [url, setUrl] = useState(DEMO_URL);
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);

  const jobsQuery = useQuery({
    queryKey: ["jobs"],
    queryFn: () => fetchJobs(30),
    refetchInterval: (query) => {
      const jobs = query.state.data ?? [];
      return jobs.some((job) => !isTerminalStatus(job.status)) ? 2000 : false;
    },
  });

  const selectedJobQuery = useQuery({
    queryKey: ["job", selectedJobId],
    queryFn: () => fetchJob(selectedJobId!),
    enabled: Boolean(selectedJobId),
    refetchInterval: (query) => {
      const job = query.state.data;
      if (!job) return false;
      return isTerminalStatus(job.status) ? false : 1500;
    },
  });

  const importMutation = useMutation({
    mutationFn: (repositoryUrl: string) => importRepository(repositoryUrl),
    onSuccess: (result) => {
      setSelectedJobId(result.job.id);
      void queryClient.invalidateQueries({ queryKey: ["jobs"] });
    },
  });

  const retryMutation = useMutation({
    mutationFn: (jobId: string) => retryJob(jobId),
    onSuccess: (job) => {
      setSelectedJobId(job.id);
      void queryClient.invalidateQueries({ queryKey: ["jobs"] });
      void queryClient.invalidateQueries({ queryKey: ["job", job.id] });
    },
  });

  const selectedJob: IndexingJob | undefined = useMemo(() => {
    if (selectedJobQuery.data) return selectedJobQuery.data;
    return jobsQuery.data?.find((job) => job.id === selectedJobId);
  }, [jobsQuery.data, selectedJobId, selectedJobQuery.data]);

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    importMutation.mutate(url.trim());
  }

  return (
    <div className="space-y-4">
      <PageShell
        title="Jobs"
        description="Track indexing through clone, file discovery, and Python AST parsing. Relationships, chunking, and embedding stages are reserved for later work; a successful job today means files were classified and Python deep files were parsed into verified symbols."
      />

      <section className="rounded-xl border border-[var(--border)] bg-[var(--panel)] p-6">
        <h3 className="text-lg font-semibold">Import repository</h3>
        <p className="mt-1 text-sm text-[var(--muted)]">
          Public GitHub HTTPS URLs only. Demo fixture is prefilled.
        </p>
        <form className="mt-4 flex flex-col gap-3 sm:flex-row" onSubmit={onSubmit}>
          <input
            className="min-w-0 flex-1 rounded-md border border-[var(--border)] bg-[color-mix(in_srgb,var(--bg)_70%,black)] px-3 py-2 text-sm outline-none ring-[var(--accent)] focus:ring-2"
            value={url}
            onChange={(event) => setUrl(event.target.value)}
            placeholder="https://github.com/owner/repo"
            aria-label="Repository URL"
          />
          <button
            type="submit"
            className="rounded-md bg-[var(--accent)] px-4 py-2 text-sm font-medium text-white disabled:opacity-60"
            disabled={importMutation.isPending || !url.trim()}
          >
            {importMutation.isPending ? "Importing…" : "Start import"}
          </button>
        </form>
        {importMutation.isError && (
          <p className="mt-3 text-sm text-rose-300">
            {(importMutation.error as Error).message}
          </p>
        )}
      </section>

      {selectedJob && (
        <section className="rounded-xl border border-[var(--border)] bg-[var(--panel)] p-6">
          <JobProgress job={selectedJob} />
          {(selectedJob.status === "FAILED" || selectedJob.status === "CANCELLED") && (
            <button
              type="button"
              className="mt-4 rounded-md border border-[var(--border)] px-3 py-1.5 text-sm hover:border-[var(--accent)]"
              onClick={() => retryMutation.mutate(selectedJob.id)}
              disabled={retryMutation.isPending}
            >
              {retryMutation.isPending ? "Retrying…" : "Retry job"}
            </button>
          )}
        </section>
      )}

      <section className="rounded-xl border border-[var(--border)] bg-[var(--panel)] p-6">
        <div className="flex items-center justify-between gap-3">
          <h3 className="text-lg font-semibold">Recent jobs</h3>
          <button
            type="button"
            className="text-sm text-[var(--muted)] hover:text-[var(--text)]"
            onClick={() => void jobsQuery.refetch()}
          >
            Refresh
          </button>
        </div>
        {jobsQuery.isLoading && <p className="mt-3 text-sm text-[var(--muted)]">Loading jobs…</p>}
        {jobsQuery.isError && (
          <p className="mt-3 text-sm text-amber-300">
            Could not load jobs. Is the API running?
          </p>
        )}
        {jobsQuery.data && jobsQuery.data.length === 0 && (
          <p className="mt-3 text-sm text-[var(--muted)]">No jobs yet. Start an import above.</p>
        )}
        {jobsQuery.data && jobsQuery.data.length > 0 && (
          <ul className="mt-4 divide-y divide-[var(--border)]">
            {jobsQuery.data.map((job) => (
              <li key={job.id}>
                <button
                  type="button"
                  className="flex w-full items-center justify-between gap-3 py-3 text-left hover:bg-[color-mix(in_srgb,var(--bg)_35%,transparent)]"
                  onClick={() => setSelectedJobId(job.id)}
                >
                  <div>
                    <p className="font-mono text-xs text-[var(--muted)]">{job.id}</p>
                    <p className="mt-1 text-sm">
                      {job.stage.replaceAll("_", " ")} · {job.progress_percentage}%
                    </p>
                  </div>
                  <span className="text-xs tracking-wide text-[var(--muted)] uppercase">
                    {job.status}
                  </span>
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
