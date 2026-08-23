import ast
import re
from typing import List, Dict, Any
from app.models import LineAnalysisItem

class LineAnalyzer:
    """
    Analyzes code line-by-line to categorize statement types, Big-O contribution, and syntax health.
    """

    @classmethod
    def analyze_python(cls, code: str) -> List[LineAnalysisItem]:
        lines = code.splitlines()
        results: List[LineAnalysisItem] = []
        if not lines:
            return results

        # Attempt to parse AST for deep node mapping
        ast_map: Dict[int, List[ast.AST]] = {}
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if hasattr(node, "lineno"):
                    ast_map.setdefault(node.lineno, []).append(node)
        except SyntaxError:
            pass

        for i, line_text in enumerate(lines, start=1):
            stripped = line_text.strip()
            if not stripped:
                results.append(LineAnalysisItem(
                    line_number=i,
                    content=line_text,
                    classification="Empty line",
                    complexity_impact="—",
                    status="ok",
                    notes=""
                ))
                continue

            if stripped.startswith("#"):
                results.append(LineAnalysisItem(
                    line_number=i,
                    content=line_text,
                    classification="Comment",
                    complexity_impact="—",
                    status="ok",
                    notes=""
                ))
                continue

            nodes = ast_map.get(i, [])
            classification = "Statement"
            impact = "O(1)"
            status = "ok"
            notes = ""

            # Check node types
            node_types = [type(n) for n in nodes]
            if ast.FunctionDef in node_types or ast.AsyncFunctionDef in node_types:
                classification = "Function declaration"
                impact = "O(1)"
                notes = "Defines function entrypoint"
            elif ast.ClassDef in node_types:
                classification = "Class declaration"
                impact = "O(1)"
            elif ast.For in node_types or ast.While in node_types or ast.AsyncFor in node_types:
                classification = "Loop header"
                impact = "O(n)"
                status = "warning"
                notes = "Iterative loop construct"
            elif ast.Return in node_types:
                classification = "Return statement"
                impact = "O(1)"
                notes = "Exits function with return value"
            elif ast.If in node_types:
                classification = "Conditional branch"
                impact = "O(1)"
                notes = "Evaluates boolean expression"
            elif ast.Import in node_types or ast.ImportFrom in node_types:
                classification = "Module import"
                impact = "O(1)"
            elif ast.Assign in node_types or ast.AugAssign in node_types:
                if any(isinstance(n, ast.Subscript) for n in nodes):
                    classification = "Array/Dict access & assignment"
                    impact = "O(1)"
                elif any(isinstance(n, (ast.ListComp, ast.SetComp, ast.DictComp)) for n in nodes):
                    classification = "Comprehension & memory allocation"
                    impact = "O(n)"
                    status = "warning"
                    notes = "Allocates new collection"
                else:
                    classification = "Variable assignment"
                    impact = "O(1)"
            elif ast.Expr in node_types:
                if any(isinstance(n, ast.Call) for n in nodes):
                    if "print" in stripped:
                        classification = "I/O Output (print)"
                        impact = "O(1)"
                    else:
                        classification = "Function / method call"
                        impact = "O(1)"

            # Regex heuristics fallback if AST didn't tag
            if classification == "Statement":
                if re.match(r'^\s*def\s+', line_text):
                    classification = "Function declaration"
                elif re.match(r'^\s*class\s+', line_text):
                    classification = "Class definition"
                elif re.match(r'^\s*(for|while)\s+', line_text):
                    classification = "Loop header"
                    impact = "O(n)"
                    status = "warning"
                elif re.match(r'^\s*if\s+|^\s*elif\s+|^\s*else:', line_text):
                    classification = "Conditional check"
                elif re.match(r'^\s*return\b', line_text):
                    classification = "Return statement"
                elif re.match(r'^\s*print\s*\(', line_text):
                    classification = "I/O Print statement"
                elif '=' in line_text:
                    classification = "Assignment / Initialization"

            results.append(LineAnalysisItem(
                line_number=i,
                content=line_text,
                classification=classification,
                complexity_impact=impact,
                status=status,
                notes=notes
            ))

        return results

    @classmethod
    def analyze_generic(cls, code: str, language: str) -> List[LineAnalysisItem]:
        lines = code.splitlines()
        results: List[LineAnalysisItem] = []
        for i, line_text in enumerate(lines, start=1):
            stripped = line_text.strip()
            if not stripped:
                results.append(LineAnalysisItem(
                    line_number=i,
                    content=line_text,
                    classification="Empty line",
                    complexity_impact="—",
                    status="ok"
                ))
                continue

            if stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("*"):
                results.append(LineAnalysisItem(
                    line_number=i,
                    content=line_text,
                    classification="Comment",
                    complexity_impact="—",
                    status="ok"
                ))
                continue

            classification = "Statement"
            impact = "O(1)"
            status = "ok"
            notes = ""

            if re.search(r'^\s*#include\b|^\s*import\b|^\s*using\s+namespace\b|^\s*package\b', line_text):
                classification = "Import / Header include"
            elif re.search(r'\b(for|while)\s*\(', stripped):
                classification = "Loop construct"
                impact = "O(n)"
                status = "warning"
                notes = "Iterative block"
            elif re.search(r'\b(if|else if|else|switch|case)\b', stripped):
                classification = "Conditional branch"
            elif re.search(r'\breturn\b', stripped):
                classification = "Return statement"
            elif re.search(r'\b(std::cout|printf|puts|System\.out\.print|console\.log)\b', stripped):
                classification = "I/O Output"
            elif re.search(r'\b(class|struct|interface|enum)\b', stripped):
                classification = "Type definition"
            elif re.search(r'\b(vector<|new\s+\w+|malloc\(|ArrayList)', stripped):
                classification = "Heap memory allocation"
                impact = "O(n)"
                status = "warning"
                notes = "Dynamic memory allocation"
            elif '=' in stripped:
                classification = "Variable assignment / update"
            elif re.search(r'\b(int|double|float|char|bool|auto|let|const|var)\s+\w+\s*\(', stripped):
                classification = "Function signature"

            results.append(LineAnalysisItem(
                line_number=i,
                content=line_text,
                classification=classification,
                complexity_impact=impact,
                status=status,
                notes=notes
            ))

        return results
