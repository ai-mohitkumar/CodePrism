import subprocess
import time
import os
import sys
import threading
import tempfile
import re
from typing import Optional, Dict, Any, Tuple
from app.models import ExecutionResult
from app.profiler.memory import monitor_process_memory

class CodeExecutor:
    """
    Executes source code in isolated temporary files with runtime timeout and memory profiling.
    """

    @classmethod
    def execute_command(
        cls,
        cmd: list,
        cwd: Optional[str] = None,
        stdin_text: str = "",
        timeout_sec: float = 5.0
    ) -> Tuple[int, str, str, float, float]:
        """
        Runs command, captures stdout/stderr, wall time in seconds, and peak RAM in MB.
        """
        start_time = time.perf_counter()
        peak_ram_mb = 0.0

        try:
            proc = subprocess.Popen(
                cmd,
                cwd=cwd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace"
            )

            # Memory tracking thread
            stop_event = threading.Event()
            mem_result = [4.2]

            def track_mem():
                mem_result[0] = monitor_process_memory(proc.pid, stop_event)

            mem_thread = threading.Thread(target=track_mem, daemon=True)
            mem_thread.start()

            try:
                stdout, stderr = proc.communicate(input=stdin_text, timeout=timeout_sec)
                exit_code = proc.returncode
            except subprocess.TimeoutExpired:
                proc.kill()
                stdout, stderr = proc.communicate()
                exit_code = -1
                stderr += f"\n[Execution Timeout] Program exceeded maximum time limit of {timeout_sec}s."
            finally:
                stop_event.set()
                mem_thread.join(timeout=0.1)

            elapsed_time = time.perf_counter() - start_time
            peak_ram_mb = max(mem_result[0], 5.0)

            return exit_code, stdout, stderr, elapsed_time, peak_ram_mb

        except Exception as e:
            elapsed_time = time.perf_counter() - start_time
            return -1, "", str(e), elapsed_time, 0.0

    @classmethod
    def parse_python_error(cls, stderr: str, code: str) -> Dict[str, Any]:
        """
        Extracts line number, column, caret pointer, and smart fix suggestions from Python stderr.
        """
        error_info: Dict[str, Any] = {
            "error_type": "Runtime Error",
            "error_message": stderr.strip(),
            "error_line": None,
            "error_column": None,
            "error_pointer": None,
            "suggested_fix": None
        }

        # SyntaxError match: File "...", line X, column Y
        syntax_match = re.search(r'File ".*?", line (\d+)(?:, column (\d+))?', stderr)
        if syntax_match:
            line_no = int(syntax_match.group(1))
            col_no = int(syntax_match.group(2)) if syntax_match.group(2) else None
            error_info["error_line"] = line_no
            error_info["error_column"] = col_no

            lines = code.splitlines()
            if 1 <= line_no <= len(lines):
                target_line = lines[line_no - 1]
                # Check missing closing bracket/parenthesis
                open_p = target_line.count('(') - target_line.count(')')
                open_b = target_line.count('[') - target_line.count(']')
                open_c = target_line.count('{') - target_line.count('}')

                if open_p > 0:
                    error_info["suggested_fix"] = target_line + (")" * open_p)
                    error_info["error_pointer"] = target_line + "\n" + " " * max(0, len(target_line)) + "^ Missing closing ')'"
                elif open_b > 0:
                    error_info["suggested_fix"] = target_line + ("]" * open_b)
                    error_info["error_pointer"] = target_line + "\n" + " " * max(0, len(target_line)) + "^ Missing closing ']'"
                elif open_c > 0:
                    error_info["suggested_fix"] = target_line + ("}" * open_c)
                    error_info["error_pointer"] = target_line + "\n" + " " * max(0, len(target_line)) + "^ Missing closing '}'"
                elif target_line.strip().startswith(("if", "for", "while", "def", "class", "elif", "else")) and not target_line.strip().endswith(":"):
                    error_info["suggested_fix"] = target_line + ":"
                    error_info["error_pointer"] = target_line + "\n" + " " * len(target_line) + "^ Missing colon ':' at end of statement"

        # Check NameError, IndexError, ZeroDivisionError, TypeError
        if "NameError:" in stderr:
            error_info["error_type"] = "NameError (Undefined Variable)"
            name_match = re.search(r"name '(\w+)' is not defined", stderr)
            if name_match:
                error_info["suggested_fix"] = f"Define or initialize variable '{name_match.group(1)}' before accessing it."
        elif "IndexError:" in stderr:
            error_info["error_type"] = "IndexError (Out of Bounds)"
            error_info["suggested_fix"] = "Check array/list length with len(arr) before indexing to avoid accessing out-of-range elements."
        elif "ZeroDivisionError:" in stderr:
            error_info["error_type"] = "ZeroDivisionError (Division by Zero)"
            error_info["suggested_fix"] = "Add a guard condition (e.g. `if denominator != 0:`) before performing division."
        elif "TypeError:" in stderr:
            error_info["error_type"] = "TypeError (Incompatible Types)"
        elif "RecursionError:" in stderr:
            error_info["error_type"] = "RecursionError (Maximum Stack Depth Exceeded)"
            error_info["suggested_fix"] = "Check that your recursive function has a reachable base condition."
        elif "SyntaxError:" in stderr or "IndentationError:" in stderr:
            error_info["error_type"] = "Syntax / Indentation Error"

        return error_info
