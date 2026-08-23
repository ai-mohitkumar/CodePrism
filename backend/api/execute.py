from fastapi import APIRouter, HTTPException
from models import ExecuteRequest, UniversalResult
from languages.registry import LanguageRegistry

router = APIRouter(prefix="/api", tags=["Execution"])

@router.post("/execute", response_model=UniversalResult)
def execute_code(req: ExecuteRequest):
    adapter = LanguageRegistry.get(req.language)
    if not adapter:
        raise HTTPException(status_code=400, detail=f"Unsupported language '{req.language}'.")

    return adapter.run_full_analysis(
        code=req.code,
        stdin=req.stdin or "",
        timeout_sec=req.timeout_sec or 5.0,
        filename=req.filename
    )
