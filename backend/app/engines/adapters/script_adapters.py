import tempfile
import os
import re
from app.engines.adapters.base_adapter import UniversalLanguageAdapter, LanguageFamily
from app.models import ExecutionResult
from app.profiler.executor import CodeExecutor

class KotlinAdapter(UniversalLanguageAdapter):
    def __init__(self):
        super().__init__(
            lang_id="kotlin",
            display_name="Kotlin",
            family=LanguageFamily.MANAGED_VM,
            tier=1,
            extension="kt",
            toolchain_cmd="kotlinc",
            icon="🟣"
        )

    def execute(self, code: str, stdin: str = "", timeout_sec: float = 6.0) -> ExecutionResult:
        if not self.is_toolchain_installed():
            return self.fallback_execution_notice(code)

        with tempfile.TemporaryDirectory() as temp_dir:
            src_path = os.path.join(temp_dir, "Main.kt")
            jar_path = os.path.join(temp_dir, "Main.jar")
            with open(src_path, "w", encoding="utf-8") as f:
                f.write(code)

            c_exit, c_out, c_err, c_time, _ = CodeExecutor.execute_command(
                ["kotlinc", "Main.kt", "-include-runtime", "-d", "Main.jar"],
                cwd=temp_dir,
                timeout_sec=8.0
            )

            if c_exit != 0:
                return ExecutionResult(
                    status="compilation_error",
                    stdout="",
                    stderr=c_err,
                    exit_code=c_exit,
                    execution_time_sec=round(c_time, 4),
                    peak_memory_mb=0.0,
                    error_message=c_err.strip()
                )

            r_exit, r_out, r_err, r_time, r_ram = CodeExecutor.execute_command(
                ["java", "-jar", "Main.jar"],
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

class PHPAdapter(UniversalLanguageAdapter):
    def __init__(self):
        super().__init__(
            lang_id="php",
            display_name="PHP",
            family=LanguageFamily.SCRIPTED_JIT,
            tier=1,
            extension="php",
            toolchain_cmd="php",
            icon="🐘"
        )

    def execute(self, code: str, stdin: str = "", timeout_sec: float = 5.0) -> ExecutionResult:
        if not self.is_toolchain_installed():
            return self.fallback_execution_notice(code)

        if not code.strip().startswith("<?php"):
            code = "<?php\n" + code

        with tempfile.NamedTemporaryFile(mode="w", suffix=".php", delete=False, encoding="utf-8") as f:
            f.write(code)
            temp_path = f.name

        try:
            exit_code, stdout, stderr, elapsed, ram = CodeExecutor.execute_command(
                ["php", temp_path],
                stdin_text=stdin,
                timeout_sec=timeout_sec
            )
            return ExecutionResult(
                status="success" if exit_code == 0 else "runtime_error",
                stdout=stdout,
                stderr=stderr,
                exit_code=exit_code,
                execution_time_sec=round(elapsed, 4),
                peak_memory_mb=round(ram, 2)
            )
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

class RubyAdapter(UniversalLanguageAdapter):
    def __init__(self):
        super().__init__(
            lang_id="ruby",
            display_name="Ruby",
            family=LanguageFamily.SCRIPTED_JIT,
            tier=1,
            extension="rb",
            toolchain_cmd="ruby",
            icon="💎"
        )

    def execute(self, code: str, stdin: str = "", timeout_sec: float = 5.0) -> ExecutionResult:
        if not self.is_toolchain_installed():
            return self.fallback_execution_notice(code)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".rb", delete=False, encoding="utf-8") as f:
            f.write(code)
            temp_path = f.name

        try:
            exit_code, stdout, stderr, elapsed, ram = CodeExecutor.execute_command(
                ["ruby", temp_path],
                stdin_text=stdin,
                timeout_sec=timeout_sec
            )
            return ExecutionResult(
                status="success" if exit_code == 0 else "runtime_error",
                stdout=stdout,
                stderr=stderr,
                exit_code=exit_code,
                execution_time_sec=round(elapsed, 4),
                peak_memory_mb=round(ram, 2)
            )
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

class DartAdapter(UniversalLanguageAdapter):
    def __init__(self):
        super().__init__(
            lang_id="dart",
            display_name="Dart",
            family=LanguageFamily.SCRIPTED_JIT,
            tier=1,
            extension="dart",
            toolchain_cmd="dart",
            icon="🎯"
        )

    def execute(self, code: str, stdin: str = "", timeout_sec: float = 5.0) -> ExecutionResult:
        if not self.is_toolchain_installed():
            return self.fallback_execution_notice(code)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".dart", delete=False, encoding="utf-8") as f:
            f.write(code)
            temp_path = f.name

        try:
            exit_code, stdout, stderr, elapsed, ram = CodeExecutor.execute_command(
                ["dart", "run", temp_path],
                stdin_text=stdin,
                timeout_sec=timeout_sec
            )
            return ExecutionResult(
                status="success" if exit_code == 0 else "runtime_error",
                stdout=stdout,
                stderr=stderr,
                exit_code=exit_code,
                execution_time_sec=round(elapsed, 4),
                peak_memory_mb=round(ram, 2)
            )
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

class RAdapter(UniversalLanguageAdapter):
    def __init__(self):
        super().__init__(
            lang_id="r",
            display_name="R (Data Science)",
            family=LanguageFamily.SCRIPTED_JIT,
            tier=1,
            extension="r",
            toolchain_cmd="Rscript",
            icon="📈"
        )

    def execute(self, code: str, stdin: str = "", timeout_sec: float = 5.0) -> ExecutionResult:
        if not self.is_toolchain_installed():
            return self.fallback_execution_notice(code)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".R", delete=False, encoding="utf-8") as f:
            f.write(code)
            temp_path = f.name

        try:
            exit_code, stdout, stderr, elapsed, ram = CodeExecutor.execute_command(
                ["Rscript", temp_path],
                stdin_text=stdin,
                timeout_sec=timeout_sec
            )
            return ExecutionResult(
                status="success" if exit_code == 0 else "runtime_error",
                stdout=stdout,
                stderr=stderr,
                exit_code=exit_code,
                execution_time_sec=round(elapsed, 4),
                peak_memory_mb=round(ram, 2)
            )
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

class SwiftAdapter(UniversalLanguageAdapter):
    def __init__(self):
        super().__init__(
            lang_id="swift",
            display_name="Swift",
            family=LanguageFamily.COMPILED_NATIVE,
            tier=1,
            extension="swift",
            toolchain_cmd="swift",
            icon="🕊️"
        )

    def execute(self, code: str, stdin: str = "", timeout_sec: float = 5.0) -> ExecutionResult:
        if not self.is_toolchain_installed():
            return self.fallback_execution_notice(code)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".swift", delete=False, encoding="utf-8") as f:
            f.write(code)
            temp_path = f.name

        try:
            exit_code, stdout, stderr, elapsed, ram = CodeExecutor.execute_command(
                ["swift", temp_path],
                stdin_text=stdin,
                timeout_sec=timeout_sec
            )
            return ExecutionResult(
                status="success" if exit_code == 0 else "runtime_error",
                stdout=stdout,
                stderr=stderr,
                exit_code=exit_code,
                execution_time_sec=round(elapsed, 4),
                peak_memory_mb=round(ram, 2)
            )
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
