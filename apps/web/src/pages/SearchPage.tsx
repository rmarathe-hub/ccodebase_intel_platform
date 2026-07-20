import { PageShell } from "../components/PageShell";

export function SearchPage() {
  return (
    <PageShell
      title="Search"
      description="Exact chunk search is available via the API (search_mode=exact). Hybrid, semantic, and LLM reranking layers are reserved for later retrieval work."
    />
  );
}
