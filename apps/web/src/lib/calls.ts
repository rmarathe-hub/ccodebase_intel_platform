export interface SymbolCallItem {
  id: string;
  snapshot_id: string;
  source_file_id: string;
  path: string;
  caller_symbol_id: string | null;
  caller_qualified_name: string | null;
  raw_callee: string;
  qualified_expression: string;
  line: number;
  candidate_qualified_name: string | null;
  confidence: string;
  language: string;
  created_at: string;
}

export interface SymbolCallListResponse {
  repository_id: string;
  snapshot_id: string | null;
  total: number;
  limit: number;
  offset: number;
  calls: SymbolCallItem[];
}

export interface SymbolNeighborsResponse {
  repository_id: string;
  snapshot_id: string;
  symbol_id: string;
  symbol_qualified_name: string;
  direction: "callers" | "callees" | string;
  total: number;
  calls: SymbolCallItem[];
}

export function confidenceLabel(confidence: string): string {
  switch (confidence) {
    case "resolved":
      return "Resolved";
    case "ambiguous":
      return "Ambiguous";
    case "unresolved":
      return "Unresolved";
    default:
      return confidence;
  }
}
