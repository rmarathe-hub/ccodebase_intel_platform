import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { PageShell } from "../components/PageShell";
import { fetchRepositories, fetchRepositoryChunksSearch } from "../lib/api";
import {
  citationLabel,
  searchModeLabel,
  type SearchMode,
} from "../lib/chunks";
import { supportLevelLabel, type SupportLevel } from "../lib/files";

const SEARCH_MODES: Array<{ id: SearchMode; label: string }> = [
  { id: "exact", label: "Exact" },
  { id: "hybrid", label: "Hybrid" },
  { id: "semantic", label: "Semantic" },
  { id: "rrf", label: "RRF (Ask candidates)" },
  { id: "rerank", label: "Rerank (Ask)" },
];

const LEVEL_FILTERS: Array<{ id: "all" | SupportLevel; label: string }> = [
  { id: "all", label: "All" },
  { id: "deep", label: "Deep" },
  { id: "generic", label: "Generic" },
];

export function SearchPage() {
  const [repositoryId, setRepositoryId] = useState("");
  const [query, setQuery] = useState("");
  const [submittedQuery, setSubmittedQuery] = useState("");
  const [searchMode, setSearchMode] = useState<SearchMode>("exact");
  const [level, setLevel] = useState<"all" | SupportLevel>("all");
  const [pathPrefix, setPathPrefix] = useState("");
  const [language, setLanguage] = useState("");

  const reposQuery = useQuery({
    queryKey: ["repositories"],
    queryFn: () => fetchRepositories(50),
  });

  const selectedId = repositoryId || reposQuery.data?.[0]?.id || "";

  const searchQuery = useQuery({
    queryKey: [
      "repository-chunks-search",
      selectedId,
      submittedQuery,
      searchMode,
      level,
      pathPrefix,
      language,
    ],
    queryFn: () =>
      fetchRepositoryChunksSearch(selectedId, {
        q: submittedQuery,
        search_mode: searchMode,
        support_level: level === "all" ? undefined : level,
        path_prefix: pathPrefix.trim() || undefined,
        language: language.trim() || undefined,
        limit: 50,
        offset: 0,
      }),
    enabled: Boolean(selectedId && submittedQuery.trim()),
  });

  const selectedRepo = useMemo(
    () => reposQuery.data?.find((repo) => repo.id === selectedId),
    [reposQuery.data, selectedId],
  );

  return (
    <div className="space-y-4">
      <PageShell
        title="Search"
        description="Search indexed chunks with exact, semantic, or hybrid ranking. Citations always point at parser-derived file:line ranges."
      />

      <section className="rounded-xl border border-[var(--border)] bg-[var(--panel)] p-6">
        <form
          className="flex flex-col gap-3"
          onSubmit={(event) => {
            event.preventDefault();
            setSubmittedQuery(query.trim());
          }}
        >
          <div className="flex flex-col gap-3 lg:flex-row lg:items-end">
            <label className="flex min-w-0 flex-1 flex-col gap-1 text-sm">
              <span className="text-[var(--muted)]">Repository</span>
              <select
                className="rounded-md border border-[var(--border)] bg-[color-mix(in_srgb,var(--bg)_70%,black)] px-3 py-2 outline-none ring-[var(--accent)] focus:ring-2"
                value={selectedId}
                onChange={(event) => setRepositoryId(event.target.value)}
                aria-label="Repository"
              >
                {(reposQuery.data ?? []).length === 0 && (
                  <option value="">No repositories imported yet</option>
                )}
                {(reposQuery.data ?? []).map((repo) => (
                  <option key={repo.id} value={repo.id}>
                    {repo.owner_name}/{repo.name}
                  </option>
                ))}
              </select>
            </label>

            <label className="flex min-w-[12rem] flex-col gap-1 text-sm">
              <span className="text-[var(--muted)]">Mode</span>
              <select
                className="rounded-md border border-[var(--border)] bg-[color-mix(in_srgb,var(--bg)_70%,black)] px-3 py-2 outline-none ring-[var(--accent)] focus:ring-2"
                value={searchMode}
                onChange={(event) => setSearchMode(event.target.value as SearchMode)}
                aria-label="Search mode"
              >
                {SEARCH_MODES.map((mode) => (
                  <option key={mode.id} value={mode.id}>
                    {mode.label}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <label className="flex flex-col gap-1 text-sm">
            <span className="text-[var(--muted)]">Query</span>
            <input
              className="rounded-md border border-[var(--border)] bg-[color-mix(in_srgb,var(--bg)_70%,black)] px-3 py-2 outline-none ring-[var(--accent)] focus:ring-2"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="e.g. authentication middleware or UserService"
              aria-label="Search query"
            />
          </label>

          <div className="flex flex-col gap-3 lg:flex-row">
            <label className="flex min-w-0 flex-1 flex-col gap-1 text-sm">
              <span className="text-[var(--muted)]">Path prefix</span>
              <input
                className="rounded-md border border-[var(--border)] bg-[color-mix(in_srgb,var(--bg)_70%,black)] px-3 py-2 outline-none ring-[var(--accent)] focus:ring-2"
                value={pathPrefix}
                onChange={(event) => setPathPrefix(event.target.value)}
                placeholder="src/"
                aria-label="Path prefix"
              />
            </label>
            <label className="flex min-w-0 flex-1 flex-col gap-1 text-sm">
              <span className="text-[var(--muted)]">Language</span>
              <input
                className="rounded-md border border-[var(--border)] bg-[color-mix(in_srgb,var(--bg)_70%,black)] px-3 py-2 outline-none ring-[var(--accent)] focus:ring-2"
                value={language}
                onChange={(event) => setLanguage(event.target.value)}
                placeholder="python"
                aria-label="Language"
              />
            </label>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            {LEVEL_FILTERS.map((item) => (
              <button
                key={item.id}
                type="button"
                className={[
                  "rounded-md border px-3 py-1.5 text-sm",
                  level === item.id
                    ? "border-[var(--accent)] bg-[color-mix(in_srgb,var(--accent)_20%,transparent)]"
                    : "border-[var(--border)]",
                ].join(" ")}
                onClick={() => setLevel(item.id)}
              >
                {item.label}
              </button>
            ))}
            <button
              type="submit"
              className="ml-auto rounded-md border border-[var(--accent)] bg-[color-mix(in_srgb,var(--accent)_25%,transparent)] px-4 py-1.5 text-sm font-medium"
            >
              Search
            </button>
          </div>
        </form>

        {selectedRepo && (
          <p className="mt-3 text-xs text-[var(--muted)]">
            Searching latest ready snapshot for {selectedRepo.owner_name}/{selectedRepo.name}
            {searchQuery.data?.snapshot_id
              ? ` · snapshot ${searchQuery.data.snapshot_id.slice(0, 8)}… · mode ${searchModeLabel(searchQuery.data.search_mode)}`
              : " · import a repo and wait for the worker before searching"}
          </p>
        )}
      </section>

      <section className="overflow-hidden rounded-xl border border-[var(--border)] bg-[var(--panel)]">
        {!submittedQuery.trim() ? (
          <p className="p-6 text-sm text-[var(--muted)]">
            Enter a query and press Search. Exact works without embeddings; semantic and hybrid
            need the Embedding stage.
          </p>
        ) : reposQuery.isLoading || searchQuery.isLoading ? (
          <p className="p-6 text-sm text-[var(--muted)]">Searching…</p>
        ) : reposQuery.isError ? (
          <p className="p-6 text-sm text-rose-300">{(reposQuery.error as Error).message}</p>
        ) : searchQuery.isError ? (
          <p className="p-6 text-sm text-rose-300">{(searchQuery.error as Error).message}</p>
        ) : (searchQuery.data?.hits.length ?? 0) === 0 ? (
          <p className="p-6 text-sm text-[var(--muted)]">
            No chunks matched. Try exact mode for identifiers, or widen filters.
          </p>
        ) : (
          <ul className="divide-y divide-[var(--border)]/70">
            {searchQuery.data?.hits.map((hit) => (
              <li key={hit.id} className="px-4 py-4">
                <div className="flex flex-wrap items-center gap-2">
                  <code className="font-mono text-xs text-[var(--accent)]">
                    {citationLabel(hit)}
                  </code>
                  <span
                    className={[
                      "rounded px-2 py-0.5 text-xs",
                      hit.support_level === "deep"
                        ? "bg-emerald-500/15 text-emerald-200"
                        : hit.support_level === "generic"
                          ? "bg-sky-500/15 text-sky-200"
                          : "bg-zinc-500/20 text-zinc-300",
                    ].join(" ")}
                  >
                    {supportLevelLabel(hit.support_level)}
                  </span>
                  {hit.verified_deep ? (
                    <span className="rounded bg-emerald-500/10 px-2 py-0.5 text-xs text-emerald-200">
                      verified deep
                    </span>
                  ) : (
                    <span className="rounded bg-zinc-500/15 px-2 py-0.5 text-xs text-zinc-300">
                      not verified deep
                    </span>
                  )}
                  {hit.score != null && (
                    <span className="text-xs text-[var(--muted)]">
                      score {hit.score.toFixed(4)}
                    </span>
                  )}
                </div>
                {hit.score_breakdown && (
                  <p className="mt-1 text-xs text-[var(--muted)]">
                    {Object.entries(hit.score_breakdown)
                      .map(([key, value]) => `${key}=${value}`)
                      .join(" · ")}
                  </p>
                )}
                <pre className="mt-2 max-h-40 overflow-auto rounded-md border border-[var(--border)] bg-[color-mix(in_srgb,var(--bg)_75%,black)] p-3 font-mono text-xs whitespace-pre-wrap">
                  {hit.content.length > 800 ? `${hit.content.slice(0, 800)}…` : hit.content}
                </pre>
              </li>
            ))}
          </ul>
        )}
        {searchQuery.data && (
          <p className="border-t border-[var(--border)] px-4 py-3 text-xs text-[var(--muted)]">
            Showing {searchQuery.data.hits.length} of {searchQuery.data.total} hits
          </p>
        )}
      </section>

      <p className="text-xs text-[var(--muted)]">
        Honesty: exact search is LLM-independent. Semantic/hybrid use stored embeddings (local-hash
        in CI; Azure when configured). RRF merges exact∥semantic for Ask candidates; Rerank may
        use a mock or Azure chat (falls back to RRF). Generic hits are never verified-deep.
        Full Ask answers are Week 10 Days 5–6 — not this page.
      </p>
    </div>
  );
}
