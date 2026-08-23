import shutil
import subprocess
import os
import re
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from app.engines.base import BaseLanguageEngine
from app.models import ExecutionResult, ComplexityResult, LineAnalysisItem, SecurityIssue, QualityMetric
from app.analyzers.complexity import ComplexityAnalyzer
from app.analyzers.line_analyzer import LineAnalyzer
from app.analyzers.security import SecurityScanner
from app.analyzers.quality import QualityAuditor
from app.profiler.executor import CodeExecutor

class LanguageFamily:
    COMPILED_NATIVE = "Compiled Native"
    MANAGED_VM = "Managed VM (.NET / JVM)"
    SCRIPTED_JIT = "Scripted / JIT"
    SPECIAL_PURPOSE = "Domain Specific / Special Purpose"

class UniversalLanguageAdapter(BaseLanguageEngine, ABC):
    """
    Extensible Language Adapter base class for CodePrism.
    Encapsulates toolchain discovery, execution family, compiler error parsing,
    and universal static intelligence (Big-O, security, quality, line-by-line).
    """

    def __init__(
        self,
        lang_id: str,
        display_name: str,
        family: str,
        tier: int,
        extension: str,
        toolchain_cmd: Optional[str] = None,
        icon: str = "⚡"
    ):
        self._lang_id = lang_id
        self._display_name = display_name
        self._family = family
        self._tier = tier
        self._extension = extension
        self._toolchain_cmd = toolchain_cmd
        self._icon = icon

    @property
    def language_id(self) -> str:
        return self._lang_id

    @property
    def display_name(self) -> str:
        return self._display_name

    @property
    def family(self) -> str:
        return self._family

    @property
    def tier(self) -> int:
        return self._tier

    @property
    def extension(self) -> str:
        return self._extension

    @property
    def icon(self) -> str:
        return self._icon

    def is_toolchain_installed(self) -> bool:
        if not self._toolchain_cmd:
            return False
        return shutil.which(self._toolchain_cmd) is not None

    def get_metadata(self) -> Dict[str, Any]:
        return {
            "id": self._lang_id,
            "name": self._display_name,
            "family": self._family,
            "tier": self._tier,
            "extension": self._extension,
            "icon": self._icon,
            "is_installed": self.is_toolchain_installed(),
            "toolchain_cmd": self._toolchain_cmd
        }

    def analyze_complexity(self, code: str) -> ComplexityResult:
        return ComplexityAnalyzer.analyze_generic(code, self._lang_id)

    def analyze_lines(self, code: str) -> List[LineAnalysisItem]:
        return LineAnalyzer.analyze_generic(code, self._lang_id)

    def audit_security(self, code: str) -> List[SecurityIssue]:
        return SecurityScanner.audit_generic(code, self._lang_id)

    def evaluate_quality(self, code: str) -> QualityMetric:
        return QualityAuditor.evaluate_generic(code, self._lang_id)

    def fallback_execution_notice(self, code: str) -> ExecutionResult:
        return ExecutionResult(
            status="success",
            stdout=f"[Static Analysis Mode] Toolchain '{self._toolchain_cmd}' is not detected in host environment.\n"
                   f"CodePrism completed full Static AST Inspection, Big-O Complexity Inferencing, Line-by-Line Breakdown, "
                   f"Code Quality Indexing, and Security Auditing.\n\n"
                   f"To enable native runtime execution, install '{self._toolchain_cmd}' or configure a container runner.",
            stderr="",
            exit_code=0,
            execution_time_sec=0.001,
            peak_memory_mb=5.0
        )
