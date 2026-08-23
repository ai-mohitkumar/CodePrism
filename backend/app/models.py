from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class AnalyzeRequest(BaseModel):
    language: str = Field(default="python", description="Programming language: python, cpp, c, java, javascript")
    code: str = Field(..., description="Source code to analyze and execute")
    stdin: Optional[str] = Field(default="", description="Standard input for the program")
    run_empirical_benchmark: Optional[bool] = Field(default=True, description="Whether to benchmark multi-size inputs")

class ExecuteRequest(BaseModel):
    language: str = Field(default="python")
    code: str = Field(...)
    stdin: Optional[str] = Field(default="")
    timeout_sec: Optional[float] = Field(default=5.0)

class BenchmarkRequest(BaseModel):
    language: str = Field(default="python")
    code: str = Field(...)
    input_sizes: Optional[List[int]] = Field(default=[100, 500, 2000, 6000, 15000])

class BenchmarkPoint(BaseModel):
    size: int
    time_ms: float
    memory_mb: float

class BenchmarkResult(BaseModel):
    points: List[BenchmarkPoint] = []
    empirical_big_o: str = "O(n)"
    explanation: str = ""

class ComplexityResult(BaseModel):
    time_complexity: str = "O(1)"
    space_complexity: str = "O(1)"
    confidence: float = 0.9
    explanation: str = ""
    nested_depth: int = 0
    recursion_found: bool = False
    has_halving: bool = False
    details: List[str] = []

class LineAnalysisItem(BaseModel):
    line_number: int
    content: str
    classification: str
    complexity_impact: str
    status: str = "ok"  # ok, warning, error
    notes: str = ""

class SecurityIssue(BaseModel):
    severity: str  # Critical, High, Medium, Low
    line: Optional[int] = None
    title: str
    description: str
    suggestion: str

class QualityMetric(BaseModel):
    maintainability_score: float = 8.5
    readability_score: float = 9.0
    cyclomatic_complexity: int = 1
    total_lines: int = 0
    code_lines: int = 0
    comment_lines: int = 0
    potential_issues: List[str] = []

class ExecutionResult(BaseModel):
    status: str = "success"  # success, compilation_error, runtime_error, timeout
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    execution_time_sec: float = 0.0
    peak_memory_mb: float = 0.0
    error_line: Optional[int] = None
    error_column: Optional[int] = None
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    error_pointer: Optional[str] = None
    suggested_fix: Optional[str] = None

class AIInsight(BaseModel):
    line_by_line_summary: str = ""
    algorithmic_breakdown: str = ""
    optimization_suggestions: List[str] = []
    optimized_code: Optional[str] = None
    original_big_o: str = "O(n^2)"
    optimized_big_o: str = "O(n log n)"
    why_faster: str = ""

class AnalysisResponse(BaseModel):
    language: str
    execution: ExecutionResult
    complexity: ComplexityResult
    line_analysis: List[LineAnalysisItem]
    quality: QualityMetric
    security: List[SecurityIssue]
    benchmark: Optional[BenchmarkResult] = None
    ai_insights: Optional[AIInsight] = None

class OptimizeRequest(BaseModel):
    language: str
    code: str
    goal: Optional[str] = "Improve time and space complexity"

class OptimizeResponse(BaseModel):
    original_code: str
    optimized_code: str
    original_big_o: str
    optimized_big_o: str
    explanation: str
    diff_summary: List[str]
