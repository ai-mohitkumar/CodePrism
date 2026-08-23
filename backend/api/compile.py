from fastapi import APIRouter, HTTPException
from models import CompileRequest, CompileResponse
from languages.registry import LanguageRegistry

router = APIRouter(prefix="/api", tags=["Compiler Engine"])

@router.post("/compile", response_model=CompileResponse)
def compile_code(req: CompileRequest):
    adapter = LanguageRegistry.get(req.language)
    if not adapter:
        raise HTTPException(status_code=400, detail=f"Unsupported compiler for language '{req.language}'.")

    return adapter.compile_detailed(req.code, flags=req.compiler_flags)
