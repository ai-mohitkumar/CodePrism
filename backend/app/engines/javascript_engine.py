import tempfile
import os
import re
from typing import List, Optional, Dict, Any
from app.engines.base import BaseLanguageEngine
from app.models import ExecutionResult, ComplexityResult, LineAnalysisItem, SecurityIssue, QualityMetric
from app.analyzers.complexity import ComplexityAnalyzer
from app.analyzers.line_analyzer import LineAnalyzer
from app.analyzers.security import SecurityScanner
from app.analyzers.quality import QualityAuditor
from app.profiler.executor import CodeExecutor

class JavaScriptLanguageEngine(BaseLanguageEngine):
    @property
    def language_id(self) -> str:
        return "javascript"

    def execute(self, code: str, stdin: str = "", timeout_sec: float = 5.0) -> ExecutionResult:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False, encoding="utf-8") as f:
            f.write(code)
            temp_path = f.name

        try:
            exit_code, stdout, stderr, elapsed_time, peak_ram = CodeExecutor.execute_command(
                ["node", temp_path],
                stdin_text=stdin,
                timeout_sec=timeout_sec
            )

            status = "success"
            line_no = None
            col_no = None
            error_pointer = None
            err_type = "JavaScript Runtime Error"

            if exit_code != 0 or stderr:
                status = "timeout" if "[Execution Timeout]" in stderr else "runtime_error"
                if "SyntaxError:" in stderr:
                    status = "compilation_error"
                    err_type = "JavaScript Syntax Error"

                # Parse node error stack
                match = re.search(r'\.js:(\d+)(?::(\d+))?', stderr)
                if match:
                    line_no = int(match.group(1))
                    col_no = int(match.group(2)) if match.group(2) else None
                    lines = code.splitlines()
                    if 1 <= line_no <= len(lines):
                        target = lines[line_no - 1]
                        error_pointer = target + "\n" + " " * max(0, (col_no or len(target)) - 1) + "^ Error here"

            return ExecutionResult(
                status=status,
                stdout=stdout,
                stderr=stderr,
                exit_code=exit_code,
                execution_time_sec=round(elapsed_time, 4),
                peak_memory_mb=round(peak_ram, 2),
                error_line=line_no,
                error_column=col_no,
                error_type=err_type if (exit_code != 0 or stderr) else None,
                error_message=stderr.strip() if stderr else None,
                error_pointer=error_pointer
            )
        finally:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass

    def analyze_complexity(self, code: str) -> ComplexityResult:
        return ComplexityAnalyzer.analyze_generic(code, "javascript")

    def analyze_lines(self, code: str) -> List[LineAnalysisItem]:
        return LineAnalyzer.analyze_generic(code, "javascript")

    def audit_security(self, code: str) -> List[SecurityIssue]:
        return SecurityScanner.audit_generic(code, "javascript")

    def evaluate_quality(self, code: str) -> QualityMetric:
        return QualityAuditor.evaluate_generic(code, "javascript")
