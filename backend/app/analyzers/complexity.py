import ast
import re
from typing import List, Dict, Any, Tuple, Optional
from app.models import ComplexityResult

class ComplexityAnalyzer:
    """
    Intelligent Static Complexity Engine.
    Performs AST analysis for Python and robust AST-like pattern parsing for other languages
    to mathematically estimate Big-O Time & Space complexity with natural language explanations.
    """

    @classmethod
    def analyze_python_ast(cls, code: str) -> ComplexityResult:
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return ComplexityResult(
                time_complexity="Unknown (Syntax Error)",
                space_complexity="Unknown (Syntax Error)",
                confidence=0.0,
                explanation="Could not parse AST due to syntax error in the code.",
                details=["Fix syntax errors to compute static Big-O complexity."]
            )

        max_loop_depth = 0
        recursion_info = cls._detect_python_recursion(tree)
        has_halving = cls._detect_python_halving(tree)
        has_sort = cls._detect_python_sorting(tree)
        space_complexity, space_details = cls._detect_python_space(tree, recursion_info)

        # Walk AST to find loop nesting
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Module)):
                depth = cls._get_max_loop_depth(node)
                if depth > max_loop_depth:
                    max_loop_depth = depth

        # Determine Big-O Time
        time_comp = "O(1)"
        confidence = 0.95
        details = []

        if recursion_info["found"]:
            rec_branches = recursion_info["branches"]
            rec_halving = recursion_info["halving"]
            if rec_branches >= 2 and not rec_halving:
                time_comp = "O(2^n)"
                confidence = 0.90
                details.append(f"Recursive branching detected: function calls itself {rec_branches} times per frame (e.g. naive Fibonacci/Tree exploration).")
            elif rec_halving:
                if max_loop_depth >= 1:
                    time_comp = "O(n log n)"
                    confidence = 0.88
                    details.append("Divide-and-conquer pattern with linear combination step detected (MergeSort / QuickSort style).")
                else:
                    time_comp = "O(log n)"
                    confidence = 0.92
                    details.append("Divide-and-conquer logarithmic reduction (Binary Search recursion).")
            else:
                if max_loop_depth >= 1:
                    time_comp = "O(n^2)"
                    confidence = 0.85
                    details.append("Linear recursive depth with inner loop iterations per frame.")
                else:
                    time_comp = "O(n)"
                    confidence = 0.92
                    details.append("Linear recursion depth (O(n) recursive stack frames).")
        elif has_sort:
            if max_loop_depth >= 1:
                time_comp = "O(n log n)" if max_loop_depth == 1 else f"O(n^{max_loop_depth} log n)"
                confidence = 0.90
                details.append("Sorting operations combined with loop iteration detected.")
            else:
                time_comp = "O(n log n)"
                confidence = 0.94
                details.append("Direct comparison-based sorting operation detected (Timsort/Dual-Pivot QuickSort O(n log n)).")
        elif max_loop_depth == 0:
            if has_halving:
                time_comp = "O(log n)"
                confidence = 0.90
                details.append("Loop with logarithmic state progression (halving/doubling step).")
            else:
                time_comp = "O(1)"
                confidence = 0.98
                details.append("Sequential constant-time instructions with no unbounded loops or recursions.")
        elif max_loop_depth == 1:
            if has_halving:
                time_comp = "O(log n)"
                confidence = 0.92
                details.append("Single loop halving search space per iteration (e.g., Binary Search).")
            else:
                time_comp = "O(n)"
                confidence = 0.95
                details.append("Single linear loop traversing input elements.")
        elif max_loop_depth == 2:
            time_comp = "O(n^2)"
            confidence = 0.92
            details.append("Nested loop structure (2 levels of nested iteration detected).")
        elif max_loop_depth == 3:
            time_comp = "O(n^3)"
            confidence = 0.90
            details.append("Triple nested loop structure (3 levels of nested iteration detected).")
        else:
            time_comp = f"O(n^{max_loop_depth})"
            confidence = 0.85
            details.append(f"{max_loop_depth} levels of nested loops detected.")

        explanation = cls._generate_explanation(time_comp, space_complexity, max_loop_depth, recursion_info, has_halving)
        details.extend(space_details)

        return ComplexityResult(
            time_complexity=time_comp,
            space_complexity=space_complexity,
            confidence=confidence,
            explanation=explanation,
            nested_depth=max_loop_depth,
            recursion_found=recursion_info["found"],
            has_halving=has_halving,
            details=details
        )

    @classmethod
    def _get_max_loop_depth(cls, node: ast.AST, current_depth: int = 0) -> int:
        max_d = current_depth
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.For, ast.While, ast.AsyncFor)):
                child_d = cls._get_max_loop_depth(child, current_depth + 1)
                max_d = max(max_d, child_d)
            elif isinstance(child, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
                comp_depth = len(child.generators)
                child_d = cls._get_max_loop_depth(child, current_depth + comp_depth)
                max_d = max(max_d, child_d)
            else:
                child_d = cls._get_max_loop_depth(child, current_depth)
                max_d = max(max_d, child_d)
        return max_d

    @classmethod
    def _detect_python_recursion(cls, tree: ast.AST) -> Dict[str, Any]:
        info = {"found": False, "func_name": "", "branches": 0, "halving": False}
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                fname = node.name
                call_count = 0
                halving = False
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Name) and child.func.id == fname:
                            call_count += 1
                            for arg in child.args:
                                if isinstance(arg, ast.BinOp) and isinstance(arg.op, (ast.FloorDiv, ast.Div, ast.RShift)):
                                    halving = True
                if call_count > 0:
                    return {
                        "found": True,
                        "func_name": fname,
                        "branches": call_count,
                        "halving": halving
                    }
        return info

    @classmethod
    def _detect_python_halving(cls, tree: ast.AST) -> bool:
        for node in ast.walk(tree):
            if isinstance(node, ast.While):
                for child in ast.walk(node):
                    # Check for /= 2, //= 2, >>= 1 or (low + high) // 2
                    if isinstance(child, ast.AugAssign) and isinstance(child.op, (ast.FloorDiv, ast.Div, ast.RShift)):
                        return True
                    if isinstance(child, ast.Assign):
                        for val in ast.walk(child.value):
                            if isinstance(val, ast.BinOp) and isinstance(val.op, (ast.FloorDiv, ast.Div, ast.RShift)):
                                return True
        return False

    @classmethod
    def _detect_python_sorting(cls, tree: ast.AST) -> bool:
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in ("sorted", "heapq"):
                    return True
                if isinstance(node.func, ast.Attribute) and node.func.attr in ("sort", "heappush", "heappop"):
                    return True
        return False

    @classmethod
    def _detect_python_space(cls, tree: ast.AST, recursion_info: Dict[str, Any]) -> Tuple[str, List[str]]:
        details = []
        has_matrix = False
        has_linear_alloc = False

        for node in ast.walk(tree):
            # Nested list comprehension: [[0]*n for _ in range(n)]
            if isinstance(node, ast.ListComp):
                for elt in ast.walk(node.elt):
                    if isinstance(elt, (ast.ListComp, ast.BinOp)):
                        has_matrix = True
                has_linear_alloc = True
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in ("list", "dict", "set"):
                    has_linear_alloc = True

        if has_matrix:
            details.append("2D grid or matrix memory allocation detected: O(n^2) auxiliary space.")
            return "O(n^2)", details
        
        if recursion_info["found"]:
            details.append(f"Recursive call stack frames up to depth n: O(n) space.")
            return "O(n)", details

        if has_linear_alloc:
            details.append("Dynamic list/dictionary proportional to input elements: O(n) auxiliary space.")
            return "O(n)", details

        details.append("In-place mutations and constant scalar pointers: O(1) auxiliary space.")
        return "O(1)", details

    @classmethod
    def analyze_generic(cls, code: str, language: str) -> ComplexityResult:
        """
        Generic analyzer for C++, Java, JS with pattern-based AST approximation.
        """
        # Count loop nesting levels
        lines = code.splitlines()
        max_depth = 0
        current_depth = 0
        has_halving = False
        has_sort = bool(re.search(r'\b(std::sort|sort|Arrays\.sort|Collections\.sort|qsort)\b', code))
        
        # Check recursion: look for function declarations and calls inside
        func_match = re.search(r'\b(?:void|int|double|float|long|bool|auto|function|def|public|private)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', code)
        is_recursive = False
        rec_branches = 0
        if func_match:
            fname = func_match.group(1)
            if fname not in ("main", "if", "for", "while", "switch"):
                calls = len(re.findall(r'\b' + re.escape(fname) + r'\s*\(', code))
                if calls > 1:
                    is_recursive = True
                    rec_branches = calls - 1

        # Check loop depth
        for line in lines:
            stripped = line.strip()
            if re.search(r'\b(for|while)\s*\(', stripped):
                current_depth += 1
                max_depth = max(max_depth, current_depth)
                if re.search(r'(/=|\bmid\b|\b>>=|\b/\s*2)', stripped):
                    has_halving = True
            elif '}' in stripped:
                if current_depth > 0:
                    current_depth -= 1

        # Check halving anywhere in body
        if re.search(r'(/=\s*2|>>=\s*1|mid\s*=\s*\([^)]+\)\s*/\s*2)', code):
            has_halving = True

        # Check space allocation
        has_vector_alloc = bool(re.search(r'\b(vector<|new\s+\w+\[|ArrayList|int\[\]|new\s+Array|\[\])', code))
        has_matrix = bool(re.search(r'\b(vector<vector<|new\s+\w+\[[^\]]+\]\[|\bint\[\]\[\])', code))

        details = []
        if is_recursive:
            if rec_branches >= 2 and not has_halving:
                time_comp = "O(2^n)"
                confidence = 0.88
                details.append(f"Recursive branching detected ({rec_branches} calls per activation frame).")
            elif has_halving:
                time_comp = "O(log n)"
                confidence = 0.90
                details.append("Divide-and-conquer logarithmic reduction.")
            else:
                time_comp = "O(n)"
                confidence = 0.90
                details.append("Linear recursive depth.")
        elif has_sort:
            time_comp = "O(n log n)"
            confidence = 0.92
            details.append("Standard library sorting algorithm detected.")
        elif max_depth == 0:
            if has_halving:
                time_comp = "O(log n)"
                confidence = 0.88
                details.append("Logarithmic operation pattern.")
            else:
                time_comp = "O(1)"
                confidence = 0.95
                details.append("Sequential constant-time instructions.")
        elif max_depth == 1:
            if has_halving:
                time_comp = "O(log n)"
                confidence = 0.90
                details.append("Single loop with logarithmic step / halving reduction.")
            else:
                time_comp = "O(n)"
                confidence = 0.94
                details.append("Single iterative loop traversing input elements.")
        elif max_depth == 2:
            time_comp = "O(n^2)"
            confidence = 0.90
            details.append("2 levels of nested loops detected.")
        elif max_depth == 3:
            time_comp = "O(n^3)"
            confidence = 0.88
            details.append("3 levels of nested loops detected.")
        else:
            time_comp = f"O(n^{max_depth})"
            confidence = 0.82
            details.append(f"{max_depth} levels of nested loops detected.")

        if has_matrix:
            space_comp = "O(n^2)"
            details.append("2D dynamically allocated matrix structure.")
        elif is_recursive or has_vector_alloc:
            space_comp = "O(n)"
            details.append("Dynamic buffer/recursion stack scaling with N.")
        else:
            space_comp = "O(1)"
            details.append("Constant scalar pointers and primitive variable registers.")

        rec_dict = {"found": is_recursive, "func_name": func_match.group(1) if func_match else "", "branches": rec_branches, "halving": has_halving}
        explanation = cls._generate_explanation(time_comp, space_comp, max_depth, rec_dict, has_halving)

        return ComplexityResult(
            time_complexity=time_comp,
            space_complexity=space_comp,
            confidence=confidence,
            explanation=explanation,
            nested_depth=max_depth,
            recursion_found=is_recursive,
            has_halving=has_halving,
            details=details
        )

    @classmethod
    def _generate_explanation(cls, time_comp: str, space_comp: str, depth: int, rec_info: Dict[str, Any], has_halving: bool) -> str:
        if time_comp == "O(1)":
            return "The program executes a fixed number of operations that do not depend on the input size N, requiring constant O(1) time and space."
        elif time_comp == "O(log n)":
            return "The search/state space is halved on each iteration or recursion step, shrinking exponentially by a factor of 2, resulting in O(log n) operations."
        elif time_comp == "O(n)":
            if rec_info.get("found"):
                return f"The recursive function '{rec_info.get('func_name', '')}' is invoked sequentially up to depth N, performing O(1) work per call for an overall O(n) runtime and O(n) call-stack memory."
            return "The algorithm iterates over the input elements linearly once, executing a constant amount of work per element, leading to O(n) time complexity."
        elif time_comp == "O(n log n)":
            return "The algorithm combines linear data traversal or partitioning with logarithmic sub-problem divisions (typical of efficient sorting like MergeSort/QuickSort/Timsort), yielding O(n log n)."
        elif time_comp == "O(n^2)":
            return "The algorithm contains 2 nested loops where the outer loop runs ~n times and the inner loop executes ~n times for each outer step, resulting in O(n²) total iterations."
        elif time_comp == "O(n^3)":
            return "The algorithm features 3 nested loops (such as naive matrix multiplication), performing n × n × n = O(n³) operations."
        elif time_comp == "O(2^n)":
            return f"The recursive function '{rec_info.get('func_name', '')}' spawns multiple recursive sub-branches per step without memoization, generating an exponential call tree of size O(2^n)."
        return f"Static analysis evaluated a maximum loop nesting depth of {depth}, leading to an estimated asymptotic complexity of {time_comp}."
