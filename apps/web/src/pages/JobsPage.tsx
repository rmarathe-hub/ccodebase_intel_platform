import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { ImportRepositoryPanel } from "../components/ImportRepositoryPanel";
import { JobProgress } from "../components/JobProgress";
import { PageShell } from "../components/PageShell";
import { cancelJob, fetchJob, fetchJobs, retryJob } from "../lib/api";
import { isTerminalStatus, type IndexingJob } from "../lib/jobs";

export function JobsPage() {
  const queryClient = useQueryClient();
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

  const retryMutation = useMutation({
    mutationFn: (jobId: string) => retryJob(jobId),
    onSuccess: (job) => {
      setSelectedJobId(job.id);
      void queryClient.invalidateQueries({ queryKey: ["jobs"] });
      void queryClient.invalidateQueries({ queryKey: ["job", job.id] });
    },
  });

  const cancelMutation = useMutation({
    mutationFn: (jobId: string) => cancelJob(jobId),
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

  return (
    <div className="space-y-4">
      <PageShell
        title="Jobs"
        description="Import from here or the Dashboard, then track every indexing stage through Ready. Cancel in-flight jobs or retry failed ones from history."
      />

      <ImportRepositoryPanel
        title="Import repository"
        showWorkspaceLinksOnReady
        onImported={(result) => setSelectedJobId(result.job.id)}
      />

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
                  className={[
                    "flex w-full items-center justify-between gap-3 py-3 text-left hover:bg-[color-mix(in_srgb,var(--bg)_35%,transparent)]",
                    selectedJobId === job.id
                      ? "bg-[color-mix(in_srgb,var(--accent)_10%,transparent)]"
                      : "",
                  ].join(" ")}
                  onClick={() => setSelectedJobId(job.id)}
                >
                  <div>
                    <p className="font-mono text-xs text-[var(--muted)]">{job.id}</p>
                    <p className="mt-1 text-sm">
                      {job.stage.replaceAll("_", " ")} · {job.progress_percentage}%
                    </p>
                  </div>
                  <span className="text-xs tracking-wide text-[var(--muted)] uppercase">
                    {job.status === "SUCCEEDED" ? "Ready" : job.status}
                  </span>
                </button>
              </li>
            ))}
          </ul>
        )}

        {selectedJob && (
          <div className="mt-6 border-t border-[var(--border)] pt-6">
            <JobProgress
              job={selectedJob}
              showWorkspaceLinks
              onCancel={(jobId) => cancelMutation.mutate(jobId)}
              cancelPending={cancelMutation.isPending}
            />
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
          </div>
        )}
      </section>
    </div>
  );
}
