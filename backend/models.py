from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

class LanguageTier(str, Enum):
    TIER_A = "Tier A (Essential)"
    TIER_B = "Tier B (Popular & Academic)"
    SPECIAL_PURPOSE = "Special Purpose"

class LanguageFamily(str, Enum):
    NATIVE = "Native Compiled"
    MANAGED_VM = "Managed VM"
    SCRIPT_JIT = "Scripted / JIT"
    SPECIAL_PURPOSE = "Special Purpose"

# Compiler Models
class CompileRequest(BaseModel):
    language: str = Field(default="cpp", description="Language identifier")
    code: str = Field(..., description="Source code")
    compiler_flags: Optional[List[str]] = Field(default=[], description="Optional compiler flags (e.g. -O2, -Wall)")
    filename: Optional[str] = Field(default=None, description="Source filename")

class CompilerDiagnostic(BaseModel):
    severity: str  # error, warning, note
    line: Optional[int] = None
    column: Optional[int] = None
    message: str
    pointer: Optional[str] = None
    suggested_fix: Optional[str] = None

class CompileResponse(BaseModel):
    success: bool
    compiler_name: str
    target_artifact: Optional[str] = None
    artifact_type: str  # Native Binary, JVM Bytecode, Python Bytecode, JS Bundle, AST
    compilation_time_ms: float = 0.0
    errors_count: int = 0
    warnings_count: int = 0
    raw_output: str = ""
    diagnostics: List[CompilerDiagnostic] = []
    ir_bytecode: Optional[str] = None

# Universal Execution and Analysis Models
class FunctionTiming(BaseModel):
    function_name: str
    cumtime_ms: float
    percall_ms: float
    call_count: int

class StandardCompileResult(BaseModel):
    success: bool = True
    compiler_output: str = ""
    errors: List[str] = []
    warnings: List[str] = []
    error_line: Optional[int] = None
    error_column: Optional[int] = None
    error_pointer: Optional[str] = None
    suggested_fix: Optional[str] = None

class StandardExecutionResult(BaseModel):
    exit_code: int = 0
    stdout: str = ""
    stderr: str = ""
    runtime_ms: float = 0.0
    memory_mb: float = 0.0
    cpu_percent: float = 0.0
    functions: List[FunctionTiming] = []
    status: str = "success"  # success, compilation_error, runtime_error, timeout

class ExecuteResponse(BaseModel):
    success: bool = True
    status: str = "success"
    output: str = ""
    stderr: str = ""
    exit_code: int = 0
    runtime_ms: float = 0.0
    memory_mb: float = 0.0
    cpu_percent: float = 0.0
    functions: List[FunctionTiming] = []
    error_line: Optional[int] = None
    error_column: Optional[int] = None
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    error_pointer: Optional[str] = None
    suggested_fix: Optional[str] = None

class StandardComplexityResult(BaseModel):
    time: str = "O(1)"
    space: str = "O(1)"
    confidence: float = 0.95
    reason: str = ""
    nested_depth: int = 0
    has_recursion: bool = False
    has_halving: bool = False
    details: List[str] = []

class ComplexityResponse(BaseModel):
    time_complexity: str = "O(1)"
    space_complexity: str = "O(1)"
    confidence: float = 0.95
    reason: str = ""
    nested_depth: int = 0
    has_recursion: bool = False
    has_halving: bool = False
    details: List[str] = []

class StandardQualityResult(BaseModel):
    score: float = 85.0
    maintainability: float = 8.5
    readability: float = 9.0
    cyclomatic: int = 1
    total_lines: int = 0
    code_lines: int = 0
    comment_lines: int = 0
    issues: List[str] = []

class QualityResponse(BaseModel):
    maintainability_score: float = 8.5
    readability_score: float = 9.0
    cyclomatic_complexity: int = 1
    total_lines: int = 0
    code_lines: int = 0
    comment_lines: int = 0
    issues: List[str] = []

class SecurityIssue(BaseModel):
    severity: str  # Critical, High, Medium, Low
    line: Optional[int] = None
    title: str
    description: str
    suggestion: str

class StandardSecurityResult(BaseModel):
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    issues: List[SecurityIssue] = []

class ASTNode(BaseModel):
    id: str
    name: str
    type: str
    lineno: Optional[int] = None
    col_offset: Optional[int] = None
    details: Optional[str] = None
    children: List['ASTNode'] = []

ASTNode.model_rebuild()

class ASTResponse(BaseModel):
    root: Optional[ASTNode] = None
    summary: List[str] = []

# Universal Unified Result Format
class UniversalResult(BaseModel):
    language: str
    version: str
    status: str  # success, compilation_error, runtime_error, timeout
    filename: Optional[str] = None
    compile: StandardCompileResult
    execution: StandardExecutionResult
    ast: Optional[ASTResponse] = None
    complexity: StandardComplexityResult
    quality: StandardQualityResult
    security: StandardSecurityResult

# Request payloads
class ExecuteRequest(BaseModel):
    language: str = Field(default="python", description="Language ID")
    code: str = Field(..., description="Source code")
    stdin: Optional[str] = Field(default="", description="Input stream")
    filename: Optional[str] = Field(default=None, description="Optional filename")
    timeout_sec: Optional[float] = Field(default=5.0)

class AnalyzeErrorRequest(BaseModel):
    language: str = "python"
    code: str
    filename: Optional[str] = None

class ErrorDiagnosis(BaseModel):
    has_error: bool
    error_type: Optional[str] = None
    line: Optional[int] = None
    column: Optional[int] = None
    message: Optional[str] = None
    pointer: Optional[str] = None
    suggested_fix: Optional[str] = None

class DebugStepRequest(BaseModel):
    language: str = "python"
    code: str
    line_number: int = 1
    breakpoints: List[int] = []
    variables: Dict[str, Any] = {}

class DebugStepResponse(BaseModel):
    current_line: int
    is_terminated: bool
    stdout: str
    variables: Dict[str, Any]
    call_stack: List[str]
    output: str

class AIRequest(BaseModel):
    language: str = "python"
    code: str
    prompt_type: str = "explain"
    user_query: Optional[str] = ""

class AIResponse(BaseModel):
    title: str
    content: str
    code_snippet: Optional[str] = None
    original_big_o: Optional[str] = None
    optimized_big_o: Optional[str] = None
    bullet_points: List[str] = []

# Job Queue Models
class JobStatus(str, Enum):
    QUEUED = "queued"
    STARTING = "starting"
    COMPILING = "compiling"
    RUNNING = "running"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"

class JobSubmissionResponse(BaseModel):
    job_id: str
    status: JobStatus
    created_at: float
    message: str

class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    progress: int
    created_at: float
    updated_at: float
    result: Optional[UniversalResult] = None
    error: Optional[str] = None

# Cloud Project & Versioning Models
class ProjectFileVersion(BaseModel):
    name: str
    language: str
    content: str

class ProjectVersion(BaseModel):
    id: str
    project_id: str
    version_tag: str
    summary: str
    files: List[ProjectFileVersion]
    total_loc: int
    created_at: float

class CreateSnapshotRequest(BaseModel):
    version_tag: str = Field(default="Snapshot", description="Tag name (e.g. v1.0, Before Refactor)")
    summary: Optional[str] = ""

class ShareProjectResponse(BaseModel):
    share_token: str
    share_url: str
    project_title: str
    language: str
    created_at: float

class ProjectTemplate(BaseModel):
    id: str
    title: str
    description: str
    language: str
    difficulty: str
    category: str
    files: List[Dict[str, str]]

# Upload and Project Models
class FileStats(BaseModel):
    loc: int = 0
    functions_count: int = 0
    classes_count: int = 0
    loops_count: int = 0

class FileUploadResponse(BaseModel):
    filename: str
    language: str
    code: str
    stats: FileStats
    result: UniversalResult

class ProjectFileSummary(BaseModel):
    path: str
    filename: str
    language: str
    loc: int
    time_complexity: str
    security_issues_count: int
    maintainability_score: float
    code_snippet: str

class DependencyEdge(BaseModel):
    source: str
    target: str
    import_statement: str

class ProjectReportResponse(BaseModel):
    project_name: str
    files_analyzed_count: int
    languages_distribution: Dict[str, int]
    total_loc: int
    total_functions: int
    total_classes: int
    highest_complexity: str
    average_complexity: str
    overall_quality_score: float
    security_summary: Dict[str, int]
    optimization_opportunities: List[str]
    files: List[ProjectFileSummary]
    dependency_graph: List[DependencyEdge]

class GitHubRepoRequest(BaseModel):
    repo_url: str = Field(..., description="Public GitHub repository URL")
    branch: Optional[str] = "main"

class LanguageMetadata(BaseModel):
    id: str
    name: str
    tier: LanguageTier
    family: LanguageFamily
    extension: str
    icon: str
    is_installed: bool
    version: str
    capabilities: List[str]
