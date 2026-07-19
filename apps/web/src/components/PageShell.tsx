type PageShellProps = {
  title: string;
  description: string;
};

export function PageShell({ title, description }: PageShellProps) {
  return (
    <section className="rounded-xl border border-[var(--border)] bg-[var(--panel)] p-6 shadow-sm">
      <h2 className="text-xl font-semibold tracking-tight">{title}</h2>
      <p className="mt-2 max-w-2xl text-sm text-[var(--muted)]">{description}</p>
    </section>
  );
}
