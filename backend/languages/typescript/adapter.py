import tempfile
import os
import re
from languages.base import BaseLanguageAdapter
from models import (
    LanguageTier, LanguageFamily, StandardCompileResult,
    StandardExecutionResult
)
from sandbox.executor import SecureSandboxExecutor

class TypeScriptAdapter(BaseLanguageAdapter):
    def __init__(self):
        super().__init__(
            lang_id="typescript",
            name="TypeScript",
            tier=LanguageTier.TIER_A,
            family=LanguageFamily.SCRIPT_JIT,
            extension="ts",
            icon="🔷",
            toolchain_cmd="node"
        )

    def execute(self, code: str, stdin: str = "", timeout_sec: float = 5.0) -> StandardExecutionResult:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ts", delete=False, encoding="utf-8") as f:
            f.write(code)
            temp_path = f.name

        try:
            exit_code, stdout, stderr, elapsed_time, peak_ram, cpu_pct = SecureSandboxExecutor.execute(
                ["node", "--experimental-strip-types", temp_path],
                stdin_text=stdin,
                timeout_sec=timeout_sec
            )

            clean_stderr = "\n".join([
                line for line in stderr.splitlines() 
                if not line.startswith("(node:") and "ExperimentalWarning" not in line
            ]).strip()

            status = "success"
            if exit_code != 0 or ("Error:" in clean_stderr):
                status = "timeout" if "[SandboxLimit]" in stderr else "runtime_error"

            return StandardExecutionResult(
                exit_code=exit_code,
                stdout=stdout,
                stderr=clean_stderr,
                runtime_ms=elapsed_time,
                memory_mb=peak_ram,
                cpu_percent=cpu_pct,
                status=status
            )
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
