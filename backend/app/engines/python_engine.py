import sys
import tempfile
import os
from typing import List, Optional, Dict, Any
from app.engines.base import BaseLanguageEngine
from app.models import ExecutionResult, ComplexityResult, LineAnalysisItem, SecurityIssue, QualityMetric
from app.analyzers.complexity import ComplexityAnalyzer
from app.analyzers.line_analyzer import LineAnalyzer
from app.analyzers.security import SecurityScanner
from app.analyzers.quality import QualityAuditor
from app.profiler.executor import CodeExecutor

class PythonLanguageEngine(BaseLanguageEngine):
    @property
    def language_id(self) -> str:
        return "python"

    def execute(self, code: str, stdin: str = "", timeout_sec: float = 5.0) -> ExecutionResult:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(code)
            temp_path = f.name

        try:
            exit_code, stdout, stderr, elapsed_time, peak_ram = CodeExecutor.execute_command(
                [sys.executable, temp_path],
                stdin_text=stdin,
                timeout_sec=timeout_sec
            )

            status = "success"
            error_details: Dict[str, Any] = {}

            if exit_code != 0 or stderr:
                if "[Execution Timeout]" in stderr:
                    status = "timeout"
                elif "SyntaxError:" in stderr or "IndentationError:" in stderr:
                    status = "compilation_error"
                else:
                    status = "runtime_error"

                error_details = CodeExecutor.parse_python_error(stderr, code)

            return ExecutionResult(
                status=status,
                stdout=stdout,
                stderr=stderr,
                exit_code=exit_code,
                execution_time_sec=round(elapsed_time, 4),
                peak_memory_mb=round(peak_ram, 2),
                error_line=error_details.get("error_line"),
                error_column=error_details.get("error_column"),
                error_type=error_details.get("error_type"),
                error_message=error_details.get("error_message"),
                error_pointer=error_details.get("error_pointer"),
                suggested_fix=error_details.get("suggested_fix")
            )
        finally:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass

    def analyze_complexity(self, code: str) -> ComplexityResult:
        return ComplexityAnalyzer.analyze_python_ast(code)

    def analyze_lines(self, code: str) -> List[LineAnalysisItem]:
        return LineAnalyzer.analyze_python(code)

    def audit_security(self, code: str) -> List[SecurityIssue]:
        return SecurityScanner.audit_python(code)

    def evaluate_quality(self, code: str) -> QualityMetric:
        return QualityAuditor.evaluate_python(code)
