import ast
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
