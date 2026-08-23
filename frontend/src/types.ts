export interface FunctionTiming {
  function_name: string;
  cumtime_ms: number;
  percall_ms: number;
  call_count: number;
}

export interface CompilerDiagnostic {
  severity: 'error' | 'warning' | 'note';
  line?: number | null;
  column?: number | null;
  message: string;
  pointer?: string | null;
  suggested_fix?: string | null;
}

export interface CompileResponse {
  success: boolean;
  compiler_name: string;
  target_artifact?: string | null;
  artifact_type: string;
  compilation_time_ms: number;
  errors_count: number;
  warnings_count: number;
  raw_output: string;
  diagnostics: CompilerDiagnostic[];
  ir_bytecode?: string | null;
}

export interface StandardCompileResult {
  success: boolean;
  compiler_output: string;
  errors: string[];
  warnings: string[];
  error_line?: number | null;
  error_column?: number | null;
  error_pointer?: string | null;
  suggested_fix?: string | null;
}

export interface StandardExecutionResult {
  exit_code: number;
  stdout: string;
  stderr: string;
  runtime_ms: number;
  memory_mb: number;
  cpu_percent: number;
  functions: FunctionTiming[];
  status: 'success' | 'compilation_error' | 'runtime_error' | 'timeout';
}

export interface StandardComplexityResult {
  time: string;
  space: string;
  confidence: number;
  reason: string;
  nested_depth: number;
  has_recursion: boolean;
  has_halving: boolean;
  details: string[];
}

export type ComplexityResponse = StandardComplexityResult;

export interface SecurityIssue {
  severity: 'Critical' | 'High' | 'Medium' | 'Low';
  line?: number | null;
  title: string;
  description: string;
  suggestion: string;
}

export interface StandardSecurityResult {
  critical: number;
  high: number;
  medium: number;
  low: number;
  issues: SecurityIssue[];
}

export interface StandardQualityResult {
  score: number;
  maintainability: number;
  readability: number;
  cyclomatic: number;
  total_lines: number;
  code_lines: number;
  comment_lines: number;
  issues: string[];
}

export interface ASTNode {
  id: string;
  name: string;
  type: string;
  lineno?: number | null;
  col_offset?: number | null;
  details?: string | null;
  children: ASTNode[];
}

export interface ASTResponse {
  root?: ASTNode | null;
  summary: string[];
}

export interface UniversalResult {
  language: string;
  version: string;
  status: 'success' | 'compilation_error' | 'runtime_error' | 'timeout';
  filename?: string | null;
  compile: StandardCompileResult;
  execution: StandardExecutionResult;
  ast?: ASTResponse | null;
  complexity: StandardComplexityResult;
  quality: StandardQualityResult;
  security: StandardSecurityResult;
}

export interface ErrorDiagnosis {
  has_error: boolean;
  error_type?: string | null;
  line?: number | null;
  column?: number | null;
  message?: string | null;
  pointer?: string | null;
  suggested_fix?: string | null;
}

export interface DebugStepResponse {
  current_line: number;
  is_terminated: boolean;
  stdout: string;
  variables: Record<string, any>;
  call_stack: string[];
  output: string;
}

export interface AIResponse {
  title: string;
  content: string;
  code_snippet?: string | null;
  original_big_o?: string | null;
  optimized_big_o?: string | null;
  bullet_points: string[];
}

export interface LanguageMeta {
  id: string;
  name: string;
  tier: string;
  family: string;
  extension: string;
  icon: string;
  is_installed: boolean;
  version: string;
  capabilities: string[];
}

export interface FileStats {
  loc: number;
  functions_count: number;
  classes_count: number;
  loops_count: number;
}

export interface FileUploadResponse {
  filename: string;
  language: string;
  code: string;
  stats: FileStats;
  result: UniversalResult;
}

export interface ProjectFileSummary {
  path: string;
  filename: string;
  language: string;
  loc: number;
  time_complexity: string;
  security_issues_count: number;
  maintainability_score: number;
  code_snippet: string;
}

export interface DependencyEdge {
  source: string;
  target: string;
  import_statement: string;
}

export interface ProjectReportResponse {
  project_name: string;
  files_analyzed_count: number;
  languages_distribution: Record<string, number>;
  total_loc: number;
  total_functions: number;
  total_classes: number;
  highest_complexity: string;
  average_complexity: string;
  overall_quality_score: number;
  security_summary: Record<string, number>;
  optimization_opportunities: string[];
  files: ProjectFileSummary[];
  dependency_graph: DependencyEdge[];
}

// Cloud Projects & Device Sync
export interface ProjectFileItem {
  name: string;
  language: string;
  content: string;
}

export interface ProjectMetadata {
  id: string;
  title: string;
  description: string;
  language: string;
  files_count: number;
  updated_at: number;
  created_at: number;
  versions_count?: number;
}

export interface ProjectDetails {
  id: string;
  title: string;
  description: string;
  language: string;
  files: ProjectFileItem[];
  updated_at: number;
  created_at: number;
  versions_count?: number;
}

export interface ProjectVersion {
  id: string;
  project_id: string;
  version_tag: string;
  summary: string;
  files_count: number;
  total_loc: number;
  created_at: number;
  files: ProjectFileItem[];
}

export interface ProjectTemplate {
  id: string;
  title: string;
  description: string;
  language: string;
  difficulty: string;
  category: string;
  files: Array<{ name: string; language: string; content: string }>;
}

export interface ShareProjectResponse {
  share_token: string;
  share_url: string;
  project_title: string;
  language: string;
  created_at: number;
}
