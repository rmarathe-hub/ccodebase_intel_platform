import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
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
  const [searchParams, setSearchParams] = useSearchParams();
  const repoFromUrl = searchParams.get("repo") ?? "";
  const [repositoryId, setRepositoryId] = useState(repoFromUrl);
  const [query, setQuery] = useState(searchParams.get("q") ?? "");
  const [submittedQuery, setSubmittedQuery] = useState(searchParams.get("q") ?? "");
  const [searchMode, setSearchMode] = useState<SearchMode>(
    (searchParams.get("mode") as SearchMode) || "exact",
  );
  const [level, setLevel] = useState<"all" | SupportLevel>(
    (searchParams.get("level") as "all" | SupportLevel) || "all",
  );
  const [pathPrefix, setPathPrefix] = useState(searchParams.get("path") ?? "");
  const [language, setLanguage] = useState(searchParams.get("lang") ?? "");

  const reposQuery = useQuery({
    queryKey: ["repositories"],
    queryFn: () => fetchRepositories(50),
  });

  const selectedId = repositoryId || repoFromUrl || reposQuery.data?.[0]?.id || "";
  const hasRepos = (reposQuery.data?.length ?? 0) > 0;
  const filtersActive =
    level !== "all" || Boolean(pathPrefix.trim()) || Boolean(language.trim());

  function syncParams(next: {
    repo?: string;
    q?: string;
    mode?: SearchMode;
    level?: "all" | SupportLevel;
    path?: string;
    lang?: string;
  }) {
    const params = new URLSearchParams(searchParams);
    const repo = next.repo ?? selectedId;
    if (repo) params.set("repo", repo);
    else params.delete("repo");
    const q = next.q ?? submittedQuery;
    if (q) params.set("q", q);
    else params.delete("q");
    const mode = next.mode ?? searchMode;
    if (mode && mode !== "exact") params.set("mode", mode);
    else params.delete("mode");
    const lvl = next.level ?? level;
    if (lvl && lvl !== "all") params.set("level", lvl);
    else params.delete("level");
    const path = (next.path ?? pathPrefix).trim();
    if (path) params.set("path", path);
    else params.delete("path");
    const lang = (next.lang ?? language).trim();
    if (lang) params.set("lang", lang);
    else params.delete("lang");
    setSearchParams(params, { replace: true });
  }

  function selectRepository(nextId: string) {
    setRepositoryId(nextId);
    syncParams({ repo: nextId });
  }

  function clearFilters() {
    setLevel("all");
    setPathPrefix("");
    setLanguage("");
    syncParams({ level: "all", path: "", lang: "" });
  }

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
        {!reposQuery.isLoading && !hasRepos && (
          <div className="mb-4 rounded-lg border border-amber-500/30 bg-amber-500/10 px-3 py-2 text-sm text-amber-100">
            No repositories indexed yet.{" "}
            <Link className="underline" to="/">
              Import a public GitHub URL
            </Link>{" "}
            first.
          </div>
        )}

        <form
          className="flex flex-col gap-3"
          onSubmit={(event) => {
            event.preventDefault();
            const next = query.trim();
            setSubmittedQuery(next);
            syncParams({ q: next, mode: searchMode, level, path: pathPrefix, lang: language });
          }}
        >
          <div className="flex flex-col gap-3 lg:flex-row lg:items-end">
            <label className="flex min-w-0 flex-1 flex-col gap-1 text-sm">
              <span className="text-[var(--muted)]">Repository</span>
              <select
                className="rounded-md border border-[var(--border)] bg-[color-mix(in_srgb,var(--bg)_70%,black)] px-3 py-2 outline-none ring-[var(--accent)] focus:ring-2"
                value={selectedId}
                onChange={(event) => selectRepository(event.target.value)}
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
                onChange={(event) => {
                  const mode = event.target.value as SearchMode;
                  setSearchMode(mode);
                  syncParams({ mode });
                }}
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
                onClick={() => {
                  setLevel(item.id);
                  syncParams({ level: item.id });
                }}
              >
                {item.label}
              </button>
            ))}
            {filtersActive && (
              <button
                type="button"
                className="rounded-md border border-[var(--border)] px-3 py-1.5 text-sm text-[var(--muted)] hover:text-[var(--text)]"
                onClick={clearFilters}
              >
                Clear filters
              </button>
            )}
            <button
              type="submit"
              disabled={!selectedId || !query.trim()}
              className="ml-auto rounded-md border border-[var(--accent)] bg-[color-mix(in_srgb,var(--accent)_25%,transparent)] px-4 py-1.5 text-sm font-medium disabled:opacity-50"
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
        {!hasRepos && !reposQuery.isLoading ? (
          <p className="p-6 text-sm text-[var(--muted)]">
            Nothing to search yet. Import a repository from the Dashboard, wait until Ready, then
            come back.
          </p>
        ) : !submittedQuery.trim() ? (
          <p className="p-6 text-sm text-[var(--muted)]">
            Enter a query and press Search. Exact works without embeddings; semantic and hybrid
            need the Embedding stage. Narrow with path / language / deep-vs-generic filters.
          </p>
        ) : reposQuery.isLoading || searchQuery.isLoading ? (
          <p className="p-6 text-sm text-[var(--muted)]">Searching…</p>
        ) : reposQuery.isError ? (
          <p className="p-6 text-sm text-rose-300">{(reposQuery.error as Error).message}</p>
        ) : searchQuery.isError ? (
          <p className="p-6 text-sm text-rose-300">{(searchQuery.error as Error).message}</p>
        ) : searchQuery.data?.snapshot_id == null ? (
          <p className="p-6 text-sm text-amber-200">
            No ready snapshot for this repository yet. Open Jobs or Repository overview and wait
            for Ready, or re-index.
          </p>
        ) : (searchQuery.data?.hits.length ?? 0) === 0 ? (
          <div className="space-y-2 p-6 text-sm text-[var(--muted)]">
            <p>No chunks matched.</p>
            <ul className="list-disc space-y-1 pl-5">
              <li>Try exact mode for identifiers / symbol names.</li>
              <li>Clear path or language filters if they are too narrow.</li>
              <li>Generic languages still return honest non-deep hits.</li>
            </ul>
          </div>
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
        {searchQuery.data && searchQuery.data.snapshot_id && (
          <p className="border-t border-[var(--border)] px-4 py-3 text-xs text-[var(--muted)]">
            Showing {searchQuery.data.hits.length} of {searchQuery.data.total} hits
          </p>
        )}
      </section>

      <p className="text-xs text-[var(--muted)]">
        Honesty: exact search is LLM-independent. Semantic/hybrid use stored embeddings (local-hash
        in CI; Azure when configured). RRF merges exact∥semantic for Ask candidates; Rerank may
        use a mock or Azure chat (falls back to RRF). Generic hits are never verified-deep.
        For grounded NL answers with citation validation, use the Ask page.
      </p>
    </div>
  );
}
