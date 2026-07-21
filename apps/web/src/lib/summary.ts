export interface DeterministicSummary {
  language_mix: Record<string, number>;
  support_level_mix: Record<string, number>;
  important_directories: string[];
  test_directories: string[];
  documentation_directories: string[];
  build_systems: string[];
  configuration_files: string[];
  documentation_files: string[];
  entry_point_candidates: string[];
  chunk_counts: Record<string, unknown>;
  parser_coverage: Record<string, number>;
  skipped_file_counts: Record<string, number>;
  file_count: number;
}

export interface RepositorySummaryResponse {
  repository_id: string;
  snapshot_id: string | null;
  deterministic_summary: DeterministicSummary | null;
  llm_summary: Record<string, unknown> | null;
  llm_summary_status: string;
  evidence: Array<{ path: string; start_line: number; end_line: number }>;
  model_provenance: Record<string, unknown> | null;
}
