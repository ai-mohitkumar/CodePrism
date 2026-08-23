import tempfile
import os
import re
from languages.base import BaseLanguageAdapter
from models import (
    LanguageTier, LanguageFamily, StandardCompileResult,
    StandardExecutionResult
)
from sandbox.executor import SecureSandboxExecutor

class JavaScriptAdapter(BaseLanguageAdapter):
    def __init__(self):
        super().__init__(
            lang_id="javascript",
            name="JavaScript (Node.js)",
            tier=LanguageTier.TIER_A,
            family=LanguageFamily.SCRIPT_JIT,
            extension="js",
            icon="🌐",
            toolchain_cmd="node"
        )

    def compile(self, code: str) -> StandardCompileResult:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False, encoding="utf-8") as f:
            f.write(code)
            temp_path = f.name

        try:
            exit_code, stdout, stderr, _, _, _ = SecureSandboxExecutor.execute(
                ["node", "--check", temp_path],
                timeout_sec=4.0
            )

            if exit_code != 0 and stderr:
                match = re.search(r'\.js:(\d+)', stderr)
                line_no = int(match.group(1)) if match else 1
                lines = code.splitlines()
                pointer = ""
                if 1 <= line_no <= len(lines):
                    pointer = lines[line_no - 1] + "\n" + " " * len(lines[line_no - 1]) + "^ Syntax Error"

                return StandardCompileResult(
                    success=False,
                    compiler_output=stderr,
                    errors=[stderr.strip()],
                    error_line=line_no,
                    error_pointer=pointer
                )

            return StandardCompileResult(success=True)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def execute(self, code: str, stdin: str = "", timeout_sec: float = 5.0) -> StandardExecutionResult:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False, encoding="utf-8") as f:
            f.write(code)
            temp_path = f.name

        try:
            exit_code, stdout, stderr, r_ms, r_mb, r_cpu = SecureSandboxExecutor.execute(
                ["node", temp_path],
                stdin_text=stdin,
                timeout_sec=timeout_sec
            )

            clean_stderr = "\n".join([
                l for l in stderr.splitlines() if not l.startswith("(node:")
            ]).strip()

            status = "success"
            if exit_code != 0:
                status = "timeout" if "[SandboxLimit]" in stderr else "runtime_error"

            return StandardExecutionResult(
                exit_code=exit_code,
                stdout=stdout,
                stderr=clean_stderr,
                runtime_ms=r_ms,
                memory_mb=r_mb,
                cpu_percent=r_cpu,
                status=status
            )
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
