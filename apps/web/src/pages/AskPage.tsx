import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { PageShell } from "../components/PageShell";
import { askRepository, fetchAskBudget, fetchRepositories } from "../lib/api";
import {
  askCitationLabel,
  askStatusLabel,
  type AskBudgetEcho,
  type AskResponse,
} from "../lib/ask";
import { supportLevelLabel, type SupportLevel } from "../lib/files";

const LEVEL_FILTERS: Array<{ id: "all" | SupportLevel; label: string }> = [
  { id: "all", label: "All" },
  { id: "deep", label: "Deep" },
  { id: "generic", label: "Generic" },
];

function BudgetMeter({ budget }: { budget: AskBudgetEcho }) {
  const pct =
    budget.requests_limit > 0
      ? Math.min(100, Math.round((budget.requests_used / budget.requests_limit) * 100))
      : 0;
  return (
    <div className="rounded-lg border border-[var(--border)] px-3 py-2 text-xs">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <span className="text-[var(--muted)]">Per-repo Ask budget</span>
        <span className={budget.exhausted ? "text-rose-300" : "text-[var(--text)]"}>
          {budget.requests_used}/{budget.requests_limit} requests · {budget.remaining_requests}{" "}
          left
        </span>
      </div>
      <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-[color-mix(in_srgb,var(--border)_80%,black)]">
        <div
          className={[
            "h-full rounded-full transition-[width]",
            budget.exhausted || pct >= 90 ? "bg-rose-400" : "bg-[var(--accent)]",
          ].join(" ")}
          style={{ width: `${pct}%` }}
        />
      </div>
      <p className="mt-1 text-[var(--muted)]">
        Context token budget is separate (shown on each answer). Search stays free and
        deterministic.
      </p>
    </div>
  );
}

export function AskPage() {
  const queryClient = useQueryClient();
  const [searchParams, setSearchParams] = useSearchParams();
  const repoFromUrl = searchParams.get("repo") ?? "";
  const [repositoryId, setRepositoryId] = useState(repoFromUrl);
  const [question, setQuestion] = useState(searchParams.get("q") ?? "");
  const [level, setLevel] = useState<"all" | SupportLevel>(
    (searchParams.get("level") as "all" | SupportLevel) || "all",
  );
  const [pathPrefix, setPathPrefix] = useState(searchParams.get("path") ?? "");
  const [language, setLanguage] = useState(searchParams.get("lang") ?? "");
  const [applyRerank, setApplyRerank] = useState(true);
  const [expand, setExpand] = useState(true);
  const [result, setResult] = useState<AskResponse | null>(null);

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
    level?: "all" | SupportLevel;
    path?: string;
    lang?: string;
  }) {
    const params = new URLSearchParams(searchParams);
    const repo = next.repo ?? selectedId;
    if (repo) params.set("repo", repo);
    else params.delete("repo");
    const q = (next.q ?? question).trim();
    if (q) params.set("q", q);
    else params.delete("q");
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
    setResult(null);
    syncParams({ repo: nextId });
  }

  function clearFilters() {
    setLevel("all");
    setPathPrefix("");
    setLanguage("");
    syncParams({ level: "all", path: "", lang: "" });
  }

  const budgetQuery = useQuery({
    queryKey: ["ask-budget", selectedId],
    queryFn: () => fetchAskBudget(selectedId),
    enabled: Boolean(selectedId),
  });

  const askMutation = useMutation({
    mutationFn: (body: {
      question: string;
      support_level?: string;
      path_prefix?: string;
      language?: string;
      apply_rerank: boolean;
      expand: boolean;
    }) => askRepository(selectedId, body),
    onSuccess: (data) => {
      setResult(data);
      void queryClient.invalidateQueries({ queryKey: ["ask-budget", selectedId] });
    },
  });

  const selectedRepo = useMemo(
    () => reposQuery.data?.find((repo) => repo.id === selectedId),
    [reposQuery.data, selectedId],
  );

  const liveBudget = result?.budget ?? budgetQuery.data ?? null;
  const budgetBlocked = Boolean(liveBudget?.exhausted);

  return (
    <div className="space-y-4">
      <PageShell
        title="Ask"
        description="Ask grounded questions against indexed evidence. Every citation is post-validated against retrieved file:line spans."
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

        {liveBudget && <div className="mb-4"><BudgetMeter budget={liveBudget} /></div>}

        <form
          className="flex flex-col gap-3"
          onSubmit={(event) => {
            event.preventDefault();
            if (!selectedId || budgetBlocked) return;
            const fd = new FormData(event.currentTarget);
            const q = String(fd.get("question") ?? question).trim();
            if (!q) return;
            setQuestion(q);
            setResult(null);
            syncParams({ q, level, path: pathPrefix, lang: language });
            askMutation.mutate({
              question: q,
              support_level: level === "all" ? undefined : level,
              path_prefix:
                String(fd.get("path_prefix") ?? pathPrefix).trim() || undefined,
              language: String(fd.get("language") ?? language).trim() || undefined,
              apply_rerank: applyRerank,
              expand,
            });
          }}
        >
          <label className="flex min-w-0 flex-col gap-1 text-sm">
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

          <label className="flex flex-col gap-1 text-sm">
            <span className="text-[var(--muted)]">Question</span>
            <textarea
              name="question"
              className="min-h-[6rem] rounded-md border border-[var(--border)] bg-[color-mix(in_srgb,var(--bg)_70%,black)] px-3 py-2 outline-none ring-[var(--accent)] focus:ring-2"
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="e.g. how does authentication middleware work?"
              aria-label="Ask question"
            />
          </label>

          <div className="flex flex-col gap-3 lg:flex-row">
            <label className="flex min-w-0 flex-1 flex-col gap-1 text-sm">
              <span className="text-[var(--muted)]">Path prefix</span>
              <input
                name="path_prefix"
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
                name="language"
                className="rounded-md border border-[var(--border)] bg-[color-mix(in_srgb,var(--bg)_70%,black)] px-3 py-2 outline-none ring-[var(--accent)] focus:ring-2"
                value={language}
                onChange={(event) => setLanguage(event.target.value)}
                placeholder="python"
                aria-label="Language"
              />
            </label>
          </div>

          <div className="flex flex-wrap items-center gap-3">
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
                className="rounded-md border border-[var(--border)] px-3 py-1.5 text-sm text-[var(--muted)]"
                onClick={clearFilters}
              >
                Clear filters
              </button>
            )}
            <label className="flex items-center gap-2 text-sm text-[var(--muted)]">
              <input
                type="checkbox"
                checked={applyRerank}
                onChange={(event) => setApplyRerank(event.target.checked)}
                aria-label="Apply rerank"
              />
              Rerank
            </label>
            <label className="flex items-center gap-2 text-sm text-[var(--muted)]">
              <input
                type="checkbox"
                checked={expand}
                onChange={(event) => setExpand(event.target.checked)}
                aria-label="Expand context"
              />
              Expand context
            </label>
            <button
              type="submit"
              disabled={
                !selectedId || !question.trim() || askMutation.isPending || budgetBlocked
              }
              className="ml-auto rounded-md border border-[var(--accent)] bg-[color-mix(in_srgb,var(--accent)_25%,transparent)] px-4 py-1.5 text-sm font-medium disabled:opacity-50"
            >
              {askMutation.isPending ? "Asking…" : budgetBlocked ? "Budget exhausted" : "Ask"}
            </button>
          </div>
        </form>

        {selectedRepo && (
          <p className="mt-3 text-xs text-[var(--muted)]">
            Asking against latest ready snapshot for {selectedRepo.owner_name}/
            {selectedRepo.name}
            {result?.snapshot_id
              ? ` · snapshot ${result.snapshot_id.slice(0, 8)}…`
              : " · import a repo and wait for indexing before asking"}
          </p>
        )}
      </section>

      <section className="overflow-hidden rounded-xl border border-[var(--border)] bg-[var(--panel)]">
        {!hasRepos && !reposQuery.isLoading ? (
          <p className="p-6 text-sm text-[var(--muted)]">
            Nothing to ask yet. Import a repository, wait until Ready, then ask grounded questions
            here — or use{" "}
            <Link className="text-[var(--accent)] underline" to="/search">
              Search
            </Link>{" "}
            for free deterministic lookup.
          </p>
        ) : reposQuery.isLoading ? (
          <p className="p-6 text-sm text-[var(--muted)]">Loading repositories…</p>
        ) : reposQuery.isError ? (
          <p className="p-6 text-sm text-rose-300">{(reposQuery.error as Error).message}</p>
        ) : askMutation.isPending ? (
          <p className="p-6 text-sm text-[var(--muted)]">Retrieving evidence and drafting answer…</p>
        ) : askMutation.isError ? (
          <p className="p-6 text-sm text-rose-300">{(askMutation.error as Error).message}</p>
        ) : !result ? (
          <p className="p-6 text-sm text-[var(--muted)]">
            Enter a question and press Ask. Answers cite only retrieved evidence; invented
            citations are stripped. Prefer Search when you only need a cheap identifier lookup.
          </p>
        ) : (
          <div className="space-y-4 p-4">
            <div className="flex flex-wrap items-center gap-2">
              <span className="rounded-md border border-[var(--border)] px-2 py-0.5 text-xs">
                {askStatusLabel(result.status)}
              </span>
              {result.cached && (
                <span className="rounded bg-amber-500/15 px-2 py-0.5 text-xs text-amber-100">
                  cached
                </span>
              )}
              {result.model_provenance && (
                <span className="text-xs text-[var(--muted)]">
                  {String(result.model_provenance.provider ?? "unknown")}
                  {result.model_provenance.mode
                    ? ` · ${String(result.model_provenance.mode)}`
                    : ""}
                </span>
              )}
              <span className="text-xs text-[var(--muted)]">
                depth {result.context_depth} · context tokens {result.context_tokens_used}/
                {result.context_token_budget}
              </span>
            </div>

            {result.status === "budget_exceeded" && (
              <p className="rounded-md border border-rose-500/30 bg-rose-500/10 px-3 py-2 text-sm text-rose-100">
                This repository&apos;s Ask budget is exhausted. Use Search, or raise
                ASK_MAX_REQUESTS_PER_REPOSITORY locally.
              </p>
            )}

            <div>
              <h2 className="mb-2 text-sm font-medium">Answer</h2>
              <pre className="max-h-80 overflow-auto rounded-md border border-[var(--border)] bg-[color-mix(in_srgb,var(--bg)_75%,black)] p-3 font-mono text-xs whitespace-pre-wrap">
                {result.answer}
              </pre>
            </div>

            <div>
              <h2 className="mb-2 text-sm font-medium">
                Validated citations ({result.citations.length})
              </h2>
              {result.citations.length === 0 ? (
                <p className="text-sm text-[var(--muted)]">No validated citations.</p>
              ) : (
                <ul className="divide-y divide-[var(--border)]/70 rounded-md border border-[var(--border)]">
                  {result.citations.map((cite) => (
                    <li
                      key={`${cite.path}:${cite.start_line}-${cite.end_line}`}
                      className="flex flex-wrap items-center gap-2 px-3 py-2 text-sm"
                    >
                      <code className="font-mono text-xs text-[var(--accent)]">
                        {askCitationLabel(cite)}
                      </code>
                      <span className="rounded bg-emerald-500/15 px-2 py-0.5 text-xs text-emerald-200">
                        validated
                      </span>
                    </li>
                  ))}
                </ul>
              )}
              {!result.validation.ok && (
                <p className="mt-2 text-xs text-amber-200">
                  Validation dropped {result.validation.dropped_count} citation(s).
                  {result.validation.errors.length
                    ? ` ${result.validation.errors.slice(0, 3).join("; ")}`
                    : ""}
                </p>
              )}
            </div>

            {result.analysis && (
              <div>
                <h2 className="mb-2 text-sm font-medium">Query analysis</h2>
                <p className="text-xs text-[var(--muted)]">
                  kind={result.analysis.kind}
                  {result.analysis.rewrite_applied ? " · rewrite applied" : " · no rewrite"}
                </p>
                {result.analysis.retrieval_queries.length > 0 && (
                  <ul className="mt-1 list-inside list-disc text-xs text-[var(--muted)]">
                    {result.analysis.retrieval_queries.map((q) => (
                      <li key={q}>
                        <code>{q}</code>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            )}

            <div>
              <h2 className="mb-2 text-sm font-medium">
                Evidence used ({result.evidence.length})
              </h2>
              {result.evidence.length === 0 ? (
                <p className="text-sm text-[var(--muted)]">No evidence units.</p>
              ) : (
                <ul className="divide-y divide-[var(--border)]/70 rounded-md border border-[var(--border)]">
                  {result.evidence.map((item) => (
                    <li key={item.chunk_id} className="px-3 py-2">
                      <div className="flex flex-wrap items-center gap-2">
                        <code className="font-mono text-xs text-[var(--accent)]">
                          {item.citation}
                        </code>
                        <span className="rounded bg-zinc-500/20 px-2 py-0.5 text-xs text-zinc-300">
                          {item.role}
                        </span>
                        <span
                          className={[
                            "rounded px-2 py-0.5 text-xs",
                            item.support_level === "deep"
                              ? "bg-emerald-500/15 text-emerald-200"
                              : item.support_level === "generic"
                                ? "bg-sky-500/15 text-sky-200"
                                : "bg-zinc-500/20 text-zinc-300",
                          ].join(" ")}
                        >
                          {supportLevelLabel(item.support_level as SupportLevel)}
                        </span>
                        <span className="text-xs text-[var(--muted)]">depth {item.depth}</span>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        )}
      </section>

      <p className="text-xs text-[var(--muted)]">
        Honesty: Ask is opt-in and budgeted per repository. Default CI mode uses a deterministic
        mock answer over retrieved evidence. Live Azure chat is used only when configured and mock
        is off. Citations that are not in retrieved evidence are dropped. Prefer Search for cheap
        deterministic lookup; Ask for grounded NL answers.
      </p>
    </div>
  );
}
