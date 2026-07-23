export type SupportLevel = "deep" | "generic" | "skip";

export interface RepositoryListItem {
  id: string;
  host: string;
  owner_name: string;
  name: string;
  default_branch: string;
  clone_url: string;
  created_at: string;
}

export interface SourceFile {
  id: string;
  snapshot_id: string;
  path: string;
  size_bytes: number;
  line_count: number | null;
  content_hash: string | null;
  language: string | null;
  support_level: SupportLevel | string;
  parser_name: string | null;
  parser_version: string | null;
  skip_reason: string | null;
  is_test_file: boolean;
  is_generated: boolean;
  is_vendor: boolean;
  is_binary: boolean;
  created_at: string;
}

export interface SourceFileListResponse {
  repository_id: string;
  snapshot_id: string | null;
  total: number;
  limit: number;
  offset: number;
  files: SourceFile[];
}

export interface SourceFileContentChunk {
  chunk_id: string;
  start_line: number;
  end_line: number;
  content: string;
  support_level: string;
  symbol_id: string | null;
}

export interface SourceFileContentResponse {
  repository_id: string;
  snapshot_id: string | null;
  path: string;
  indexed: boolean;
  language: string | null;
  support_level: string | null;
  line_count: number | null;
  content: string;
  chunks: SourceFileContentChunk[];
  coverage_complete: boolean;
  missing_ranges: number[][];
  message: string | null;
}

export function supportLevelLabel(level: string): string {
  switch (level) {
    case "deep":
      return "Deep";
    case "generic":
      return "Generic";
    case "skip":
      return "Skip";
    default:
      return level;
  }
}
