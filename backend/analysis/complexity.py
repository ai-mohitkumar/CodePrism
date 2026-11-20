import ast
import re
from typing import List, Dict, Any, Tuple, Optional
from models import ComplexityResponse

class ComplexityEngine:
    """
    High-fidelity Big-O Time & Space complexity inference engine.
    Supports AST parsing for Python, and grammar-aware scope-stack parsing
    for C++, Java, JavaScript, TypeScript, C#, Rust, and Go.
    """

    @classmethod
    def analyze_python(cls, code: str) -> ComplexityResponse:
        try:
            tree = ast.parse(code)
        except SyntaxError:
            # Fall back to generic text parser if there's a syntax error
            return cls.analyze_generic(code, "python")

        max_loop_depth = 0
        # Check module-level loops
        depth_mod = cls._get_max_loop_depth(tree)
        if depth_mod > max_loop_depth:
            max_loop_depth = depth_mod

        # Also check individual function definitions
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                d = cls._get_max_loop_depth(node)
                if d > max_loop_depth:
                    max_loop_depth = d

        recursion_info = cls._detect_recursion_python(tree)
        has_halving = cls._detect_halving_python(tree)
        has_sort = cls._detect_sort_python(tree)
        space_comp, space_details = cls._detect_space_python(tree, recursion_info)

        details: List[str] = []
        confidence = 0.95

        # Decision Tree for Time Complexity
        if recursion_info["found"]:
            branches = recursion_info["branches"]
            halving = recursion_info["halving"]
            if branches >= 2 and not halving:
                time_comp = "O(2^n)"
                confidence = 0.92
                reason = f"Branching recursion detected in '{recursion_info['func_name']}()' with {branches} recursive calls per activation frame without memoization -> Exponential O(2^n)."
                details.append(reason)
            elif halving:
                if max_loop_depth >= 1:
                    time_comp = "O(n log n)"
                    confidence = 0.92
                    reason = "Divide-and-conquer recursion with linear partition/combination loop (MergeSort / QuickSort pattern) -> O(n log n)."
                else:
                    time_comp = "O(log n)"
                    confidence = 0.94
                    reason = f"Recursive divide-and-conquer search halving problem size each frame -> Logarithmic O(log n)."
                details.append(reason)
            else:
                time_comp = "O(n)"
                confidence = 0.92
                reason = f"Linear single-branch recursion depth with {recursion_info['func_name']}() call stack frames -> O(n)."
                details.append(reason)
        elif has_sort:
            time_comp = "O(n log n)" if max_loop_depth <= 1 else f"O(n^{max_loop_depth} log n)"
            confidence = 0.94
            reason = "Comparison-based sorting algorithm detected (e.g. Timsort O(n log n))."
            details.append(reason)
        elif max_loop_depth == 0:
            if has_halving:
                time_comp = "O(log n)"
                confidence = 0.90
                reason = "Binary halving / doubling progression without outer loops -> O(log n)."
            else:
                time_comp = "O(1)"
                confidence = 0.98
                reason = "Sequential constant-time instructions with no loops or recursive calls -> O(1)."
            details.append(reason)
        elif max_loop_depth == 1:
            if has_halving:
                time_comp = "O(log n)"
                confidence = 0.94
                reason = "Single loop halving or doubling the search space per iteration (Binary Search pattern) -> O(log n)."
            else:
                time_comp = "O(n)"
                confidence = 0.96
                reason = "Single linear loop iterating through input elements -> O(n)."
            details.append(reason)
        elif max_loop_depth == 2:
            if has_halving:
                time_comp = "O(n log n)"
                confidence = 0.92
                reason = "Nested loops with logarithmic inner step or partition -> O(n log n)."
            else:
                time_comp = "O(n²)"
                confidence = 0.95
                reason = "Two nested loops detected where the inner loop executes across the input for each outer iteration -> Quadratic O(n²)."
            details.append(reason)
        elif max_loop_depth == 3:
            time_comp = "O(n³)"
            confidence = 0.92
            reason = "Three nested loops detected (Cubic O(n³), typical in 3D grid or matrix multiplication operations)."
            details.append(reason)
        else:
            time_comp = f"O(n^{max_loop_depth})"
            confidence = 0.88
            reason = f"{max_loop_depth} levels of nested loops detected -> Polynomial O(n^{max_loop_depth})."
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
        """
        Scope-stack parser for C++, Java, JavaScript, TypeScript, C#, Rust, and Go.
        Tracks brace scopes to distinguish loops from if-blocks, functions, and classes.
        """
        lines = code.splitlines()
        max_loop_depth = 0
        scope_stack: List[str] = [] # stores 'loop', 'func', or 'block'

        # Patterns for loops in C-style languages
        loop_pattern = re.compile(r'\b(for|while)\s*\(|\bfor\s+[A-Za-z0-9_]+\s+in\s+|\bfor\s*\{')
        # Patterns for halving (binary search)
        halving_pattern = re.compile(r'(/=\s*2|>>=\s*1|\bmid\s*=\s*[^;]+/\s*2|\bhigh\s*=\s*mid|\blow\s*=\s*mid|\b(i|j|k|step)\s*\*=\s*2|\b(i|j|k|step)\s*\/=\s*2)')
        # Patterns for sorting
        sort_pattern = re.compile(r'\b(std::sort|qsort|Arrays\.sort|Collections\.sort|\.sort\(|sorted\(|sort\.Slice)\b')

        has_halving = bool(halving_pattern.search(code))
        has_sort = bool(sort_pattern.search(code))

        # Check recursion in C-family languages
        recursion_info = cls._detect_recursion_generic(code)

        for line in lines:
            stripped = line.strip()
            # Ignore comments
            if stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("*"):
                continue

            # Remove string literals to avoid counting braces inside strings
            cleaned_line = re.sub(r'"([^"\\]|\\.)*"', '""', stripped)
            cleaned_line = re.sub(r"'([^'\\]|\\.)*'", "''", cleaned_line)

            is_loop_line = bool(loop_pattern.search(cleaned_line))

            for char in cleaned_line:
                if char == '{':
                    if is_loop_line:
                        scope_stack.append('loop')
                        is_loop_line = False # consumed
                    else:
                        scope_stack.append('block')
                    
                    # Update max loop depth
                    current_loop_depth = sum(1 for s in scope_stack if s == 'loop')
                    if current_loop_depth > max_loop_depth:
                        max_loop_depth = current_loop_depth

                elif char == '}':
                    if scope_stack:
                        scope_stack.pop()

            # Handle single-line loops without braces: e.g. for (...) for (...)
            if is_loop_line and '{' not in cleaned_line:
                # Count consecutive for / while on the same line
                loops_on_line = len(loop_pattern.findall(cleaned_line))
                current_loop_depth = sum(1 for s in scope_stack if s == 'loop') + loops_on_line
                if current_loop_depth > max_loop_depth:
                    max_loop_depth = current_loop_depth

        # Space complexity detection for C-family
        space_comp, space_details = cls._detect_space_generic(code, recursion_info["found"])

        details: List[str] = []
        confidence = 0.94

        if recursion_info["found"]:
            branches = recursion_info["branches"]
            if branches >= 2 and not has_halving:
                time_comp = "O(2^n)"
                confidence = 0.90
                reason = f"Branching recursive function '{recursion_info['func_name']}()' calls itself {branches} times per frame without memoization -> Exponential O(2^n)."
            elif has_halving:
                if max_loop_depth >= 1:
                    time_comp = "O(n log n)"
                    confidence = 0.92
                    reason = "Divide-and-conquer recursion with linear partitioning loop -> Linearithmic O(n log n)."
                else:
                    time_comp = "O(log n)"
                    confidence = 0.94
                    reason = f"Recursive divide-and-conquer reduction halving the search space per activation -> O(log n)."
            else:
                time_comp = "O(n)"
                confidence = 0.92
                reason = f"Linear recursion stack in function '{recursion_info['func_name']}()' -> Linear O(n)."
            details.append(reason)
        elif has_sort:
            time_comp = "O(n log n)" if max_loop_depth <= 1 else f"O(n^{max_loop_depth} log n)"
            confidence = 0.95
            reason = "Standard library comparison-based sort detected (O(n log n))."
            details.append(reason)
        elif max_loop_depth == 0:
            if has_halving:
                time_comp = "O(log n)"
                confidence = 0.92
                reason = "Halving / doubling step progression without outer loops -> Logarithmic O(log n)."
            else:
                time_comp = "O(1)"
                confidence = 0.98
                reason = "Constant-time instructions with no loop nesting or recursion -> O(1)."
            details.append(reason)
        elif max_loop_depth == 1:
            if has_halving:
                time_comp = "O(log n)"
                confidence = 0.94
                reason = "Single loop halving search space per iteration (Binary Search pattern) -> Logarithmic O(log n)."
            else:
                time_comp = "O(n)"
                confidence = 0.96
                reason = "Single linear loop scanning elements -> Linear O(n)."
            details.append(reason)
        elif max_loop_depth == 2:
            if has_halving:
                time_comp = "O(n log n)"
                confidence = 0.92
                reason = "Nested iteration where inner loop scales logarithmically -> O(n log n)."
            else:
                time_comp = "O(n²)"
                confidence = 0.95
                reason = "Two nested loops detected where the inner loop executes across the dataset for each outer step -> Quadratic O(n²)."
            details.append(reason)
        elif max_loop_depth == 3:
            time_comp = "O(n³)"
            confidence = 0.92
            reason = "Three nested loops detected (Cubic O(n³), e.g. matrix multiplication or 3D traversal)."
            details.append(reason)
        else:
            time_comp = f"O(n^{max_loop_depth})"
            confidence = 0.88
            reason = f"{max_loop_depth} levels of nested loops detected -> Polynomial O(n^{max_loop_depth})."
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
    def _detect_recursion_python(cls, tree: ast.AST) -> Dict[str, Any]:
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
    def _detect_recursion_generic(cls, code: str) -> Dict[str, Any]:
        # Match function declarations: return_type func_name(args)
        funcs = re.findall(r'\b(?:int|void|bool|double|float|long|auto|String|def|function)?\s+([A-Za-z0-9_]+)\s*\([^)]*\)\s*\{', code)
        for fname in funcs:
            if fname in ('main', 'if', 'for', 'while', 'switch', 'catch'):
                continue
            # Look for calls to fname inside code
            calls = len(re.findall(rf'\b{fname}\s*\(', code))
            if calls >= 2: # At least declaration + 1 internal recursive call
                return {
                    "found": True,
                    "func_name": fname,
                    "branches": calls - 1
                }
        return {"found": False, "func_name": "", "branches": 0}

    @classmethod
    def _detect_halving_python(cls, tree: ast.AST) -> bool:
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
    def _detect_sort_python(cls, tree: ast.AST) -> bool:
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in ("sorted", "heapq"):
                    return True
                if isinstance(node.func, ast.Attribute) and node.func.attr in ("sort", "heappush"):
                    return True
        return False

    @classmethod
    def _detect_space_python(cls, tree: ast.AST, rec_info: Dict[str, Any]) -> Tuple[str, List[str]]:
        details = []
        for node in ast.walk(tree):
            # Check 2D allocations
            if isinstance(node, ast.ListComp):
                for elt in ast.walk(node.elt):
                    if isinstance(elt, (ast.ListComp, ast.BinOp)):
                        details.append("Allocates 2D matrix structure -> O(n²) space.")
                        return "O(n²)", details
                details.append("Allocates dynamic list / array -> O(n) space.")
                return "O(n)", details
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in ('list', 'dict', 'set'):
                    details.append(f"Allocates dynamic collection '{node.func.id}()' -> O(n) space.")
                    return "O(n)", details

        if rec_info["found"]:
            details.append(f"Call stack frames for recursion in '{rec_info['func_name']}()' -> O(n) auxiliary stack space.")
            return "O(n)", details

        details.append("In-place scalar variables only -> O(1) auxiliary space.")
        return "O(1)", details

    @classmethod
    def _detect_space_generic(cls, code: str, has_recursion: bool) -> Tuple[str, List[str]]:
        details = []

        # 2D Grid / Matrix allocations
        if re.search(r'(vector\s*<\s*vector|new\s+[A-Za-z0-9_]+\s*\[[^\]]+\]\s*\[[^\]]+\]|int\s+\[\]\s*\[\])', code):
            details.append("Allocates 2D matrix / nested vector buffers -> O(n²) space.")
            return "O(n²)", details

        # 1D Dynamic Collections
        if re.search(r'(vector\s*<|new\s+[A-Za-z0-9_]+\s*\[|ArrayList|HashMap|HashSet|new\s+Array|new\s+Map|new\s+Set|make\s*\(\s*\[\])', code):
            details.append("Allocates dynamic heap collections / array buffers -> O(n) auxiliary space.")
            return "O(n)", details

        if has_recursion:
            details.append("Recursive call stack memory allocation -> O(n) auxiliary space.")
            return "O(n)", details

        details.append("In-place scalar variables (no dynamic buffers allocated) -> O(1) space.")
        return "O(1)", details
