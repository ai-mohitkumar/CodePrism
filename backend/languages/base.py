from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
import shutil
import os
import time
from models import (
    LanguageTier, LanguageFamily, UniversalResult,
    StandardCompileResult, StandardExecutionResult,
    StandardComplexityResult, StandardQualityResult,
    StandardSecurityResult, ASTResponse, CompileResponse, CompilerDiagnostic
)
from analysis.complexity import ComplexityEngine
from analysis.security import SecurityAuditor
from analysis.quality import QualityEngine
from sandbox.executor import SecureSandboxExecutor

class BaseLanguageAdapter(ABC):
    def __init__(
        self,
        lang_id: str,
        name: str,
        tier: LanguageTier,
        family: LanguageFamily,
        extension: str,
        icon: str,
        toolchain_cmd: Optional[str] = None
    ):
        self.lang_id = lang_id
        self.name = name
        self.tier = tier
        self.family = family
        self.extension = extension
        self.icon = icon
        self.toolchain_cmd = toolchain_cmd

    def is_installed(self) -> bool:
        if not self.toolchain_cmd:
            return True
        return shutil.which(self.toolchain_cmd) is not None

    def get_version(self) -> str:
        if self.is_installed():
            return f"{self.name} (Native Toolchain)"
        return f"{self.name} (Sandboxed Static Engine)"

    def compile(self, code: str) -> StandardCompileResult:
        """Default compile step."""
        return StandardCompileResult(success=True)

    def compile_detailed(self, code: str, flags: Optional[List[str]] = None) -> CompileResponse:
        """Detailed compiler pipeline returning artifact information and diagnostics."""
        start_time = time.perf_counter()
        std_res = self.compile(code)
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        diagnostics: List[CompilerDiagnostic] = []
        if not std_res.success:
            diagnostics.append(CompilerDiagnostic(
                severity="error",
                line=std_res.error_line,
                column=std_res.error_column,
                message=std_res.compiler_output,
                pointer=std_res.error_pointer,
                suggested_fix=std_res.suggested_fix
            ))

        artifact_type = "Script / Interpreted"
        target_art = f"module.{self.extension}"
        if self.family == LanguageFamily.NATIVE:
            artifact_type = "Native Binary (x86_64 Executable)"
            target_art = "output.exe"
        elif self.family == LanguageFamily.MANAGED_VM:
            artifact_type = "JVM / Managed Bytecode (.class / .dll)"
            target_art = "output.class"

        return CompileResponse(
            success=std_res.success,
            compiler_name=self.get_version(),
            target_artifact=target_art if std_res.success else None,
            artifact_type=artifact_type,
            compilation_time_ms=round(elapsed_ms, 2),
            errors_count=len(std_res.errors) if not std_res.success else 0,
            warnings_count=len(std_res.warnings),
            raw_output=std_res.compiler_output,
            diagnostics=diagnostics,
            ir_bytecode=None
        )

    @abstractmethod
    def execute(self, code: str, stdin: str = "", timeout_sec: float = 5.0) -> StandardExecutionResult:
        """Executes source code in the secure sandbox."""
        pass

    def parse_ast(self, code: str) -> Optional[ASTResponse]:
        """Parses AST if available."""
        return None

    def analyze_complexity(self, code: str) -> StandardComplexityResult:
        comp = ComplexityEngine.analyze_generic(code, self.lang_id)
        return StandardComplexityResult(
            time=comp.time_complexity,
            space=comp.space_complexity,
            confidence=comp.confidence,
            reason=comp.reason,
            nested_depth=comp.nested_depth,
            has_recursion=comp.has_recursion,
            has_halving=comp.has_halving,
            details=comp.details
        )

    def audit_security(self, code: str) -> StandardSecurityResult:
        issues = SecurityAuditor.audit_generic(code, self.lang_id)
        crit = sum(1 for i in issues if i.severity.lower() == 'critical')
        high = sum(1 for i in issues if i.severity.lower() == 'high')
        med = sum(1 for i in issues if i.severity.lower() == 'medium')
        low = sum(1 for i in issues if i.severity.lower() == 'low')
        return StandardSecurityResult(
            critical=crit,
            high=high,
            medium=med,
            low=low,
            issues=issues
        )

    def evaluate_quality(self, code: str) -> StandardQualityResult:
        q = QualityEngine.evaluate_generic(code, self.lang_id)
        return StandardQualityResult(
            score=round(q.maintainability_score * 10, 1),
            maintainability=q.maintainability_score,
            readability=q.readability_score,
            cyclomatic=q.cyclomatic_complexity,
            total_lines=q.total_lines,
            code_lines=q.code_lines,
            comment_lines=q.comment_lines,
            issues=q.issues
        )

    def run_full_analysis(self, code: str, stdin: str = "", timeout_sec: float = 5.0, filename: Optional[str] = None) -> UniversalResult:
        """Universal execution and analysis pipeline returning the standard format."""
        # 1. Compile
        compile_res = self.compile(code)
        
        # 2. Execute
        if not compile_res.success:
            exec_res = StandardExecutionResult(
                status="compilation_error",
                exit_code=1,
                stderr=compile_res.compiler_output or "Compilation error",
                runtime_ms=0.0,
                memory_mb=0.0
            )
        else:
            exec_res = self.execute(code, stdin=stdin, timeout_sec=timeout_sec)

        # 3. AST
        ast_res = self.parse_ast(code)

        # 4. Complexity
        complexity_res = self.analyze_complexity(code)

        # 5. Security & Quality
        security_res = self.audit_security(code)
        quality_res = self.evaluate_quality(code)

        overall_status = exec_res.status
        if not compile_res.success:
            overall_status = "compilation_error"

        return UniversalResult(
            language=self.lang_id,
            version=self.get_version(),
            status=overall_status,
            filename=filename or f"solution.{self.extension}",
            compile=compile_res,
            execution=exec_res,
            ast=ast_res,
            complexity=complexity_res,
            quality=quality_res,
            security=security_res
        )
