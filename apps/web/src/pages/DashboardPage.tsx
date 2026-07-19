import { useQuery } from "@tanstack/react-query";
import { PageShell } from "../components/PageShell";

const apiBase = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function fetchHealth(): Promise<{ status: string }> {
  const response = await fetch(`${apiBase}/health`);
  if (!response.ok) {
    throw new Error(`Health check failed (${response.status})`);
  }
  return response.json() as Promise<{ status: string }>;
}

export function DashboardPage() {
  const health = useQuery({
    queryKey: ["health"],
    queryFn: fetchHealth,
    retry: false,
  });

  return (
    <div className="space-y-4">
      <PageShell
        title="Dashboard"
        description="Import repositories, watch indexing jobs, and jump into search, symbols, and citation-backed answers."
      />
      <div className="rounded-xl border border-[var(--border)] bg-[var(--panel)] p-6 text-sm">
        <p className="text-[var(--muted)]">API health</p>
        {health.isLoading && <p className="mt-2">Checking…</p>}
        {health.isError && (
          <p className="mt-2 text-amber-300">
            API unreachable at {apiBase}. Start the API locally to connect.
          </p>
        )}
        {health.data && (
          <p className="mt-2 text-emerald-300">Status: {health.data.status}</p>
        )}
      </div>
    </div>
  );
}
