import ast
import re
from typing import List
from app.models import SecurityIssue

class SecurityScanner:
    """
    Scans source code for dangerous vulnerabilities, unsafe system calls, and security anti-patterns.
    """

    @classmethod
    def audit_python(cls, code: str) -> List[SecurityIssue]:
        issues: List[SecurityIssue] = []

        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                lineno = getattr(node, "lineno", None)

                # Check dangerous calls: eval, exec, compile
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ("eval", "exec"):
                            issues.append(SecurityIssue(
                                severity="Critical",
                                line=lineno,
                                title=f"Arbitrary Code Execution via `{node.func.id}()`",
                                description=f"Using `{node.func.id}()` with untrusted input allows attackers to execute arbitrary code on the host system.",
                                suggestion="Replace dynamic code execution with structured parsing (e.g. `ast.literal_eval()`, `json.loads()`)."
                            ))
                        elif node.func.id in ("compile", "__import__"):
                            issues.append(SecurityIssue(
                                severity="High",
                                line=lineno,
                                title=f"Dynamic Module / Code Loading via `{node.func.id}()`",
                                description="Dynamically importing modules or compiling bytecode at runtime introduces code injection risks.",
                                suggestion="Use static imports and predefined registries."
                            ))

                # Check dangerous imports
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    names = []
                    if isinstance(node, ast.Import):
                        names = [alias.name for alias in node.names]
                    elif node.module:
                        names = [node.module]

                    for name in names:
                        if name in ("os", "subprocess", "posix", "nt"):
                            issues.append(SecurityIssue(
                                severity="Medium",
                                line=lineno,
                                title=f"System Process Access via `{name}`",
                                description=f"Importing `{name}` allows process spawning and OS command execution. Ensure commands are sanitized.",
                                suggestion="Avoid passing unsanitized shell commands or use restricted sandboxed APIs."
                            ))
                        elif name in ("pickle", "shelve"):
                            issues.append(SecurityIssue(
                                severity="High",
                                line=lineno,
                                title=f"Insecure Deserialization via `{name}`",
                                description="Python's `pickle` library is inherently insecure against untrusted payloads.",
                                suggestion="Use safe serialization formats such as JSON or Protocol Buffers."
                            ))

        except SyntaxError:
            pass

        # Text-based checks for hardcoded credentials
        lines = code.splitlines()
        for idx, line in enumerate(lines, start=1):
            if re.search(r'(api_key|password|secret|token|private_key)\s*=\s*["\'][A-Za-z0-9_\-]{8,}["\']', line, re.IGNORECASE):
                issues.append(SecurityIssue(
                    severity="High",
                    line=idx,
                    title="Hardcoded Credential / Secret Detected",
                    description="Plaintext API tokens or passwords in source code can be leaked into public repositories.",
                    suggestion="Extract secrets to environment variables or a secure key management vault."
                ))

        return issues

    @classmethod
    def audit_generic(cls, code: str, language: str) -> List[SecurityIssue]:
        issues: List[SecurityIssue] = []
        lines = code.splitlines()

        for idx, line in enumerate(lines, start=1):
            # C/C++ checks
            if language in ("cpp", "c"):
                if re.search(r'\bgets\s*\(', line):
                    issues.append(SecurityIssue(
                        severity="Critical",
                        line=idx,
                        title="Unsafe Function `gets()` (Buffer Overflow Vulnerability)",
                        description="`gets()` does not perform bounds checking and is susceptible to stack buffer overflows.",
                        suggestion="Use `fgets()` or `std::getline()` with strict buffer limits."
                    ))
                if re.search(r'\b(strcpy|strcat|sprintf)\s*\(', line):
                    issues.append(SecurityIssue(
                        severity="Medium",
                        line=idx,
                        title="Unbounded String Copy Function",
                        description="Functions like `strcpy` and `sprintf` can cause memory buffer overflows if inputs exceed allocated capacity.",
                        suggestion="Use bounded equivalents like `strncpy`, `snprintf`, or `std::string`."
                    ))
                if re.search(r'\bsystem\s*\(', line):
                    issues.append(SecurityIssue(
                        severity="High",
                        line=idx,
                        title="Command Execution via `system()`",
                        description="Direct invocation of the system shell can allow command injection.",
                        suggestion="Avoid invoking shell commands or validate and sanitize all command arguments."
                    ))

            # Java checks
            if language == "java":
                if re.search(r'Runtime\.getRuntime\(\)\.exec|ProcessBuilder', line):
                    issues.append(SecurityIssue(
                        severity="High",
                        line=idx,
                        title="Process Execution in Java",
                        description="Launching external OS processes requires rigorous input validation to prevent command injection.",
                        suggestion="Validate arguments or avoid external process invocation."
                    ))

            # JavaScript checks
            if language in ("javascript", "js"):
                if re.search(r'\beval\s*\(', line):
                    issues.append(SecurityIssue(
                        severity="Critical",
                        line=idx,
                        title="Dangerous `eval()` Usage",
                        description="`eval()` evaluates arbitrary strings as JavaScript in the caller's scope.",
                        suggestion="Refactor using standard object property lookups or `JSON.parse()`."
                    ))
                if re.search(r'\bchild_process\b', line):
                    issues.append(SecurityIssue(
                        severity="High",
                        line=idx,
                        title="Process Spawning via `child_process`",
                        description="Arbitrary shell execution hazard.",
                        suggestion="Restrict arguments and use `execFile` without shell interpolation."
                    ))

            # Generic secrets check
            if re.search(r'(api_key|password|secret|token|private_key)\s*[:=]\s*["\'][A-Za-z0-9_\-]{8,}["\']', line, re.IGNORECASE):
                issues.append(SecurityIssue(
                    severity="High",
                    line=idx,
                    title="Hardcoded Credential / Secret Detected",
                    description="Plaintext credentials found in source code.",
                    suggestion="Store credentials in environment variables."
                ))

        return issues
