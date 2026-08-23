import tempfile
import os
import re
from app.engines.adapters.base_adapter import UniversalLanguageAdapter, LanguageFamily
from app.models import ExecutionResult
from app.profiler.executor import CodeExecutor

class TypeScriptAdapter(UniversalLanguageAdapter):
    def __init__(self):
        super().__init__(
            lang_id="typescript",
            display_name="TypeScript",
            family=LanguageFamily.SCRIPTED_JIT,
            tier=1,
            extension="ts",
            toolchain_cmd="node",
            icon="🔷"
        )

    def execute(self, code: str, stdin: str = "", timeout_sec: float = 5.0) -> ExecutionResult:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ts", delete=False, encoding="utf-8") as f:
            f.write(code)
            temp_path = f.name

        try:
            # Node 22 supports --experimental-strip-types
            exit_code, stdout, stderr, elapsed_time, peak_ram = CodeExecutor.execute_command(
                ["node", "--experimental-strip-types", temp_path],
                stdin_text=stdin,
                timeout_sec=timeout_sec
            )

            # Filter out harmless Node experimental warnings from stderr
            clean_stderr = "\n".join([
                line for line in stderr.splitlines() 
                if not line.startswith("(node:") and "ExperimentalWarning" not in line
            ]).strip()

            status = "success"
            line_no = None
            if exit_code != 0 or ("Error:" in clean_stderr):
                status = "timeout" if "[Execution Timeout]" in stderr else "runtime_error"
                match = re.search(r'\.ts:(\d+)', stderr)
                if match:
                    line_no = int(match.group(1))

            return ExecutionResult(
                status=status,
                stdout=stdout,
                stderr=clean_stderr,
                exit_code=exit_code,
                execution_time_sec=round(elapsed_time, 4),
                peak_memory_mb=round(peak_ram, 2),
                error_line=line_no,
                error_type="TypeScript Execution Error" if status != "success" else None,
                error_message=clean_stderr if clean_stderr else None
            )
        finally:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass
