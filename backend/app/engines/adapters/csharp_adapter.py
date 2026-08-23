import tempfile
import os
import re
from app.engines.adapters.base_adapter import UniversalLanguageAdapter, LanguageFamily
from app.models import ExecutionResult
from app.profiler.executor import CodeExecutor

class CSharpAdapter(UniversalLanguageAdapter):
    def __init__(self):
        super().__init__(
            lang_id="csharp",
            display_name="C# (.NET 9)",
            family=LanguageFamily.MANAGED_VM,
            tier=1,
            extension="cs",
            toolchain_cmd="dotnet",
            icon="🔷"
        )

    def execute(self, code: str, stdin: str = "", timeout_sec: float = 8.0) -> ExecutionResult:
        if not self.is_toolchain_installed():
            return self.fallback_execution_notice(code)

        # Wrap in Program if class / namespace missing
        if "class " not in code:
            code = f"""using System;
using System.Collections.Generic;

public class Program {{
    public static void Main(string[] args) {{
        {code}
    }}
}}"""

        with tempfile.TemporaryDirectory() as temp_dir:
            proj_file = os.path.join(temp_dir, "App.csproj")
            src_file = os.path.join(temp_dir, "Program.cs")

            with open(proj_file, "w", encoding="utf-8") as f:
                f.write("""<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net9.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
  </PropertyGroup>
</Project>""")

            with open(src_file, "w", encoding="utf-8") as f:
                f.write(code)

            # Run with dotnet run
            r_exit, r_out, r_err, r_time, r_ram = CodeExecutor.execute_command(
                ["dotnet", "run", "--no-restore"],
                cwd=temp_dir,
                stdin_text=stdin,
                timeout_sec=timeout_sec
            )

            status = "success"
            line_no = None
            err_msg = r_err or r_out

            if r_exit != 0:
                status = "compilation_error" if "error CS" in err_msg else "runtime_error"
                match = re.search(r'Program\.cs\((\d+),(\d+)\):\s*error\s+(CS\d+):\s*(.*)', err_msg)
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
                error_type="C# Compilation Error" if status == "compilation_error" else None,
                error_message=err_msg.strip() if r_exit != 0 else None
            )
