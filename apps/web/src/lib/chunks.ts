export type SearchMode = "exact" | "semantic" | "hybrid" | "rrf" | "rerank";

export interface ChunkSearchHit {
  id: string;
  path: string;
  language: string | null;
  support_level: string;
  chunk_type: string;
  start_line: number;
  end_line: number;
  content: string;
  content_hash: string;
  extraction_method: string;
  parser_name: string;
  parser_version: string;
  verified_deep: boolean;
  llm_enriched: boolean;
  validation_status: string | null;
  semantic_label: string | null;
  concise_summary: string | null;
  parent_context: string | null;
  created_at: string;
  score: number | null;
  score_breakdown: Record<string, number> | null;
}

export interface ChunkSearchResponse {
  repository_id: string;
  snapshot_id: string | null;
  query: string;
  total: number;
  limit: number;
  offset: number;
  search_mode: SearchMode | string;
  hits: ChunkSearchHit[];
}

export interface ChunkSearchParams {
  q: string;
  search_mode?: SearchMode;
  language?: string;
  path_prefix?: string;
  support_level?: string;
  limit?: number;
  offset?: number;
}

export function searchModeLabel(mode: string): string {
  switch (mode) {
    case "exact":
      return "Exact";
    case "semantic":
      return "Semantic";
    case "hybrid":
      return "Hybrid";
    case "rrf":
      return "RRF";
    case "rerank":
      return "Rerank";
    default:
      return mode;
  }
}

export function citationLabel(hit: ChunkSearchHit): string {
  return `${hit.path}:${hit.start_line}-${hit.end_line}`;
}
