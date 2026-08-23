from fastapi import APIRouter
from models import DebugStepRequest, DebugStepResponse
import ast

router = APIRouter(prefix="/api/debug", tags=["Debugger"])

@router.post("/step", response_model=DebugStepResponse)
def debug_step(req: DebugStepRequest):
    lines = req.code.splitlines()
    total_lines = len(lines)
    curr_line = max(1, min(req.line_number, total_lines))

    # Inspect current line text
    line_text = lines[curr_line - 1].strip() if 1 <= curr_line <= total_lines else ""
    vars_map = dict(req.variables)
    output_str = ""

    # Simple variable tracker simulation for common statements
    if "=" in line_text and not line_text.startswith(("if", "for", "while")):
        parts = line_text.split("=", 1)
        var_name = parts[0].strip()
        var_val = parts[1].strip()
        if var_name.isidentifier():
            try:
                # evaluate primitive literals
                parsed_val = ast.literal_eval(var_val)
                vars_map[var_name] = parsed_val
            except Exception:
                vars_map[var_name] = var_val

    if "print(" in line_text:
        match = line_text.split("print(", 1)[1].rsplit(")", 1)[0]
        output_str = f"Printed: {vars_map.get(match.strip(), match.strip())}\n"

    # Determine next execution line
    next_line = curr_line + 1
    # Check if breakpoint hit
    while next_line <= total_lines:
        if lines[next_line - 1].strip() and not lines[next_line - 1].strip().startswith("#"):
            break
        next_line += 1

    is_term = next_line > total_lines

    return DebugStepResponse(
        current_line=min(next_line, total_lines) if not is_term else curr_line,
        is_terminated=is_term,
        stdout=output_str,
        variables=vars_map,
        call_stack=[f"<module>() at line {curr_line}"],
        output=f"Executed line {curr_line}: {line_text}"
    )
