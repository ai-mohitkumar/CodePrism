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

class CppLanguageEngine(BaseLanguageEngine):
    @property
    def language_id(self) -> str:
        return "cpp"

    def execute(self, code: str, stdin: str = "", timeout_sec: float = 5.0) -> ExecutionResult:
        with tempfile.TemporaryDirectory() as temp_dir:
            src_path = os.path.join(temp_dir, "solution.cpp")
            exe_path = os.path.join(temp_dir, "solution.exe")

            with open(src_path, "w", encoding="utf-8") as f:
                f.write(code)

            # Step 1: Compile with g++
            compile_cmd = ["g++", "-O2", "-std=c++17", src_path, "-o", exe_path]
            c_exit, c_out, c_err, c_time, _ = CodeExecutor.execute_command(compile_cmd, cwd=temp_dir, timeout_sec=8.0)

            if c_exit != 0:
                # Parse GCC compile error
                line_no = None
                col_no = None
                suggested_fix = None
                error_pointer = None

                match = re.search(r'solution\.cpp:(\d+):(\d+):\s*error:\s*(.*)', c_err)
                if match:
                    line_no = int(match.group(1))
                    col_no = int(match.group(2))
                    msg = match.group(3)
                    lines = code.splitlines()
                    if 1 <= line_no <= len(lines):
                        target = lines[line_no - 1]
                        error_pointer = target + "\n" + " " * max(0, col_no - 1) + "^ " + msg

                return ExecutionResult(
                    status="compilation_error",
                    stdout="",
                    stderr=c_err,
                    exit_code=c_exit,
                    execution_time_sec=round(c_time, 4),
                    peak_memory_mb=0.0,
                    error_line=line_no,
                    error_column=col_no,
                    error_type="C++ Compilation Error",
                    error_message=c_err.strip(),
                    error_pointer=error_pointer,
                    suggested_fix=suggested_fix
                )

            # Step 2: Run executable
            r_exit, r_out, r_err, r_time, r_ram = CodeExecutor.execute_command(
                [exe_path],
                cwd=temp_dir,
                stdin_text=stdin,
                timeout_sec=timeout_sec
            )

            status = "success"
            if r_exit != 0 or r_err:
                status = "timeout" if "[Execution Timeout]" in r_err else "runtime_error"

            return ExecutionResult(
                status=status,
                stdout=r_out,
                stderr=r_err,
                exit_code=r_exit,
                execution_time_sec=round(r_time, 4),
                peak_memory_mb=round(r_ram, 2)
            )

    def analyze_complexity(self, code: str) -> ComplexityResult:
        return ComplexityAnalyzer.analyze_generic(code, "cpp")

    def analyze_lines(self, code: str) -> List[LineAnalysisItem]:
        return LineAnalyzer.analyze_generic(code, "cpp")

    def audit_security(self, code: str) -> List[SecurityIssue]:
        return SecurityScanner.audit_generic(code, "cpp")

    def evaluate_quality(self, code: str) -> QualityMetric:
        return QualityAuditor.evaluate_generic(code, "cpp")
