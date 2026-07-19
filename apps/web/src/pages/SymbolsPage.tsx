import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { PageShell } from "../components/PageShell";
import {
  fetchRepositories,
  fetchSymbolCallees,
  fetchSymbolCallers,
  fetchRepositorySymbols,
} from "../lib/api";
import { confidenceLabel } from "../lib/calls";
import {
  frameworkRoleLabel,
  symbolKindLabel,
  type FrameworkRole,
  type SymbolItem,
  type SymbolKind,
} from "../lib/symbols";

type ViewPreset = "all" | "functions" | "classes" | "routes" | "models";

const PRESETS: Array<{ id: ViewPreset; label: string }> = [
  { id: "all", label: "All" },
  { id: "functions", label: "Functions" },
  { id: "classes", label: "Classes" },
  { id: "routes", label: "Routes" },
  { id: "models", label: "Models" },
];

const KIND_FILTERS: Array<{ id: "all" | SymbolKind; label: string }> = [
  { id: "all", label: "All kinds" },
  { id: "class", label: "Classes" },
  { id: "function", label: "Functions" },
  { id: "method", label: "Methods" },
  { id: "interface", label: "Interfaces" },
  { id: "type_alias", label: "Type aliases" },
  { id: "package", label: "Packages" },
  { id: "enum", label: "Enums" },
  { id: "record", label: "Records" },
  { id: "field", label: "Fields" },
  { id: "constructor", label: "Constructors" },
  { id: "import", label: "Imports" },
  { id: "export", label: "Exports" },
];

const ROLE_FILTERS: Array<{ id: "all" | FrameworkRole; label: string }> = [
  { id: "all", label: "Any role" },
  { id: "fastapi_route", label: "FastAPI" },
  { id: "flask_route", label: "Flask" },
  { id: "django_view", label: "Django" },
  { id: "sqlalchemy_model", label: "SQLAlchemy" },
  { id: "pydantic_model", label: "Pydantic" },
  { id: "celery_task", label: "Celery" },
  { id: "react_component", label: "React" },
  { id: "express_route", label: "Express" },
  { id: "nestjs_controller", label: "Nest controller" },
  { id: "nestjs_service", label: "Nest service" },
  { id: "nestjs_route", label: "Nest route" },
  { id: "nextjs_page", label: "Next page" },
  { id: "nextjs_route", label: "Next route" },
  { id: "spring_rest_controller", label: "Spring REST" },
  { id: "spring_controller", label: "Spring controller" },
  { id: "spring_service", label: "Spring service" },
  { id: "spring_repository", label: "Spring repository" },
  { id: "spring_entity", label: "Spring entity" },
  { id: "spring_route", label: "Spring route" },
  { id: "spring_interface", label: "Spring interface" },
  { id: "spring_implementation", label: "Spring implementation" },
];

function presetParams(preset: ViewPreset): {
  kind?: SymbolKind;
  framework_role?: FrameworkRole;
} {
  switch (preset) {
    case "functions":
      return { kind: "function" };
    case "classes":
      return { kind: "class" };
    case "routes":
      return { framework_role: "fastapi_route" };
    case "models":
      return { framework_role: "pydantic_model" };
    default:
      return {};
  }
}

export function SymbolsPage() {
  const [repositoryId, setRepositoryId] = useState<string>("");
  const [preset, setPreset] = useState<ViewPreset>("all");
  const [kind, setKind] = useState<"all" | SymbolKind>("all");
  const [role, setRole] = useState<"all" | FrameworkRole>("all");
  const [localOnly, setLocalOnly] = useState(false);
  const [nameContains, setNameContains] = useState("");
  const [pathPrefix, setPathPrefix] = useState("");
  const [selected, setSelected] = useState<SymbolItem | null>(null);

  const reposQuery = useQuery({
    queryKey: ["repositories"],
    queryFn: () => fetchRepositories(50),
  });

  const selectedId = repositoryId || reposQuery.data?.[0]?.id || "";
  const fromPreset = presetParams(preset);
  const effectiveKind = fromPreset.kind ?? (kind === "all" ? undefined : kind);
  const effectiveRole =
    fromPreset.framework_role ?? (role === "all" ? undefined : role);

  const symbolsQuery = useQuery({
    queryKey: [
      "repository-symbols",
      selectedId,
      preset,
      kind,
      role,
      localOnly,
      nameContains,
      pathPrefix,
    ],
    queryFn: () =>
      fetchRepositorySymbols(selectedId, {
        kind: effectiveKind,
        framework_role: effectiveRole,
        is_local_import: localOnly ? true : undefined,
        name_contains: nameContains.trim() || undefined,
        path_prefix: pathPrefix.trim() || undefined,
        limit: 200,
        offset: 0,
      }),
    enabled: Boolean(selectedId),
  });

  const callersQuery = useQuery({
    queryKey: ["symbol-callers", selectedId, selected?.id],
    queryFn: () => fetchSymbolCallers(selectedId, selected!.id),
    enabled: Boolean(selectedId && selected?.id),
  });

  const calleesQuery = useQuery({
    queryKey: ["symbol-callees", selectedId, selected?.id],
    queryFn: () => fetchSymbolCallees(selectedId, selected!.id),
    enabled: Boolean(selectedId && selected?.id),
  });

  const selectedRepo = useMemo(
    () => reposQuery.data?.find((repo) => repo.id === selectedId),
    [reposQuery.data, selectedId],
  );

  // For routes/models presets that only hit one role, also merge sibling roles client-side
  // when user wants broader "Routes" / "Models" — fetch FastAPI only for routes is ok for Day 7;
  // models: also allow SQLAlchemy via role filter buttons.

  return (
    <div className="space-y-4">
      <PageShell
        title="Symbols"
        description="Verify Python deep analysis: browse functions, classes, routes, and models, then inspect callers and callees for a selected symbol. Resolution confidence is heuristic."
      />

      <section className="rounded-xl border border-[var(--border)] bg-[var(--panel)] p-6">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-end">
          <label className="flex min-w-0 flex-1 flex-col gap-1 text-sm">
            <span className="text-[var(--muted)]">Repository</span>
            <select
              className="rounded-md border border-[var(--border)] bg-[color-mix(in_srgb,var(--bg)_70%,black)] px-3 py-2 outline-none ring-[var(--accent)] focus:ring-2"
              value={selectedId}
              onChange={(event) => {
                setRepositoryId(event.target.value);
                setSelected(null);
              }}
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

          <label className="flex min-w-0 flex-1 flex-col gap-1 text-sm">
            <span className="text-[var(--muted)]">Name contains</span>
            <input
              className="rounded-md border border-[var(--border)] bg-[color-mix(in_srgb,var(--bg)_70%,black)] px-3 py-2 outline-none ring-[var(--accent)] focus:ring-2"
              value={nameContains}
              onChange={(event) => setNameContains(event.target.value)}
              placeholder="load_"
              aria-label="Name contains"
            />
          </label>

          <label className="flex min-w-0 flex-1 flex-col gap-1 text-sm">
            <span className="text-[var(--muted)]">Path prefix</span>
            <input
              className="rounded-md border border-[var(--border)] bg-[color-mix(in_srgb,var(--bg)_70%,black)] px-3 py-2 outline-none ring-[var(--accent)] focus:ring-2"
              value={pathPrefix}
              onChange={(event) => setPathPrefix(event.target.value)}
              placeholder="scripts/"
              aria-label="Path prefix"
            />
          </label>

          <label className="flex items-center gap-2 text-sm text-[var(--muted)]">
            <input
              type="checkbox"
              checked={localOnly}
              onChange={(event) => setLocalOnly(event.target.checked)}
            />
            Local imports only
          </label>
        </div>

        <div className="mt-4 flex flex-wrap gap-2">
          {PRESETS.map((item) => (
            <button
              key={item.id}
              type="button"
              className={[
                "rounded-md border px-3 py-1.5 text-sm",
                preset === item.id
                  ? "border-[var(--accent)] bg-[color-mix(in_srgb,var(--accent)_20%,transparent)]"
                  : "border-[var(--border)]",
              ].join(" ")}
              onClick={() => {
                setPreset(item.id);
                setSelected(null);
                if (item.id !== "all") {
                  setKind("all");
                  setRole("all");
                }
              }}
            >
              {item.label}
            </button>
          ))}
        </div>

        {preset === "all" && (
          <>
            <div className="mt-3 flex flex-wrap gap-2">
              {KIND_FILTERS.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  className={[
                    "rounded-md border px-3 py-1.5 text-sm",
                    kind === item.id
                      ? "border-[var(--accent)] bg-[color-mix(in_srgb,var(--accent)_20%,transparent)]"
                      : "border-[var(--border)]",
                  ].join(" ")}
                  onClick={() => setKind(item.id)}
                >
                  {item.label}
                </button>
              ))}
            </div>
            <div className="mt-3 flex flex-wrap gap-2">
              {ROLE_FILTERS.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  className={[
                    "rounded-md border px-3 py-1.5 text-sm",
                    role === item.id
                      ? "border-[var(--accent)] bg-[color-mix(in_srgb,var(--accent)_20%,transparent)]"
                      : "border-[var(--border)]",
                  ].join(" ")}
                  onClick={() => setRole(item.id)}
                >
                  {item.label}
                </button>
              ))}
            </div>
          </>
        )}

        {selectedRepo && (
          <p className="mt-3 text-xs text-[var(--muted)]">
            Click a row to inspect callers and callees · {selectedRepo.owner_name}/
            {selectedRepo.name}
            {symbolsQuery.data?.snapshot_id
              ? ` · snapshot ${symbolsQuery.data.snapshot_id.slice(0, 8)}…`
              : " · no snapshot yet"}
          </p>
        )}
      </section>

      <section className="rounded-xl border border-[var(--border)] bg-[var(--panel)] p-6">
        {symbolsQuery.isLoading && <p className="text-sm text-[var(--muted)]">Loading symbols…</p>}
        {symbolsQuery.isError && (
          <p className="text-sm text-red-400">
            {symbolsQuery.error instanceof Error
              ? symbolsQuery.error.message
              : "Failed to load symbols"}
          </p>
        )}
        {symbolsQuery.data && (
          <>
            <p className="mb-3 text-sm text-[var(--muted)]">
              {symbolsQuery.data.total} symbol{symbolsQuery.data.total === 1 ? "" : "s"}
            </p>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[720px] text-left text-sm">
                <thead className="text-[var(--muted)]">
                  <tr className="border-b border-[var(--border)]">
                    <th className="py-2 pr-3 font-medium">Kind</th>
                    <th className="py-2 pr-3 font-medium">Qualified name</th>
                    <th className="py-2 pr-3 font-medium">Framework / import</th>
                    <th className="py-2 pr-3 font-medium">Path</th>
                    <th className="py-2 font-medium">Details</th>
                  </tr>
                </thead>
                <tbody>
                  {symbolsQuery.data.symbols.map((sym) => {
                    const active = selected?.id === sym.id;
                    return (
                      <tr
                        key={sym.id}
                        className={[
                          "cursor-pointer border-b border-[var(--border)]/60 align-top",
                          active
                            ? "bg-[color-mix(in_srgb,var(--accent)_12%,transparent)]"
                            : "hover:bg-[color-mix(in_srgb,var(--panel)_80%,black)]",
                        ].join(" ")}
                        onClick={() => setSelected(sym)}
                      >
                        <td className="py-2 pr-3">
                          {symbolKindLabel(sym.kind)}
                          {sym.is_async ? (
                            <span className="ml-1 text-xs text-[var(--muted)]">async</span>
                          ) : null}
                        </td>
                        <td className="py-2 pr-3 font-mono text-xs">{sym.qualified_name}</td>
                        <td className="py-2 pr-3 text-xs text-[var(--muted)]">
                          {sym.framework_role ? (
                            <div>
                              {frameworkRoleLabel(sym.framework_role)}
                              {sym.framework_detail ? ` · ${sym.framework_detail}` : ""}
                            </div>
                          ) : null}
                          {sym.kind === "import" && (
                            <div>
                              {sym.import_style ?? "import"}
                              {sym.is_local_import === true
                                ? " · local"
                                : sym.is_local_import === false
                                  ? " · external"
                                  : ""}
                            </div>
                          )}
                          {!sym.framework_role && sym.kind !== "import" ? "—" : null}
                        </td>
                        <td className="py-2 pr-3 font-mono text-xs">{sym.path}</td>
                        <td className="py-2 text-xs text-[var(--muted)]">
                          <div className="font-mono">{sym.signature ?? "—"}</div>
                          {sym.decorators.length > 0 && (
                            <div className="mt-1">@{sym.decorators.join(" @")}</div>
                          )}
                          {sym.docstring && (
                            <div className="mt-1 line-clamp-2 italic">{sym.docstring}</div>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
            {symbolsQuery.data.symbols.length === 0 && (
              <p className="mt-3 text-sm text-[var(--muted)]">
                No symbols yet. Import a Python repo and wait for the worker to finish parsing.
              </p>
            )}
          </>
        )}
      </section>

      {selected && (
        <section className="grid gap-4 lg:grid-cols-2">
          <div className="rounded-xl border border-[var(--border)] bg-[var(--panel)] p-6">
            <h2 className="text-sm font-medium">Callers → {selected.qualified_name}</h2>
            <p className="mt-1 text-xs text-[var(--muted)]">Incoming calls targeting this symbol</p>
            {callersQuery.isLoading && (
              <p className="mt-3 text-sm text-[var(--muted)]">Loading callers…</p>
            )}
            {callersQuery.data && (
              <ul className="mt-3 space-y-2 text-sm">
                {callersQuery.data.calls.length === 0 && (
                  <li className="text-[var(--muted)]">No callers recorded.</li>
                )}
                {callersQuery.data.calls.map((call) => (
                  <li key={call.id} className="font-mono text-xs">
                    <span className="text-[var(--muted)]">L{call.line}</span>{" "}
                    {call.caller_qualified_name ?? "?"} → {call.qualified_expression}{" "}
                    <span className="text-[var(--muted)]">
                      ({confidenceLabel(call.confidence)})
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </div>
          <div className="rounded-xl border border-[var(--border)] bg-[var(--panel)] p-6">
            <h2 className="text-sm font-medium">{selected.qualified_name} → Callees</h2>
            <p className="mt-1 text-xs text-[var(--muted)]">Outgoing calls from this symbol</p>
            {calleesQuery.isLoading && (
              <p className="mt-3 text-sm text-[var(--muted)]">Loading callees…</p>
            )}
            {calleesQuery.data && (
              <ul className="mt-3 space-y-2 text-sm">
                {calleesQuery.data.calls.length === 0 && (
                  <li className="text-[var(--muted)]">No callees recorded.</li>
                )}
                {calleesQuery.data.calls.map((call) => (
                  <li key={call.id} className="font-mono text-xs">
                    <span className="text-[var(--muted)]">L{call.line}</span>{" "}
                    {call.qualified_expression}
                    {call.candidate_qualified_name
                      ? ` → ${call.candidate_qualified_name}`
                      : ""}{" "}
                    <span className="text-[var(--muted)]">
                      ({confidenceLabel(call.confidence)})
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </section>
      )}
    </div>
  );
}
