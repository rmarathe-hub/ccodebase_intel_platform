import { Link } from "react-router-dom";
import { isCancellableStatus, jobErrorHint, jobErrorTitle } from "../lib/jobErrors";
import {
  JOB_STAGES,
  isJobReady,
  stageIndex,
  type IndexingJob,
  type JobStatus,
} from "../lib/jobs";

type JobProgressProps = {
  job: IndexingJob;
  repositoryLabel?: string;
  showWorkspaceLinks?: boolean;
  onCancel?: (jobId: string) => void;
  cancelPending?: boolean;
};

function statusTone(status: JobStatus): string {
  switch (status) {
    case "SUCCEEDED":
      return "text-emerald-300";
    case "FAILED":
      return "text-rose-300";
    case "CANCELLED":
      return "text-zinc-400";
    case "RUNNING":
      return "text-sky-300";
    default:
      return "text-amber-200";
  }
}

function statusLabel(job: IndexingJob): string {
  if (isJobReady(job)) return "Ready";
  return job.status;
}

function workspacePath(base: string, repositoryId: string): string {
  return `${base}?repo=${encodeURIComponent(repositoryId)}`;
}

export function JobProgress({
  job,
  repositoryLabel,
  showWorkspaceLinks = false,
  onCancel,
  cancelPending = false,
}: JobProgressProps) {
  const activeIndex = stageIndex(job.stage);
  const failed = job.status === "FAILED";
  const cancelled = job.status === "CANCELLED";
  const ready = isJobReady(job);
  const canCancel = Boolean(onCancel) && isCancellableStatus(job.status);

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="text-xs tracking-[0.18em] text-[var(--muted)] uppercase">
            Indexing pipeline
          </p>
          {repositoryLabel ? (
            <p className="mt-1 text-base font-medium">{repositoryLabel}</p>
          ) : null}
          <p className="mt-1 font-mono text-xs text-[var(--muted)]">{job.id}</p>
        </div>
        <div className="text-right text-sm">
          <p className={statusTone(job.status)}>{statusLabel(job)}</p>
          <p className="text-[var(--muted)]">{job.progress_percentage}% complete</p>
          {canCancel && (
            <button
              type="button"
              className="mt-2 rounded-md border border-rose-400/40 px-2.5 py-1 text-xs text-rose-100 hover:border-rose-300 disabled:opacity-50"
              onClick={() => onCancel?.(job.id)}
              disabled={cancelPending}
            >
              {cancelPending ? "Cancelling…" : "Cancel indexing"}
            </button>
          )}
        </div>
      </div>

      <div className="h-2 overflow-hidden rounded-full bg-[color-mix(in_srgb,var(--border)_80%,black)]">
        <div
          className="h-full rounded-full bg-[var(--accent)] transition-[width] duration-500"
          style={{ width: `${Math.min(100, Math.max(0, job.progress_percentage))}%` }}
        />
      </div>

      <ol className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
        {JOB_STAGES.map((stage, index) => {
          const reached = index <= activeIndex || ready;
          const current = index === activeIndex && !ready && job.status !== "SUCCEEDED";
          return (
            <li
              key={stage.id}
              className={[
                "rounded-lg border px-3 py-2 text-sm",
                current
                  ? "border-[var(--accent)] bg-[color-mix(in_srgb,var(--accent)_18%,transparent)]"
                  : reached
                    ? "border-[var(--border)] bg-[color-mix(in_srgb,var(--panel)_70%,black)]"
                    : "border-[var(--border)] opacity-45",
              ].join(" ")}
            >
              <p className="text-xs text-[var(--muted)]">
                {String(index + 1).padStart(2, "0")}
              </p>
              <p className="mt-1 font-medium">{stage.label}</p>
            </li>
          );
        })}
      </ol>

      {ready && showWorkspaceLinks && (
        <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-4 py-3">
          <p className="text-sm font-medium text-emerald-100">
            Repository is Ready — open a workspace surface
          </p>
          <div className="mt-3 flex flex-wrap gap-2">
            {(
              [
                ["/search", "Search"],
                ["/ask", "Ask"],
                ["/graph", "Graph"],
                ["/symbols", "Symbols"],
                ["/files", "Files"],
              ] as const
            ).map(([to, label]) => (
              <Link
                key={to}
                to={workspacePath(to, job.repository_id)}
                className="rounded-md border border-emerald-400/40 bg-[color-mix(in_srgb,var(--bg)_50%,transparent)] px-3 py-1.5 text-sm text-emerald-50 hover:border-emerald-300"
              >
                {label}
              </Link>
            ))}
          </div>
        </div>
      )}

      {(failed || cancelled) && (
        <div
          className={[
            "rounded-lg border px-3 py-2 text-sm",
            failed
              ? "border-rose-500/40 bg-rose-500/10 text-rose-100"
              : "border-zinc-500/40 bg-zinc-500/10 text-zinc-200",
          ].join(" ")}
        >
          <p className="font-medium">{jobErrorTitle(job.error_code)}</p>
          {job.error_message ? (
            <p className="mt-1 opacity-80">{job.error_message}</p>
          ) : null}
          {jobErrorHint(job.error_code) ? (
            <p className="mt-2 text-xs opacity-70">{jobErrorHint(job.error_code)}</p>
          ) : null}
        </div>
      )}
    </div>
  );
}
