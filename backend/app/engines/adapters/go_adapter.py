import tempfile
import os
import re
from app.engines.adapters.base_adapter import UniversalLanguageAdapter, LanguageFamily
from app.models import ExecutionResult
from app.profiler.executor import CodeExecutor

class GoAdapter(UniversalLanguageAdapter):
    def __init__(self):
        super().__init__(
            lang_id="go",
            display_name="Go (Golang)",
            family=LanguageFamily.COMPILED_NATIVE,
            tier=1,
            extension="go",
            toolchain_cmd="go",
            icon="🐹"
        )

    def execute(self, code: str, stdin: str = "", timeout_sec: float = 6.0) -> ExecutionResult:
        if not self.is_toolchain_installed():
            return self.fallback_execution_notice(code)

        if "package " not in code:
            code = f"""package main
import "fmt"

func main() {{
    {code}
}}"""

        with tempfile.TemporaryDirectory() as temp_dir:
            src_path = os.path.join(temp_dir, "main.go")
            with open(src_path, "w", encoding="utf-8") as f:
                f.write(code)

            r_exit, r_out, r_err, r_time, r_ram = CodeExecutor.execute_command(
                ["go", "run", "main.go"],
                cwd=temp_dir,
                stdin_text=stdin,
                timeout_sec=timeout_sec
            )

            status = "success"
            line_no = None
            if r_exit != 0:
                status = "compilation_error" if "syntax error" in r_err or "undefined" in r_err else "runtime_error"
                match = re.search(r'main\.go:(\d+):(\d+)', r_err)
                if match:
                    line_no = int(match.group(1))

            return ExecutionResult(
                status=status,
                stdout=r_out,
                stderr=r_err,
                exit_code=r_exit,
                execution_time_sec=round(r_time, 4),
                peak_memory_mb=round(r_ram, 2),
                error_line=line_no,
                error_type="Go Compilation / Runtime Error" if r_exit != 0 else None,
                error_message=r_err.strip() if r_exit != 0 else None
            )
