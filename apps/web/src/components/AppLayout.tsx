import { NavLink, Outlet } from "react-router-dom";

const links: Array<{ to: string; label: string; end?: boolean }> = [
  { to: "/", label: "Dashboard", end: true },
  { to: "/repositories", label: "Repositories" },
  { to: "/search", label: "Search" },
  { to: "/ask", label: "Ask" },
  { to: "/symbols", label: "Symbols" },
  { to: "/graph", label: "Graph" },
  { to: "/files", label: "Files" },
  { to: "/jobs", label: "Jobs" },
];

export function AppLayout() {
  return (
    <div className="min-h-screen">
      <header className="border-b border-[var(--border)] bg-[color-mix(in_srgb,var(--panel)_88%,transparent)] backdrop-blur">
        <div className="mx-auto flex max-w-6xl flex-col gap-4 px-6 py-5">
          <div>
            <p className="text-xs tracking-[0.2em] text-[var(--muted)] uppercase">
              Codebase Intelligence
            </p>
            <h1 className="mt-1 text-2xl font-semibold tracking-tight">Platform</h1>
          </div>
          <nav className="flex flex-wrap gap-2">
            {links.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                end={link.end ?? false}
                className={({ isActive }) =>
                  [
                    "rounded-md px-3 py-1.5 text-sm transition",
                    isActive
                      ? "bg-[var(--accent)] text-white"
                      : "bg-[var(--panel)] text-[var(--muted)] hover:text-[var(--text)]",
                  ].join(" ")
                }
              >
                {link.label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-6 py-8">
        <Outlet />
      </main>
    </div>
  );
}
