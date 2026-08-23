import tempfile
import os
import re
import time
from typing import Optional, List
from languages.base import BaseLanguageAdapter
from models import (
    LanguageTier, LanguageFamily, StandardCompileResult,
    StandardExecutionResult, CompileResponse, CompilerDiagnostic
)
from sandbox.executor import SecureSandboxExecutor

class JavaAdapter(BaseLanguageAdapter):
    def __init__(self):
        super().__init__(
            lang_id="java",
            name="Java (JDK 25)",
            tier=LanguageTier.TIER_A,
            family=LanguageFamily.MANAGED_VM,
            extension="java",
            icon="☕",
            toolchain_cmd="javac"
        )

    def _extract_class_name(self, code: str) -> str:
        match = re.search(r'public\s+class\s+([A-Za-z0-9_]+)', code)
        if match:
            return match.group(1)
        match2 = re.search(r'class\s+([A-Za-z0-9_]+)', code)
        if match2:
            return match2.group(1)
        return "Main"

    def compile(self, code: str) -> StandardCompileResult:
        class_name = self._extract_class_name(code)
        with tempfile.TemporaryDirectory() as temp_dir:
            src = os.path.join(temp_dir, f"{class_name}.java")
            with open(src, "w", encoding="utf-8") as f:
                f.write(code)

            c_exit, c_out, c_err, _, _, _ = SecureSandboxExecutor.execute(
                ["javac", src],
                cwd=temp_dir,
                timeout_sec=8.0
            )

            if c_exit != 0:
                match = re.search(r':(\d+):\s*error:\s*(.*)', c_err)
                line_no = int(match.group(1)) if match else 1
                msg = match.group(2) if match else c_err.strip()
                return StandardCompileResult(
                    success=False,
                    compiler_output=c_err,
                    errors=[msg],
                    error_line=line_no
                )

        return StandardCompileResult(success=True)

    def compile_detailed(self, code: str, flags: Optional[List[str]] = None) -> CompileResponse:
        class_name = self._extract_class_name(code)
        start_time = time.perf_counter()

        with tempfile.TemporaryDirectory() as temp_dir:
            src = os.path.join(temp_dir, f"{class_name}.java")
            with open(src, "w", encoding="utf-8") as f:
                f.write(code)

            # Compile with javac
            c_exit, c_out, c_err, c_ms, _, _ = SecureSandboxExecutor.execute(
                ["javac", src],
                cwd=temp_dir,
                timeout_sec=8.0
            )
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            if c_exit != 0:
                diagnostics: List[CompilerDiagnostic] = []
                lines = code.splitlines()
                for match in re.finditer(r':(\d+):\s*(error|warning):\s*(.*)', c_err):
                    line_no = int(match.group(1))
                    sev = match.group(2)
                    msg = match.group(3)
                    pointer = ""
                    if 1 <= line_no <= len(lines):
                        pointer = lines[line_no - 1] + "\n" + " " * max(0, len(lines[line_no - 1])) + "^ " + msg
                    diagnostics.append(CompilerDiagnostic(
                        severity=sev,
                        line=line_no,
                        message=msg,
                        pointer=pointer
                    ))

                return CompileResponse(
                    success=False,
                    compiler_name="OpenJDK javac 25",
                    target_artifact=None,
                    artifact_type="JVM Bytecode (.class)",
                    compilation_time_ms=round(elapsed_ms, 2),
                    errors_count=len([d for d in diagnostics if d.severity == "error"]) or 1,
                    warnings_count=len([d for d in diagnostics if d.severity == "warning"]),
                    raw_output=c_err,
                    diagnostics=diagnostics,
                    ir_bytecode=None
                )

            # Disassemble JVM Bytecode with javap
            bytecode_text = ""
            try:
                _, jp_out, _, _, _, _ = SecureSandboxExecutor.execute(
                    ["javap", "-c", class_name],
                    cwd=temp_dir,
                    timeout_sec=4.0
                )
                bytecode_text = jp_out
            except Exception:
                bytecode_text = "// javap bytecode disassembler preview skipped"

            return CompileResponse(
                success=True,
                compiler_name="OpenJDK javac 25",
                target_artifact=f"{class_name}.class",
                artifact_type="JVM Bytecode (.class)",
                compilation_time_ms=round(elapsed_ms, 2),
                errors_count=0,
                warnings_count=0,
                raw_output=f"✓ Compiled successfully to JVM bytecode `{class_name}.class`.",
                diagnostics=[],
                ir_bytecode=bytecode_text
            )

    def execute(self, code: str, stdin: str = "", timeout_sec: float = 5.0) -> StandardExecutionResult:
        class_name = self._extract_class_name(code)
        with tempfile.TemporaryDirectory() as temp_dir:
            src = os.path.join(temp_dir, f"{class_name}.java")
            with open(src, "w", encoding="utf-8") as f:
                f.write(code)

            # Compile
            c_exit, c_out, c_err, c_ms, _, _ = SecureSandboxExecutor.execute(
                ["javac", src],
                cwd=temp_dir,
                timeout_sec=8.0
            )

            if c_exit != 0:
                return StandardExecutionResult(
                    status="compilation_error",
                    exit_code=c_exit,
                    stderr=c_err,
                    runtime_ms=round(c_ms, 2)
                )

            # Run JVM
            r_exit, r_out, r_err, r_ms, r_mb, r_cpu = SecureSandboxExecutor.execute(
                ["java", "-Xmx256m", class_name],
                cwd=temp_dir,
                stdin_text=stdin,
                timeout_sec=timeout_sec
            )

            status = "success"
            if r_exit != 0 or r_err:
                status = "timeout" if "[SandboxLimit]" in r_err else "runtime_error"

            return StandardExecutionResult(
                exit_code=r_exit,
                stdout=r_out,
                stderr=r_err,
                runtime_ms=round(r_ms, 2),
                memory_mb=r_mb,
                cpu_percent=r_cpu,
                status=status
            )
