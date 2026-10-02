import ast
import re
from typing import Optional, List, Dict, Any
from models import ASTNode, ASTResponse

class ASTParser:
    @classmethod
    def parse_python(cls, code: str) -> ASTResponse:
        try:
            tree = ast.parse(code)
            counter = [0]
            root_node = cls._convert_ast_node(tree, counter)
            summary = cls._generate_summary(tree)
            return ASTResponse(root=root_node, summary=summary)
        except SyntaxError as e:
            return ASTResponse(
                root=ASTNode(
                    id="err_0",
                    name="SyntaxError",
                    type="ErrorNode",
                    lineno=e.lineno,
                    col_offset=e.offset,
                    details=f"{e.msg} at line {e.lineno}:{e.offset}"
                ),
                summary=[f"AST generation aborted due to SyntaxError on line {e.lineno}"]
            )

    @classmethod
    def parse_java(cls, code: str) -> ASTResponse:
        counter = [0]
        
        def next_id():
            counter[0] += 1
            return f"node_java_{counter[0]}"

        lines = code.splitlines()
        root_children: List[ASTNode] = []
        classes_found = []
        methods_found = []
        loops_count = 0
        conditions_count = 0

        current_class: Optional[ASTNode] = None
        current_method: Optional[ASTNode] = None

        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("//") or stripped.startswith("/*"):
                continue

            # Class definition
            class_match = re.search(r'\b(?:public|private|protected)?\s*(?:static\s+)?class\s+([A-Za-z0-9_]+)(?:\s+extends\s+[A-Za-z0-9_]+)?(?:\s+implements\s+[A-Za-z0-9_,\s]+)?', stripped)
            if class_match:
                cname = class_match.group(1)
                classes_found.append(cname)
                current_class = ASTNode(
                    id=next_id(),
                    name=f"ClassDecl: {cname}",
                    type="ClassDeclaration",
                    lineno=idx,
                    details=stripped,
                    children=[]
                )
                root_children.append(current_class)
                current_method = None
                continue

            # Method definition
            method_match = re.search(r'\b(?:public|private|protected|static|final|\s)+\s+([A-Za-z0-9_<>\[\]]+)\s+([A-Za-z0-9_]+)\s*\(([^)]*)\)\s*(?:throws\s+[A-Za-z0-9_,\s]+)?\s*\{?', stripped)
            if method_match and not any(kw in method_match.group(2) for kw in ('if', 'for', 'while', 'switch', 'catch')):
                ret_type = method_match.group(1)
                mname = method_match.group(2)
                params = method_match.group(3)
                methods_found.append(f"{mname}()")
                current_method = ASTNode(
                    id=next_id(),
                    name=f"MethodDecl: {ret_type} {mname}({params})",
                    type="MethodDeclaration",
                    lineno=idx,
                    details=f"return: {ret_type}, params: {params}",
                    children=[]
                )
                if current_class:
                    current_class.children.append(current_method)
                else:
                    root_children.append(current_method)
                continue

            # Loop statements
            if re.search(r'\bfor\s*\(', stripped):
                loops_count += 1
                loop_node = ASTNode(
                    id=next_id(),
                    name="ForLoop Statement",
                    type="ForStatement",
                    lineno=idx,
                    details=stripped,
                    children=[]
                )
                target = current_method or current_class
                if target:
                    target.children.append(loop_node)
                else:
                    root_children.append(loop_node)
            elif re.search(r'\bwhile\s*\(', stripped):
                loops_count += 1
                while_node = ASTNode(
                    id=next_id(),
                    name="WhileLoop Statement",
                    type="WhileStatement",
                    lineno=idx,
                    details=stripped,
                    children=[]
                )
                target = current_method or current_class
                if target:
                    target.children.append(while_node)
                else:
                    root_children.append(while_node)

            # If Conditional
            elif re.search(r'\bif\s*\(', stripped):
                conditions_count += 1
                if_node = ASTNode(
                    id=next_id(),
                    name="IfCondition",
                    type="IfStatement",
                    lineno=idx,
                    details=stripped,
                    children=[]
                )
                target = current_method or current_class
                if target:
                    target.children.append(if_node)
                else:
                    root_children.append(if_node)

            # System.out.println
            elif "System.out.print" in stripped:
                call_node = ASTNode(
                    id=next_id(),
                    name="PrintStream: System.out.println()",
                    type="MethodInvocation",
                    lineno=idx,
                    details=stripped,
                    children=[]
                )
                target = current_method or current_class
                if target:
                    target.children.append(call_node)
                else:
                    root_children.append(call_node)

        root = ASTNode(
            id="node_java_root",
            name="CompilationUnit (Java Source)",
            type="CompilationUnit",
            lineno=1,
            children=root_children
        )

        summary = []
        if classes_found:
            summary.append(f"Declared {len(classes_found)} Java Class(es): {', '.join(classes_found)}")
        if methods_found:
            summary.append(f"Defined {len(methods_found)} Method(s): {', '.join(methods_found)}")
        if loops_count > 0:
            summary.append(f"Contains {loops_count} loop construct(s)")
        if conditions_count > 0:
            summary.append(f"Evaluates {conditions_count} branching condition(s)")

        if not summary:
            summary = ["Java source compilation unit analyzed successfully."]

        return ASTResponse(root=root, summary=summary)

    @classmethod
    def _convert_ast_node(cls, node: ast.AST, counter: List[int]) -> ASTNode:
        counter[0] += 1
        node_id = f"node_{counter[0]}"
        node_type = type(node).__name__
        name = node_type
        details = None

        if isinstance(node, ast.FunctionDef):
            name = f"FunctionDef: {node.name}()"
            details = f"args: {[a.arg for a in node.args.args]}"
        elif isinstance(node, ast.ClassDef):
            name = f"ClassDef: {node.name}"
        elif isinstance(node, ast.For):
            target = getattr(node.target, 'id', 'item')
            name = f"For Loop (iter: {target})"
        elif isinstance(node, ast.While):
            name = "While Loop"
        elif isinstance(node, ast.If):
            name = "If Conditional"
        elif isinstance(node, ast.Call):
            func_name = getattr(node.func, 'id', getattr(node.func, 'attr', 'call'))
            name = f"Call: {func_name}()"
        elif isinstance(node, ast.Name):
            name = f"Name: {node.id}"
            details = f"ctx: {type(node.ctx).__name__}"
        elif isinstance(node, ast.Constant):
            name = f"Constant: {repr(node.value)}"
        elif isinstance(node, ast.Assign):
            name = "Assignment (=)"
        elif isinstance(node, ast.Return):
            name = "Return Statement"
        elif isinstance(node, ast.BinOp):
            name = f"BinOp: {type(node.op).__name__}"

        lineno = getattr(node, 'lineno', None)
        col_offset = getattr(node, 'col_offset', None)

        children: List[ASTNode] = []
        for child in ast.iter_child_nodes(node):
            children.append(cls._convert_ast_node(child, counter))

        return ASTNode(
            id=node_id,
            name=name,
            type=node_type,
            lineno=lineno,
            col_offset=col_offset,
            details=details,
            children=children
        )

    @classmethod
    def _generate_summary(cls, tree: ast.AST) -> List[str]:
        funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
        loops = sum(1 for n in ast.walk(tree) if isinstance(n, (ast.For, ast.While)))
        conditions = sum(1 for n in ast.walk(tree) if isinstance(n, ast.If))
        calls = [getattr(n.func, 'id', getattr(n.func, 'attr', 'call')) for n in ast.walk(tree) if isinstance(n, ast.Call)]

        summary = []
        if funcs:
            summary.append(f"Declared {len(funcs)} function(s): {', '.join(funcs)}")
        if loops > 0:
            summary.append(f"Contains {loops} loop construct(s)")
        if conditions > 0:
            summary.append(f"Evaluates {conditions} branching condition(s)")
        if calls:
            top_calls = list(dict.fromkeys(calls))[:5]
            summary.append(f"Invokes {len(calls)} function call(s) (e.g. {', '.join(top_calls)})")

        return summary if summary else ["Sequential statement execution"]
