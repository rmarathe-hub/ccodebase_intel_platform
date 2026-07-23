import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  cleanupAllRepositories,
  cleanupTestRepositories,
  deleteRepository,
  reindexRepository,
} from "../lib/api";
import type { RepositoryListItem } from "../lib/files";

type Props = {
  repo: RepositoryListItem;
  /** Compact row actions vs selected-detail actions */
  compact?: boolean;
  /** Navigate to jobs after queueing re-index */
  linkJobsOnReindex?: boolean;
};

export function RepositoryCardActions({
  repo,
  compact = false,
  linkJobsOnReindex = false,
}: Props) {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const [message, setMessage] = useState<string | null>(null);

  const invalidate = () => {
    void queryClient.invalidateQueries({ queryKey: ["repositories"] });
    void queryClient.invalidateQueries({ queryKey: ["jobs"] });
    void queryClient.invalidateQueries({ queryKey: ["repository-jobs", repo.id] });
    void queryClient.invalidateQueries({ queryKey: ["repository-summary", repo.id] });
  };

  const reindexMutation = useMutation({
    mutationFn: (force: boolean) => reindexRepository(repo.id, { force }),
    onSuccess: (result, force) => {
      invalidate();
      void queryClient.invalidateQueries({ queryKey: ["job", result.job.id] });
      setMessage(
        force
          ? result.created_new_job
            ? "Force re-index queued."
            : "Indexing already active."
          : result.created_new_job
            ? "Re-index queued."
            : "Indexing already active.",
      );
      if (linkJobsOnReindex && result.created_new_job) {
        navigate(`/jobs?job=${encodeURIComponent(result.job.id)}`);
      }
    },
    onError: (err) => setMessage((err as Error).message),
  });

  const deleteMutation = useMutation({
    mutationFn: () => deleteRepository(repo.id),
    onSuccess: () => {
      invalidate();
      setMessage(`Deleted ${repo.owner_name}/${repo.name}.`);
      navigate("/repositories");
    },
    onError: (err) => setMessage((err as Error).message),
  });

  const busy = reindexMutation.isPending || deleteMutation.isPending;
  const btn = compact
    ? "rounded border border-[var(--border)] px-2 py-1 text-xs font-medium disabled:opacity-60"
    : "rounded-md border border-[var(--border)] px-3 py-1.5 text-sm font-medium disabled:opacity-60";
  const accentBtn = compact
    ? "rounded border border-transparent bg-[var(--accent)] px-2 py-1 text-xs font-medium text-white disabled:opacity-60"
    : "rounded-md bg-[var(--accent)] px-3 py-1.5 text-sm font-medium text-white disabled:opacity-60";
  const dangerBtn = compact
    ? "rounded border border-rose-500/40 px-2 py-1 text-xs font-medium text-rose-300 disabled:opacity-60"
    : "rounded-md border border-rose-500/40 px-3 py-1.5 text-sm font-medium text-rose-300 disabled:opacity-60";

  return (
    <div className="space-y-1" onClick={(e) => e.stopPropagation()}>
      <div className="flex flex-wrap items-center gap-1.5">
        <button
          type="button"
          className={accentBtn}
          disabled={busy}
          title="Always rebuild chunks and embeddings"
          onClick={() => reindexMutation.mutate(true)}
        >
          {reindexMutation.isPending ? "Queueing…" : "Force Re-index"}
        </button>
        <button
          type="button"
          className={btn}
          disabled={busy}
          onClick={() => reindexMutation.mutate(false)}
        >
          Re-index
        </button>
        <button
          type="button"
          className={dangerBtn}
          disabled={busy}
          onClick={() => {
            const ok = window.confirm(
              `Delete ${repo.owner_name}/${repo.name}? This removes all indexed data.`,
            );
            if (ok) deleteMutation.mutate();
          }}
        >
          Delete
        </button>
        {!compact && (
          <Link
            className="text-xs text-[var(--accent)] underline"
            to={`/repositories/${repo.id}`}
          >
            Open
          </Link>
        )}
      </div>
      {message && (
        <p className="text-xs text-[var(--muted)] max-w-md truncate" title={message}>
          {message}
        </p>
      )}
    </div>
  );
}

export function CleanupTestRepositoriesButton() {
  const queryClient = useQueryClient();
  const [result, setResult] = useState<string | null>(null);

  const cleanupMutation = useMutation({
    mutationFn: () => cleanupTestRepositories(),
    onSuccess: (body) => {
      void queryClient.invalidateQueries({ queryKey: ["repositories"] });
      void queryClient.invalidateQueries({ queryKey: ["jobs"] });
      setResult(
        body.deleted_count === 0
          ? "No test repositories matched."
          : `Deleted ${body.deleted_count} test repositor${body.deleted_count === 1 ? "y" : "ies"}.`,
      );
    },
    onError: (err) => setResult((err as Error).message),
  });

  return (
    <div className="space-y-1">
      <button
        type="button"
        className="rounded-md border border-rose-500/40 px-3 py-1.5 text-sm font-medium text-rose-300 disabled:opacity-60"
        disabled={cleanupMutation.isPending}
        onClick={() => {
          const ok = window.confirm(
            "Delete all local test/fixture repositories (week10/ask-*, emb-*, cfg-*, gen-*, …)? Real imports are kept.",
          );
          if (ok) cleanupMutation.mutate();
        }}
      >
        {cleanupMutation.isPending ? "Cleaning…" : "Delete test repositories"}
      </button>
      {result && <p className="text-xs text-[var(--muted)]">{result}</p>}
    </div>
  );
}

export function CleanupAllRepositoriesButton() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const [result, setResult] = useState<string | null>(null);

  const cleanupMutation = useMutation({
    mutationFn: () => cleanupAllRepositories(),
    onSuccess: (body) => {
      void queryClient.invalidateQueries({ queryKey: ["repositories"] });
      void queryClient.invalidateQueries({ queryKey: ["jobs"] });
      setResult(
        body.deleted_count === 0
          ? "No repositories to delete."
          : `Deleted all ${body.deleted_count} repositor${body.deleted_count === 1 ? "y" : "ies"}.`,
      );
      navigate("/repositories");
    },
    onError: (err) => setResult((err as Error).message),
  });

  return (
    <div className="space-y-1">
      <button
        type="button"
        className="rounded-md border border-rose-600 bg-rose-950/40 px-3 py-1.5 text-sm font-medium text-rose-200 disabled:opacity-60"
        disabled={cleanupMutation.isPending}
        onClick={() => {
          const ok = window.confirm(
            "Delete ALL repositories and their indexed data? This cannot be undone.",
          );
          if (!ok) return;
          const typed = window.prompt(
            'Type DELETE ALL to confirm wiping every repository from this local database.',
          );
          if (typed?.trim() !== "DELETE ALL") {
            setResult("Cancelled — confirmation text did not match.");
            return;
          }
          cleanupMutation.mutate();
        }}
      >
        {cleanupMutation.isPending ? "Deleting…" : "Delete all repositories"}
      </button>
      {result && <p className="text-xs text-[var(--muted)]">{result}</p>}
    </div>
  );
}
