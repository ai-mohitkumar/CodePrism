import tempfile
import os
import re
from app.engines.adapters.base_adapter import UniversalLanguageAdapter, LanguageFamily
from app.models import ExecutionResult
from app.profiler.executor import CodeExecutor

class RustAdapter(UniversalLanguageAdapter):
    def __init__(self):
        super().__init__(
            lang_id="rust",
            display_name="Rust",
            family=LanguageFamily.COMPILED_NATIVE,
            tier=1,
            extension="rs",
            toolchain_cmd="rustc",
            icon="🦀"
        )

    def execute(self, code: str, stdin: str = "", timeout_sec: float = 8.0) -> ExecutionResult:
        if not self.is_toolchain_installed():
            return self.fallback_execution_notice(code)

        with tempfile.TemporaryDirectory() as temp_dir:
            src_path = os.path.join(temp_dir, "main.rs")
            exe_path = os.path.join(temp_dir, "main.exe")

            with open(src_path, "w", encoding="utf-8") as f:
                f.write(code)

            c_exit, c_out, c_err, c_time, _ = CodeExecutor.execute_command(
                ["rustc", "-O", src_path, "-o", exe_path],
                cwd=temp_dir,
                timeout_sec=10.0
            )

            if c_exit != 0:
                line_no = None
                match = re.search(r'main\.rs:(\d+):(\d+)', c_err)
                if match:
                    line_no = int(match.group(1))

                return ExecutionResult(
                    status="compilation_error",
                    stdout="",
                    stderr=c_err,
                    exit_code=c_exit,
                    execution_time_sec=round(c_time, 4),
                    peak_memory_mb=0.0,
                    error_line=line_no,
                    error_type="Rust Compiler Error (rustc)",
                    error_message=c_err.strip()
                )

            r_exit, r_out, r_err, r_time, r_ram = CodeExecutor.execute_command(
                [exe_path],
                cwd=temp_dir,
                stdin_text=stdin,
                timeout_sec=timeout_sec
            )

            return ExecutionResult(
                status="success" if r_exit == 0 else "runtime_error",
                stdout=r_out,
                stderr=r_err,
                exit_code=r_exit,
                execution_time_sec=round(r_time, 4),
                peak_memory_mb=round(r_ram, 2)
            )
