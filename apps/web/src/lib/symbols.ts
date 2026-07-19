export type SymbolKind = "class" | "function" | "method" | "import";

export interface SymbolParameter {
  name: string;
  annotation: string | null;
  kind: string;
}

export interface SymbolItem {
  id: string;
  snapshot_id: string;
  source_file_id: string;
  path: string;
  kind: SymbolKind | string;
  name: string;
  qualified_name: string;
  language: string;
  start_line: number;
  end_line: number;
  signature: string | null;
  docstring: string | null;
  decorators: string[];
  parameters: SymbolParameter[];
  return_annotation: string | null;
  is_async: boolean;
  created_at: string;
}

export interface SymbolListResponse {
  repository_id: string;
  snapshot_id: string | null;
  total: number;
  limit: number;
  offset: number;
  symbols: SymbolItem[];
}

export function symbolKindLabel(kind: string): string {
  switch (kind) {
    case "class":
      return "Class";
    case "function":
      return "Function";
    case "method":
      return "Method";
    case "import":
      return "Import";
    default:
      return kind;
  }
}
