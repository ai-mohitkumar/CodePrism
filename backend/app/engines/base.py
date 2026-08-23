from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from app.models import ExecutionResult, ComplexityResult, LineAnalysisItem, SecurityIssue, QualityMetric

class BaseLanguageEngine(ABC):
    @property
    @abstractmethod
    def language_id(self) -> str:
        """Returns the unique identifier for the language, e.g. 'python', 'cpp'."""
        pass

    @abstractmethod
    def execute(self, code: str, stdin: str = "", timeout_sec: float = 5.0) -> ExecutionResult:
        """Executes code in a controlled subprocess and returns detailed runtime stats."""
        pass

    @abstractmethod
    def analyze_complexity(self, code: str) -> ComplexityResult:
        """Statically infers Big-O Time and Space complexity."""
        pass

    @abstractmethod
    def analyze_lines(self, code: str) -> List[LineAnalysisItem]:
        """Provides a line-by-line semantic breakdown."""
        pass

    @abstractmethod
    def audit_security(self, code: str) -> List[SecurityIssue]:
        """Scans code for security vulnerabilities and safety hazards."""
        pass

    @abstractmethod
    def evaluate_quality(self, code: str) -> QualityMetric:
        """Computes cyclomatic complexity, maintainability, and code smells."""
        pass
