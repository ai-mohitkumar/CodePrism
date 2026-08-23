import ast
import re
import math
from typing import List, Dict, Any, Set
from app.models import QualityMetric

class QualityAuditor:
    """
    Evaluates cyclomatic complexity, maintainability index, readability score,
    and identifies code smells and anti-patterns.
    """

    @classmethod
    def evaluate_python(cls, code: str) -> QualityMetric:
        lines = code.splitlines()
        total_lines = len(lines)
        blank_lines = sum(1 for l in lines if not l.strip())
        comment_lines = sum(1 for l in lines if l.strip().startswith("#"))
        code_lines = total_lines - blank_lines - comment_lines

        cyclomatic_complexity = 1
        potential_issues: List[str] = []
        short_names: Set[str] = set()

        try:
            tree = ast.parse(code)

            # Measure decision points
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.ExceptHandler, ast.With, ast.Assert)):
                    cyclomatic_complexity += 1
                elif isinstance(node, ast.BoolOp):
                    cyclomatic_complexity += len(node.values) - 1
                elif isinstance(node, ast.IfExp):
                    cyclomatic_complexity += 1

                # Check function length and parameter count
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    num_args = len(node.args.args)
                    if num_args > 5:
                        potential_issues.append(f"Function `{node.name}` takes {num_args} arguments (consider reducing parameters or passing an object).")
                    
                    # Function length
                    func_lines = getattr(node, 'end_lineno', node.lineno) - node.lineno + 1
                    if func_lines > 40:
                        potential_issues.append(f"Function `{node.name}` is {func_lines} lines long (consider refactoring into smaller modular functions).")

                # Check variable names
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                    name = node.id
                    if len(name) == 1 and name not in ('i', 'j', 'k', 'n', 'x', 'y', 'z', '_'):
                        short_names.add(name)

            if short_names:
                potential_issues.append(f"Cryptic single-character variable names detected: {', '.join(sorted(short_names))}.")

        except SyntaxError:
            pass

        # Maintainability calculation
        # Halstead Volume approximation
        volume = max(1.0, code_lines * 5.0)
        # Standard SEI Maintainability Index formula normalized to 0-10 scale
        raw_mi = 171 - 5.2 * math.log(volume) - 0.23 * cyclomatic_complexity - 16.2 * math.log(max(1, code_lines))
        mi_score = max(1.0, min(10.0, (raw_mi / 171.0) * 10.0))

        # Readability score
        readability = 9.5
        if cyclomatic_complexity > 10:
            readability -= 2.0
        elif cyclomatic_complexity > 5:
            readability -= 1.0

        if potential_issues:
            readability -= min(2.5, len(potential_issues) * 0.8)

        if total_lines > 0 and (comment_lines / total_lines) < 0.05 and code_lines > 20:
            readability -= 0.5
            potential_issues.append("Low comment-to-code ratio. Adding docstrings improves maintainability.")

        readability = max(1.0, min(10.0, readability))

        return QualityMetric(
            maintainability_score=round(mi_score, 1),
            readability_score=round(readability, 1),
            cyclomatic_complexity=cyclomatic_complexity,
            total_lines=total_lines,
            code_lines=code_lines,
            comment_lines=comment_lines,
            potential_issues=potential_issues if potential_issues else ["None. Code structure looks clean!"]
        )

    @classmethod
    def evaluate_generic(cls, code: str, language: str) -> QualityMetric:
        lines = code.splitlines()
        total_lines = len(lines)
        blank_lines = sum(1 for l in lines if not l.strip())
        comment_lines = sum(1 for l in lines if l.strip().startswith("//") or l.strip().startswith("/*") or l.strip().startswith("*"))
        code_lines = total_lines - blank_lines - comment_lines

        # Regex decision points
        decisions = len(re.findall(r'\b(if|else\s+if|for|while|case|catch|&&|\|\|)\b', code))
        cyclomatic_complexity = 1 + decisions

        potential_issues: List[str] = []
        if cyclomatic_complexity > 10:
            potential_issues.append(f"High cyclomatic complexity ({cyclomatic_complexity}). Consider breaking complex conditionals into helper functions.")
        
        if code_lines > 100:
            potential_issues.append("File is over 100 lines of code. Consider decomposing into smaller modules.")

        volume = max(1.0, code_lines * 6.0)
        raw_mi = 171 - 5.2 * math.log(volume) - 0.23 * cyclomatic_complexity - 16.2 * math.log(max(1, code_lines))
        mi_score = max(1.0, min(10.0, (raw_mi / 171.0) * 10.0))

        readability = 9.0
        if cyclomatic_complexity > 6:
            readability -= 1.5
        if potential_issues:
            readability -= 1.0

        return QualityMetric(
            maintainability_score=round(mi_score, 1),
            readability_score=round(max(1.0, min(10.0, readability)), 1),
            cyclomatic_complexity=cyclomatic_complexity,
            total_lines=total_lines,
            code_lines=code_lines,
            comment_lines=comment_lines,
            potential_issues=potential_issues if potential_issues else ["None. Code structure looks clean!"]
        )
