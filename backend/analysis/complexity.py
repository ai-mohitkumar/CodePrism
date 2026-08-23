import ast
import re
from typing import List, Dict, Any, Tuple
from models import ComplexityResponse

class ComplexityEngine:
    """
    Static Big-O Time & Space complexity inference engine with confidence scoring.
    """

    @classmethod
    def analyze_python(cls, code: str) -> ComplexityResponse:
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return ComplexityResponse(
                time_complexity="Unknown (Syntax Error)",
                space_complexity="Unknown",
                confidence=0.0,
                reason="Could not parse AST due to syntax error.",
                details=["Fix syntax errors to calculate static Big-O complexity."]
            )

        max_loop_depth = 0
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Module)):
                depth = cls._get_max_loop_depth(node)
                if depth > max_loop_depth:
                    max_loop_depth = depth

        recursion_info = cls._detect_recursion(tree)
        has_halving = cls._detect_halving(tree)
        has_sort = cls._detect_sort(tree)
        space_comp, space_details = cls._detect_space(tree, recursion_info)

        details: List[str] = []
        confidence = 0.95

        if recursion_info["found"]:
            branches = recursion_info["branches"]
            halving = recursion_info["halving"]
            if branches >= 2 and not halving:
                time_comp = "O(2^n)"
                confidence = 0.90
                reason = f"Recursive function '{recursion_info['func_name']}' branches {branches} times per activation frame without memoization."
                details.append(reason)
            elif halving:
                if max_loop_depth >= 1:
                    time_comp = "O(n log n)"
                    confidence = 0.92
                    reason = "Divide-and-conquer algorithm with linear partition step (MergeSort / QuickSort style)."
                else:
                    time_comp = "O(log n)"
                    confidence = 0.94
                    reason = "Logarithmic divide-and-conquer reduction (Binary Search recursion)."
                details.append(reason)
            else:
                time_comp = "O(n)"
                confidence = 0.92
                reason = f"Linear recursion depth with {recursion_info['func_name']}() frames."
                details.append(reason)
        elif has_sort:
            time_comp = "O(n log n)" if max_loop_depth <= 1 else f"O(n^{max_loop_depth} log n)"
            confidence = 0.94
            reason = "Standard library comparison-based sort detected (Timsort O(n log n))."
            details.append(reason)
        elif max_loop_depth == 0:
            if has_halving:
                time_comp = "O(log n)"
                confidence = 0.90
                reason = "Variable halving/doubling progression without nested loops."
            else:
                time_comp = "O(1)"
                confidence = 0.98
                reason = "Sequential constant-time instructions with no loops or recursion."
            details.append(reason)
        elif max_loop_depth == 1:
            if has_halving:
                time_comp = "O(log n)"
                confidence = 0.94
                reason = "Single loop halving search space per iteration (Binary Search pattern)."
            else:
                time_comp = "O(n)"
                confidence = 0.96
                reason = "Single linear loop traversing input elements once."
            details.append(reason)
        elif max_loop_depth == 2:
            time_comp = "O(n²)"
            confidence = 0.92
            reason = "Two nested loops detected where the inner loop executes for each outer iteration."
            details.append(reason)
        elif max_loop_depth == 3:
            time_comp = "O(n³)"
            confidence = 0.90
            reason = "Three nested loops detected (cubic operations such as matrix multiplication)."
            details.append(reason)
        else:
            time_comp = f"O(n^{max_loop_depth})"
            confidence = 0.85
            reason = f"{max_loop_depth} levels of nested loops detected."
            details.append(reason)

        details.extend(space_details)

        return ComplexityResponse(
            time_complexity=time_comp,
            space_complexity=space_comp,
            confidence=confidence,
            reason=reason,
            nested_depth=max_loop_depth,
            has_recursion=recursion_info["found"],
            has_halving=has_halving,
            details=details
        )

    @classmethod
    def analyze_generic(cls, code: str, language: str) -> ComplexityResponse:
        lines = code.splitlines()
        max_depth = 0
        current_depth = 0
        has_halving = bool(re.search(r'(/=\s*2|>>=\s*1|mid\s*=\s*\([^)]+\)\s*/\s*2)', code))
        has_sort = bool(re.search(r'\b(sort|std::sort|qsort)\b', code))

        for line in lines:
            if re.search(r'\b(for|while)\s*\(', line):
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif '}' in line and current_depth > 0:
                current_depth -= 1

        time_comp = "O(1)"
        confidence = 0.90
        reason = "Sequential constant operations."

        if has_sort:
            time_comp = "O(n log n)"
            reason = "Standard library sort algorithm (O(n log n))."
        elif max_depth == 0:
            time_comp = "O(log n)" if has_halving else "O(1)"
            reason = "Logarithmic pattern." if has_halving else "Constant O(1) execution."
        elif max_depth == 1:
            time_comp = "O(log n)" if has_halving else "O(n)"
            reason = "Logarithmic loop." if has_halving else "Single linear loop traversal."
        elif max_depth == 2:
            time_comp = "O(n²)"
            reason = "Two nested loops detected."
        elif max_depth >= 3:
            time_comp = f"O(n^{max_depth})"
            reason = f"{max_depth} nested loops detected."

        return ComplexityResponse(
            time_complexity=time_comp,
            space_complexity="O(1)",
            confidence=confidence,
            reason=reason,
            nested_depth=max_depth,
            has_recursion=False,
            has_halving=has_halving,
            details=[reason]
        )

    @classmethod
    def _get_max_loop_depth(cls, node: ast.AST, current_depth: int = 0) -> int:
        max_d = current_depth
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.For, ast.While, ast.AsyncFor)):
                d = cls._get_max_loop_depth(child, current_depth + 1)
                max_d = max(max_d, d)
            elif isinstance(child, (ast.ListComp, ast.SetComp, ast.DictComp)):
                d = cls._get_max_loop_depth(child, current_depth + len(child.generators))
                max_d = max(max_d, d)
            else:
                d = cls._get_max_loop_depth(child, current_depth)
                max_d = max(max_d, d)
        return max_d

    @classmethod
    def _detect_recursion(cls, tree: ast.AST) -> Dict[str, Any]:
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                fname = node.name
                call_count = 0
                halving = False
                for child in ast.walk(node):
                    if isinstance(child, ast.Call) and isinstance(child.func, ast.Name) and child.func.id == fname:
                        call_count += 1
                        for a in child.args:
                            if isinstance(a, ast.BinOp) and isinstance(a.op, (ast.FloorDiv, ast.Div, ast.RShift)):
                                halving = True
                if call_count > 0:
                    return {"found": True, "func_name": fname, "branches": call_count, "halving": halving}
        return {"found": False, "func_name": "", "branches": 0, "halving": False}

    @classmethod
    def _detect_halving(cls, tree: ast.AST) -> bool:
        for node in ast.walk(tree):
            if isinstance(node, ast.While):
                for child in ast.walk(node):
                    if isinstance(child, ast.AugAssign) and isinstance(child.op, (ast.FloorDiv, ast.Div, ast.RShift)):
                        return True
                    if isinstance(child, ast.Assign):
                        for val in ast.walk(child.value):
                            if isinstance(val, ast.BinOp) and isinstance(val.op, (ast.FloorDiv, ast.Div, ast.RShift)):
                                return True
        return False

    @classmethod
    def _detect_sort(cls, tree: ast.AST) -> bool:
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in ("sorted", "heapq"):
                    return True
                if isinstance(node.func, ast.Attribute) and node.func.attr in ("sort", "heappush"):
                    return True
        return False

    @classmethod
    def _detect_space(cls, tree: ast.AST, rec_info: Dict[str, Any]) -> Tuple[str, List[str]]:
        details = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ListComp):
                for elt in ast.walk(node.elt):
                    if isinstance(elt, (ast.ListComp, ast.BinOp)):
                        details.append("Allocates 2D matrix: O(n²) space.")
                        return "O(n²)", details
                details.append("Dynamic list comprehension: O(n) space.")
                return "O(n)", details

        if rec_info["found"]:
            details.append("Recursive call stack frames: O(n) space.")
            return "O(n)", details

        details.append("In-place scalar variables: O(1) auxiliary space.")
        return "O(1)", details
