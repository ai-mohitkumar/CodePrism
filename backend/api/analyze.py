from fastapi import APIRouter, HTTPException
from models import (
    AnalyzeErrorRequest, ErrorDiagnosis, ASTResponse, 
    ComplexityResponse, ExecuteRequest, UniversalResult
)
from languages.registry import LanguageRegistry

router = APIRouter(prefix="/api/analyze", tags=["Analysis"])

@router.post("/errors", response_model=ErrorDiagnosis)
def analyze_errors(req: AnalyzeErrorRequest):
    adapter = LanguageRegistry.get(req.language)
    if not adapter:
        return ErrorDiagnosis(has_error=False)

    compile_res = adapter.compile(req.code)
    if not compile_res.success:
        return ErrorDiagnosis(
            has_error=True,
            error_type="Compile/Syntax Error",
            line=compile_res.error_line,
            column=compile_res.error_column,
            message=compile_res.compiler_output,
            pointer=compile_res.error_pointer,
            suggested_fix=compile_res.suggested_fix
        )

    return ErrorDiagnosis(has_error=False)

@router.post("/ast", response_model=ASTResponse)
def analyze_ast(req: AnalyzeErrorRequest):
    adapter = LanguageRegistry.get(req.language)
    if adapter:
        ast_res = adapter.parse_ast(req.code)
        if ast_res:
            return ast_res
    return ASTResponse(summary=[f"AST visualizer currently provides deep AST tree decomposition for Python and standard syntax trees for {req.language}."])

@router.post("/complexity", response_model=ComplexityResponse)
def analyze_complexity(req: AnalyzeErrorRequest):
    adapter = LanguageRegistry.get(req.language)
    if adapter:
        comp = adapter.analyze_complexity(req.code)
        return ComplexityResponse(
            time_complexity=comp.time,
            space_complexity=comp.space,
            confidence=comp.confidence,
            reason=comp.reason,
            nested_depth=comp.nested_depth,
            has_recursion=comp.has_recursion,
            has_halving=comp.has_halving,
            details=comp.details
        )
    return ComplexityResponse()

@router.post("/full", response_model=UniversalResult)
def analyze_full(req: ExecuteRequest):
    adapter = LanguageRegistry.get(req.language)
    if not adapter:
        raise HTTPException(status_code=400, detail=f"Unsupported language '{req.language}'.")

    return adapter.run_full_analysis(
        code=req.code,
        stdin=req.stdin or "",
        timeout_sec=req.timeout_sec or 5.0,
        filename=req.filename
    )
