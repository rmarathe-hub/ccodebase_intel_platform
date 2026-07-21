/** Human-readable indexing failure / cancel messages for product UX. */

const TITLES: Record<string, string> = {
  repo_too_large: "Repository exceeds clone size limit",
  clone_timeout: "Clone timed out",
  clone_failed: "Clone failed",
  git_missing: "Git is not available",
  cancelled: "Indexing cancelled",
  worker_error: "Indexing worker error",
  snapshot_validation_failed: "Snapshot validation failed",
};

const HINTS: Record<string, string> = {
  repo_too_large:
    "Public demos use a shallow clone size cap. Try a smaller repository, or raise GIT_CLONE_MAX_BYTES for local use.",
  clone_timeout:
    "The clone did not finish within the configured timeout. Retry, or increase GIT_CLONE_TIMEOUT_SECONDS.",
  clone_failed:
    "Git could not clone this URL. Confirm the repository is public and the branch exists.",
  cancelled: "You can retry from Jobs or re-index from the repository overview.",
};

export function jobErrorTitle(errorCode: string | null | undefined): string {
  if (!errorCode) return "Indexing failed";
  return TITLES[errorCode] ?? errorCode.replaceAll("_", " ");
}

export function jobErrorHint(errorCode: string | null | undefined): string | null {
  if (!errorCode) return null;
  return HINTS[errorCode] ?? null;
}

export function isCancellableStatus(status: string): boolean {
  return status === "QUEUED" || status === "RUNNING";
}
