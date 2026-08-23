import ast
import math
import re
from typing import List
from models import QualityResponse

class QualityEngine:
    @classmethod
    def evaluate_python(cls, code: str) -> QualityResponse:
        lines = code.splitlines()
        total_lines = len(lines)
        blank_lines = sum(1 for l in lines if not l.strip())
        comment_lines = sum(1 for l in lines if l.strip().startswith("#"))
        code_lines = total_lines - blank_lines - comment_lines

        cyclomatic = 1
        issues: List[str] = []

        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler, ast.With, ast.Assert)):
                    cyclomatic += 1
                elif isinstance(node, ast.BoolOp):
                    cyclomatic += len(node.values) - 1

                if isinstance(node, ast.FunctionDef):
                    if len(node.args.args) > 4:
                        issues.append(f"Function `{node.name}` takes {len(node.args.args)} arguments (consider reducing parameters).")
                    
                    fn_lines = getattr(node, 'end_lineno', node.lineno) - node.lineno + 1
                    if fn_lines > 35:
                        issues.append(f"Function `{node.name}` is {fn_lines} lines long (consider modularizing).")

        except SyntaxError:
            pass

        # Maintainability index
        volume = max(1.0, code_lines * 5.5)
        raw_mi = 171 - 5.2 * math.log(volume) - 0.23 * cyclomatic - 16.2 * math.log(max(1, code_lines))
        mi_score = max(1.0, min(10.0, (raw_mi / 171.0) * 10.0))

        readability = 9.5
        if cyclomatic > 6:
            readability -= 1.5
        if issues:
            readability -= min(2.0, len(issues) * 0.7)

        return QualityResponse(
            maintainability_score=round(mi_score, 1),
            readability_score=round(max(1.0, min(10.0, readability)), 1),
            cyclomatic_complexity=cyclomatic,
            total_lines=total_lines,
            code_lines=code_lines,
            comment_lines=comment_lines,
            issues=issues if issues else ["Code structure is clean and modular."]
        )

    @classmethod
    def evaluate_generic(cls, code: str, language: str) -> QualityResponse:
        lines = code.splitlines()
        total_lines = len(lines)
        blank_lines = sum(1 for l in lines if not l.strip())
        comment_lines = sum(1 for l in lines if l.strip().startswith("//") or l.strip().startswith("/*") or l.strip().startswith("*"))
        code_lines = total_lines - blank_lines - comment_lines

        decisions = len(re.findall(r'\b(if|else\s+if|for|while|case|catch|&&|\|\|)\b', code))
        cyclomatic = 1 + decisions

        volume = max(1.0, code_lines * 6.0)
        raw_mi = 171 - 5.2 * math.log(volume) - 0.23 * cyclomatic - 16.2 * math.log(max(1, code_lines))
        mi_score = max(1.0, min(10.0, (raw_mi / 171.0) * 10.0))

        return QualityResponse(
            maintainability_score=round(mi_score, 1),
            readability_score=8.5,
            cyclomatic_complexity=cyclomatic,
            total_lines=total_lines,
            code_lines=code_lines,
            comment_lines=comment_lines,
            issues=["Code structure looks good."]
        )
