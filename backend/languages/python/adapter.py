import ast
import dis
import io
import tempfile
import os
import re
import time
from typing import Optional, List
from languages.base import BaseLanguageAdapter
from models import (
    LanguageTier, LanguageFamily, StandardCompileResult,
    StandardExecutionResult, StandardComplexityResult,
    StandardQualityResult, StandardSecurityResult, ASTResponse,
    CompileResponse, CompilerDiagnostic
)
from analysis.ast import ASTParser
from analysis.complexity import ComplexityEngine
from analysis.security import SecurityAuditor
from analysis.quality import QualityEngine
from profiler.runtime import RuntimeProfiler
from sandbox.executor import SecureSandboxExecutor

class PythonAdapter(BaseLanguageAdapter):
    def __init__(self):
        super().__init__(
            lang_id="python",
            name="Python 3.12",
            tier=LanguageTier.TIER_A,
            family=LanguageFamily.SCRIPT_JIT,
            extension="py",
            icon="🐍",
            toolchain_cmd="python"
        )

    def compile(self, code: str) -> StandardCompileResult:
        try:
            ast.parse(code)
            return StandardCompileResult(success=True)
        except SyntaxError as e:
            line_no = e.lineno or 1
            col_no = e.offset or 1
            lines = code.splitlines()
            pointer = ""
            suggested_fix = None
            if 1 <= line_no <= len(lines):
                target_line = lines[line_no - 1]
                pointer = target_line + "\n" + " " * max(0, col_no - 1) + "^ " + (e.msg or "Syntax error")
                if target_line.strip().startswith(("if", "for", "while", "def", "class", "elif", "else")) and not target_line.strip().endswith(":"):
                    suggested_fix = target_line + ":"

            return StandardCompileResult(
                success=False,
                compiler_output=f"SyntaxError: {e.msg} at line {line_no}:{col_no}",
                errors=[f"SyntaxError: {e.msg}"],
                error_line=line_no,
                error_column=col_no,
                error_pointer=pointer,
                suggested_fix=suggested_fix
            )

    def compile_detailed(self, code: str, flags: Optional[List[str]] = None) -> CompileResponse:
        start_time = time.perf_counter()
        std_res = self.compile(code)
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        if not std_res.success:
            return CompileResponse(
                success=False,
                compiler_name="CPython 3.12 Bytecode Compiler",
                target_artifact=None,
                artifact_type="Python Bytecode (.pyc)",
                compilation_time_ms=round(elapsed_ms, 2),
                errors_count=1,
                warnings_count=0,
                raw_output=std_res.compiler_output,
                diagnostics=[CompilerDiagnostic(
                    severity="error",
                    line=std_res.error_line,
                    column=std_res.error_column,
                    message=std_res.compiler_output,
                    pointer=std_res.error_pointer,
                    suggested_fix=std_res.suggested_fix
                )],
                ir_bytecode=None
            )

        # Generate Python Disassembly / Bytecode IR
        ir_disassembly = ""
        try:
            compiled_code = compile(code, "<code_prism>", "exec")
            out_buf = io.StringIO()
            dis.dis(compiled_code, file=out_buf)
            ir_disassembly = out_buf.getvalue()
        except Exception:
            ir_disassembly = "# Bytecode disassembly not available"

        return CompileResponse(
            success=True,
            compiler_name="CPython 3.12 Bytecode Compiler",
            target_artifact="program.pyc",
            artifact_type="Python Bytecode (.pyc / Code Object)",
            compilation_time_ms=round(elapsed_ms, 2),
            errors_count=0,
            warnings_count=0,
            raw_output="✓ Python AST parsed & Bytecode generated successfully.",
            diagnostics=[],
            ir_bytecode=ir_disassembly
        )

    def execute(self, code: str, stdin: str = "", timeout_sec: float = 5.0) -> StandardExecutionResult:
        exit_code, stdout, stderr, runtime_ms, peak_mb, cpu_pct, functions = RuntimeProfiler.execute_and_profile_python(
            code, stdin=stdin, timeout_sec=timeout_sec
        )
        status = "success"
        if exit_code != 0 or stderr:
            status = "timeout" if "[TimeoutError]" in stderr or "[SandboxLimit]" in stderr else "runtime_error"

        return StandardExecutionResult(
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            runtime_ms=runtime_ms,
            memory_mb=peak_mb,
            cpu_percent=cpu_pct,
            functions=functions,
            status=status
        )

    def parse_ast(self, code: str) -> Optional[ASTResponse]:
        return ASTParser.parse_python(code)

    def analyze_complexity(self, code: str) -> StandardComplexityResult:
        comp = ComplexityEngine.analyze_python(code)
        return StandardComplexityResult(
            time=comp.time_complexity,
            space=comp.space_complexity,
            confidence=comp.confidence,
            reason=comp.reason,
            nested_depth=comp.nested_depth,
            has_recursion=comp.has_recursion,
            has_halving=comp.has_halving,
            details=comp.details
        )

    def audit_security(self, code: str) -> StandardSecurityResult:
        issues = SecurityAuditor.audit_python(code)
        crit = sum(1 for i in issues if i.severity.lower() == 'critical')
        high = sum(1 for i in issues if i.severity.lower() == 'high')
        med = sum(1 for i in issues if i.severity.lower() == 'medium')
        low = sum(1 for i in issues if i.severity.lower() == 'low')
        return StandardSecurityResult(
            critical=crit,
            high=high,
            medium=med,
            low=low,
            issues=issues
        )

    def evaluate_quality(self, code: str) -> StandardQualityResult:
        q = QualityEngine.evaluate_python(code)
        return StandardQualityResult(
            score=round(q.maintainability_score * 10, 1),
            maintainability=q.maintainability_score,
            readability=q.readability_score,
            cyclomatic=q.cyclomatic_complexity,
            total_lines=q.total_lines,
            code_lines=q.code_lines,
            comment_lines=q.comment_lines,
            issues=q.issues
        )
