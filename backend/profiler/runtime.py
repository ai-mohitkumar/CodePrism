import subprocess
import time
import sys
import os
import threading
import tempfile
import cProfile
import pstats
import io
from typing import List, Tuple, Optional
from models import FunctionTiming
from profiler.memory import monitor_process_memory

class RuntimeProfiler:
    @classmethod
    def execute_and_profile_python(cls, code: str, stdin: str = "", timeout_sec: float = 5.0):
        # Create profiling wrapper
        profiler_code = f"""
import cProfile
import pstats
import io
import sys

_profile = cProfile.Profile()
_profile.enable()

try:
{cls._indent_code(code, 4)}
finally:
    _profile.disable()
    _s = io.StringIO()
    _ps = pstats.Stats(_profile, stream=_s).sort_stats('cumtime')
    _ps.print_stats(15)
    print("___PROFILE_DATA_START___", file=sys.stderr)
    print(_s.getvalue(), file=sys.stderr)
    print("___PROFILE_DATA_END___", file=sys.stderr)
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(profiler_code)
            temp_path = f.name

        start_time = time.perf_counter()
        functions: List[FunctionTiming] = []
        stdout = ""
        stderr = ""
        exit_code = 0
        peak_mb = 5.2
        cpu_percent = 21.0

        try:
            proc = subprocess.Popen(
                [sys.executable, temp_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace"
            )

            stop_event = threading.Event()
            mem_result = [5.2, 18.0]

            def track():
                mb, cpu = monitor_process_memory(proc.pid, stop_event)
                mem_result[0] = mb
                mem_result[1] = cpu

            t = threading.Thread(target=track, daemon=True)
            t.start()

            try:
                stdout, raw_stderr = proc.communicate(input=stdin, timeout=timeout_sec)
                exit_code = proc.returncode
            except subprocess.TimeoutExpired:
                proc.kill()
                stdout, raw_stderr = proc.communicate()
                exit_code = -1
                raw_stderr += f"\n[TimeoutError] Exceeded {timeout_sec}s execution limit."
            finally:
                stop_event.set()
                t.join(timeout=0.1)

            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            peak_mb = round(mem_result[0], 2)
            cpu_percent = round(mem_result[1], 1)

            # Parse profile data from stderr
            if "___PROFILE_DATA_START___" in raw_stderr and "___PROFILE_DATA_END___" in raw_stderr:
                parts = raw_stderr.split("___PROFILE_DATA_START___")
                clean_err = parts[0].strip()
                prof_data = parts[1].split("___PROFILE_DATA_END___")[0].strip()
                rest_err = parts[1].split("___PROFILE_DATA_END___")[1].strip()
                stderr = (clean_err + "\n" + rest_err).strip()

                functions = cls._parse_pstats(prof_data)
            else:
                stderr = raw_stderr.strip()

            return exit_code, stdout, stderr, elapsed_ms, peak_mb, cpu_percent, functions

        finally:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass

    @classmethod
    def execute_generic(cls, cmd: list, cwd: Optional[str] = None, stdin: str = "", timeout_sec: float = 5.0):
        start_time = time.perf_counter()
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

            stop_event = threading.Event()
            mem_result = [5.5, 20.0]

            def track():
                mb, cpu = monitor_process_memory(proc.pid, stop_event)
                mem_result[0] = mb
                mem_result[1] = cpu

            t = threading.Thread(target=track, daemon=True)
            t.start()

            try:
                stdout, stderr = proc.communicate(input=stdin, timeout=timeout_sec)
                exit_code = proc.returncode
            except subprocess.TimeoutExpired:
                proc.kill()
                stdout, stderr = proc.communicate()
                exit_code = -1
                stderr += f"\n[TimeoutError] Exceeded {timeout_sec}s execution limit."
            finally:
                stop_event.set()
                t.join(timeout=0.1)

            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return exit_code, stdout, stderr, elapsed_ms, round(mem_result[0], 2), round(mem_result[1], 1)
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return -1, "", str(e), elapsed_ms, 5.0, 0.0

    @classmethod
    def _indent_code(cls, code: str, spaces: int = 4) -> str:
        pad = " " * spaces
        return "\n".join(pad + line if line.strip() else line for line in code.splitlines())

    @classmethod
    def _parse_pstats(cls, text: str) -> List[FunctionTiming]:
        results: List[FunctionTiming] = []
        lines = text.splitlines()
        found_header = False

        for line in lines:
            if "ncalls" in line and "cumtime" in line:
                found_header = True
                continue
            if found_header and line.strip():
                parts = line.split()
                if len(parts) >= 6:
                    ncalls = parts[0].split("/")[0]
                    cumtime = parts[3]
                    percall = parts[4]
                    fname = " ".join(parts[5:])
                    # Filter internal python frames
                    if not fname.startswith("{built-in method exec}") and not "cProfile" in fname:
                        try:
                            # Shorten fname to function name
                            short_name = fname
                            if "(" in fname and ")" in fname:
                                short_name = fname.split(":")[-1].strip()
                            elif "<" in fname:
                                short_name = fname
                            
                            results.append(FunctionTiming(
                                function_name=short_name,
                                cumtime_ms=round(float(cumtime) * 1000.0, 2),
                                percall_ms=round(float(percall) * 1000.0, 2),
                                call_count=int(ncalls)
                            ))
                        except ValueError:
                            pass
        return results[:8]
