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

class JavaLanguageEngine(BaseLanguageEngine):
    @property
    def language_id(self) -> str:
        return "java"

    def execute(self, code: str, stdin: str = "", timeout_sec: float = 6.0) -> ExecutionResult:
        # Extract class name or default to Main
        class_match = re.search(r'public\s+class\s+([a-zA-Z_][a-zA-Z0-9_]*)', code)
        class_name = class_match.group(1) if class_match else "Main"

        # If code doesn't define the class, wrap it
        if "class " not in code:
            code = f"""public class Main {{
    public static void main(String[] args) {{
        {code}
    }}
}}"""
            class_name = "Main"

        with tempfile.TemporaryDirectory() as temp_dir:
            src_path = os.path.join(temp_dir, f"{class_name}.java")
            with open(src_path, "w", encoding="utf-8") as f:
                f.write(code)

            # Step 1: Compile with javac
            c_exit, c_out, c_err, c_time, _ = CodeExecutor.execute_command(
                ["javac", f"{class_name}.java"],
                cwd=temp_dir,
                timeout_sec=8.0
            )

            if c_exit != 0:
                line_no = None
                error_pointer = None
                match = re.search(rf'{class_name}\.java:(\d+):\s*error:\s*(.*)', c_err)
                if match:
                    line_no = int(match.group(1))
                    msg = match.group(2)
                    lines = code.splitlines()
                    if 1 <= line_no <= len(lines):
                        target = lines[line_no - 1]
                        error_pointer = target + "\n" + " " * len(target) + "^ " + msg

                return ExecutionResult(
                    status="compilation_error",
                    stdout="",
                    stderr=c_err,
                    exit_code=c_exit,
                    execution_time_sec=round(c_time, 4),
                    peak_memory_mb=0.0,
                    error_line=line_no,
                    error_type="Java Compilation Error",
                    error_message=c_err.strip(),
                    error_pointer=error_pointer
                )

            # Step 2: Run java bytecode
            r_exit, r_out, r_err, r_time, r_ram = CodeExecutor.execute_command(
                ["java", class_name],
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
        return ComplexityAnalyzer.analyze_generic(code, "java")

    def analyze_lines(self, code: str) -> List[LineAnalysisItem]:
        return LineAnalyzer.analyze_generic(code, "java")

    def audit_security(self, code: str) -> List[SecurityIssue]:
        return SecurityScanner.audit_generic(code, "java")

    def evaluate_quality(self, code: str) -> QualityMetric:
        return QualityAuditor.evaluate_generic(code, "java")
