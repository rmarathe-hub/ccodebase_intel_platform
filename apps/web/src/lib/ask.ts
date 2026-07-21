export type AskStatus =
  | "ok"
  | "partial"
  | "no_evidence"
  | "ask_disabled"
  | "error"
  | string;

export interface AskCitation {
  path: string;
  start_line: number;
  end_line: number;
  chunk_id: string | null;
  valid: boolean;
  reason: string;
  raw: string | null;
}

export interface AskEvidenceItem {
  chunk_id: string;
  path: string;
  start_line: number;
  end_line: number;
  support_level: string;
  role: string;
  depth: number;
  citation: string;
}

export interface AskAnalysisEcho {
  kind: string;
  rewrite_applied: boolean;
  retrieval_queries: string[];
  identifiers: string[];
  paths: string[];
}

export interface AskValidationEcho {
  ok: boolean;
  valid_count: number;
  dropped_count: number;
  errors: string[];
}

export interface AskRequestBody {
  question: string;
  language?: string;
  path_prefix?: string;
  support_level?: string;
  apply_rerank?: boolean;
  expand?: boolean;
}

export interface AskResponse {
  repository_id: string;
  snapshot_id: string | null;
  question: string;
  answer: string;
  status: AskStatus;
  citations: AskCitation[];
  evidence: AskEvidenceItem[];
  analysis: AskAnalysisEcho | null;
  validation: AskValidationEcho;
  context_depth: number;
  context_tokens_used: number;
  context_token_budget: number;
  ranked_chunk_ids: string[];
  model_provenance: Record<string, unknown> | null;
  cached: boolean;
  notes: string[];
}

export function askCitationLabel(cite: {
  path: string;
  start_line: number;
  end_line: number;
}): string {
  return `${cite.path}:${cite.start_line}-${cite.end_line}`;
}

export function askStatusLabel(status: string): string {
  switch (status) {
    case "ok":
      return "OK";
    case "partial":
      return "Partial (some citations dropped)";
    case "no_evidence":
      return "No evidence";
    case "ask_disabled":
      return "Ask disabled";
    case "error":
      return "Error";
    default:
      return status;
  }
}
