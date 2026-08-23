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

class CppAdapter(BaseLanguageAdapter):
    def __init__(self):
        super().__init__(
            lang_id="cpp",
            name="C++ (GCC)",
            tier=LanguageTier.TIER_A,
            family=LanguageFamily.NATIVE,
            extension="cpp",
            icon="⚡",
            toolchain_cmd="g++"
        )

    def compile(self, code: str) -> StandardCompileResult:
        with tempfile.TemporaryDirectory() as temp_dir:
            src = os.path.join(temp_dir, "test.cpp")
            exe = os.path.join(temp_dir, "test.exe")
            with open(src, "w", encoding="utf-8") as f:
                f.write(code)

            c_exit, c_out, c_err, _, _, _ = SecureSandboxExecutor.execute(
                ["g++", "-O2", "-std=c++17", src, "-o", exe],
                cwd=temp_dir,
                timeout_sec=8.0
            )

            if c_exit != 0:
                match = re.search(r'test\.cpp:(\d+):(\d+):\s*error:\s*(.*)', c_err)
                line_no = int(match.group(1)) if match else 1
                col_no = int(match.group(2)) if match else 1
                msg = match.group(3) if match else c_err.strip()
                lines = code.splitlines()
                pointer = ""
                if 1 <= line_no <= len(lines):
                    pointer = lines[line_no - 1] + "\n" + " " * max(0, col_no - 1) + "^ " + msg

                return StandardCompileResult(
                    success=False,
                    compiler_output=c_err,
                    errors=[msg],
                    error_line=line_no,
                    error_column=col_no,
                    error_pointer=pointer
                )

        return StandardCompileResult(success=True)

    def compile_detailed(self, code: str, flags: Optional[List[str]] = None) -> CompileResponse:
        compiler_flags = flags if flags else ["-O2", "-std=c++17"]
        start_time = time.perf_counter()

        with tempfile.TemporaryDirectory() as temp_dir:
            src = os.path.join(temp_dir, "prog.cpp")
            exe = os.path.join(temp_dir, "prog.exe")
            asm_file = os.path.join(temp_dir, "prog.s")
            with open(src, "w", encoding="utf-8") as f:
                f.write(code)

            # Compile to native binary
            c_exit, c_out, c_err, c_ms, _, _ = SecureSandboxExecutor.execute(
                ["g++"] + compiler_flags + [src, "-o", exe],
                cwd=temp_dir,
                timeout_sec=8.0
            )
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            if c_exit != 0:
                diagnostics: List[CompilerDiagnostic] = []
                lines = code.splitlines()
                for match in re.finditer(r'prog\.cpp:(\d+):(\d+):\s*(error|warning):\s*(.*)', c_err):
                    line_no = int(match.group(1))
                    col_no = int(match.group(2))
                    sev = match.group(3)
                    msg = match.group(4)
                    pointer = ""
                    if 1 <= line_no <= len(lines):
                        pointer = lines[line_no - 1] + "\n" + " " * max(0, col_no - 1) + "^ " + msg

                    diagnostics.append(CompilerDiagnostic(
                        severity=sev,
                        line=line_no,
                        column=col_no,
                        message=msg,
                        pointer=pointer
                    ))

                return CompileResponse(
                    success=False,
                    compiler_name="GCC G++ MinGW (x86_64-w64-mingw32)",
                    target_artifact=None,
                    artifact_type="Native Executable (PE x86_64)",
                    compilation_time_ms=round(elapsed_ms, 2),
                    errors_count=len([d for d in diagnostics if d.severity == "error"]) or 1,
                    warnings_count=len([d for d in diagnostics if d.severity == "warning"]),
                    raw_output=c_err,
                    diagnostics=diagnostics,
                    ir_bytecode=None
                )

            # Generate Assembly (.s)
            asm_text = ""
            try:
                SecureSandboxExecutor.execute(
                    ["g++", "-S", "-O2", "-std=c++17", "-fno-asynchronous-unwind-tables", src, "-o", asm_file],
                    cwd=temp_dir,
                    timeout_sec=4.0
                )
                if os.path.exists(asm_file):
                    with open(asm_file, "r", encoding="utf-8", errors="replace") as af:
                        asm_text = "\n".join(af.readlines()[:60])  # preview first 60 assembly lines
            except Exception:
                asm_text = "; Assembly output generation skipped"

            return CompileResponse(
                success=True,
                compiler_name="GCC G++ MinGW (x86_64-w64-mingw32)",
                target_artifact="prog.exe",
                artifact_type="Native Executable (PE x86_64)",
                compilation_time_ms=round(elapsed_ms, 2),
                errors_count=0,
                warnings_count=0,
                raw_output=f"✓ Compiled successfully to native binary `prog.exe` with flags {' '.join(compiler_flags)}.",
                diagnostics=[],
                ir_bytecode=asm_text
            )

    def execute(self, code: str, stdin: str = "", timeout_sec: float = 5.0) -> StandardExecutionResult:
        with tempfile.TemporaryDirectory() as temp_dir:
            src = os.path.join(temp_dir, "prog.cpp")
            exe = os.path.join(temp_dir, "prog.exe")
            with open(src, "w", encoding="utf-8") as f:
                f.write(code)

            # Compile
            c_exit, c_out, c_err, c_ms, _, _ = SecureSandboxExecutor.execute(
                ["g++", "-O2", "-std=c++17", src, "-o", exe],
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

            # Run binary
            r_exit, r_out, r_err, r_ms, r_mb, r_cpu = SecureSandboxExecutor.execute(
                [exe],
                cwd=temp_dir,
                stdin_text=stdin,
                timeout_sec=timeout_sec
            )

            status = "success"
            if r_exit != 0 or r_err:
                status = "timeout" if "[SandboxLimit]" in r_err or "[TimeoutError]" in r_err else "runtime_error"

            return StandardExecutionResult(
                exit_code=r_exit,
                stdout=r_out,
                stderr=r_err,
                runtime_ms=round(r_ms, 2),
                memory_mb=r_mb,
                cpu_percent=r_cpu,
                status=status
            )
