import { JOB_STAGES, stageIndex, type IndexingJob, type JobStatus } from "../lib/jobs";

type JobProgressProps = {
  job: IndexingJob;
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

export function JobProgress({ job }: JobProgressProps) {
  const activeIndex = stageIndex(job.stage);
  const failed = job.status === "FAILED";

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="text-xs tracking-[0.18em] text-[var(--muted)] uppercase">Indexing job</p>
          <p className="mt-1 font-mono text-sm text-[var(--text)]">{job.id}</p>
        </div>
        <div className="text-right text-sm">
          <p className={statusTone(job.status)}>{job.status}</p>
          <p className="text-[var(--muted)]">{job.progress_percentage}% complete</p>
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
          const reached = index <= activeIndex;
          const current = index === activeIndex && job.status !== "SUCCEEDED";
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

      {failed && (
        <div className="rounded-lg border border-rose-500/40 bg-rose-500/10 px-3 py-2 text-sm text-rose-100">
          <p className="font-medium">{job.error_code ?? "error"}</p>
          <p className="mt-1 text-rose-100/80">{job.error_message ?? "Job failed"}</p>
        </div>
      )}
    </div>
  );
}
