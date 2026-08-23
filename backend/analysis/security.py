import ast
import re
from typing import List
from models import SecurityIssue

class SecurityAuditor:
    @classmethod
    def audit_python(cls, code: str) -> List[SecurityIssue]:
        issues: List[SecurityIssue] = []

        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                lineno = getattr(node, "lineno", None)

                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ("eval", "exec"):
                            issues.append(SecurityIssue(
                                severity="Critical",
                                line=lineno,
                                title=f"Arbitrary Code Execution via `{node.func.id}()`",
                                description="Dangerous dynamic evaluation of untrusted input allows Remote Code Execution (RCE).",
                                suggestion="Use safe parsing like `ast.literal_eval()` or structured `json.loads()`."
                            ))
                        elif node.func.id in ("compile", "__import__"):
                            issues.append(SecurityIssue(
                                severity="High",
                                line=lineno,
                                title=f"Dynamic Module Loading via `{node.func.id}()`",
                                description="Dynamically loading arbitrary modules can allow unauthorized capability escalation.",
                                suggestion="Use static imports."
                            ))

                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    mod_name = node.module if isinstance(node, ast.ImportFrom) else (node.names[0].name if node.names else "")
                    if mod_name in ("subprocess", "os", "posix", "nt"):
                        issues.append(SecurityIssue(
                            severity="Medium",
                            line=lineno,
                            title=f"OS Command Execution Module `{mod_name}`",
                            description="Unsanitized commands passed to OS processes create command injection risks.",
                            suggestion="Ensure strict input sanitization or avoid spawning shell commands."
                        ))
                    elif mod_name in ("pickle", "shelve"):
                        issues.append(SecurityIssue(
                            severity="High",
                            line=lineno,
                            title="Unsafe Deserialization via `pickle`",
                            description="`pickle` can execute arbitrary code during unpickling.",
                            suggestion="Use JSON or Protocol Buffers."
                        ))
        except SyntaxError:
            pass

        # Regex credentials scan
        for idx, line in enumerate(code.splitlines(), start=1):
            if re.search(r'(api_key|password|secret|token|private_key)\s*[:=]\s*["\'][A-Za-z0-9_\-]{8,}["\']', line, re.IGNORECASE):
                issues.append(SecurityIssue(
                    severity="High",
                    line=idx,
                    title="Hardcoded API Credential / Secret Detected",
                    description="Plaintext secret found in source code. Can be leaked to public repositories.",
                    suggestion="Move credentials to environment variables or secret vaults."
                ))

        return issues

    @classmethod
    def audit_generic(cls, code: str, language: str) -> List[SecurityIssue]:
        issues: List[SecurityIssue] = []
        for idx, line in enumerate(code.splitlines(), start=1):
            if language == "cpp":
                if re.search(r'\bgets\s*\(', line):
                    issues.append(SecurityIssue(
                        severity="Critical",
                        line=idx,
                        title="Unsafe Function `gets()` (Buffer Overflow)",
                        description="`gets()` lacks buffer bounds checking, leading to stack corruption.",
                        suggestion="Use `fgets()` or `std::getline()`."
                    ))
                if re.search(r'\bsystem\s*\(', line):
                    issues.append(SecurityIssue(
                        severity="High",
                        line=idx,
                        title="Command Execution via `system()`",
                        description="Shell injection risk if user inputs are concatenated.",
                        suggestion="Use parameterized process APIs."
                    ))
            elif language in ("javascript", "typescript", "js", "ts"):
                if re.search(r'\beval\s*\(', line):
                    issues.append(SecurityIssue(
                        severity="Critical",
                        line=idx,
                        title="Dangerous `eval()` Usage",
                        description="Arbitrary JS code execution.",
                        suggestion="Refactor using standard property access or JSON parsing."
                    ))

        return issues
