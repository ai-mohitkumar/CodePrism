from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Any
from app.models import (
    AnalyzeRequest, AnalysisResponse,
    ExecuteRequest, ExecutionResult,
    BenchmarkRequest, BenchmarkResult,
    OptimizeRequest, OptimizeResponse
)
from app.engines.adapters.registry import LANGUAGE_ADAPTERS, TEMPLATES, get_all_languages_metadata
from app.profiler.benchmark import BenchmarkEngine
from app.ai.optimizer import AIOptimizer

app = FastAPI(
    title="CodePrism API",
    description="Universal Code Compiler, Static AST Analyzer, Big-O Complexity Engine, and Runtime Profiler",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "service": "CodePrism Universal API",
        "status": "online",
        "supported_languages_count": len(get_all_languages_metadata()),
        "roadmap_tiers": ["Tier 1: Essential (Top 15)", "Tier 2: Popular/Industry", "Tier 3: Domain-Specific", "Tier 4: Functional", "Tier 5: Legacy", "Tier 6: Hardware"]
    }

@app.get("/api/languages")
def get_languages():
    return {
        "languages": get_all_languages_metadata(),
        "templates": TEMPLATES
    }

@app.post("/api/execute", response_model=ExecutionResult)
def execute_code(req: ExecuteRequest):
    lang_key = req.language.lower()
    engine = LANGUAGE_ADAPTERS.get(lang_key)
    if not engine:
        raise HTTPException(status_code=400, detail=f"Unsupported language '{req.language}'.")
    return engine.execute(req.code, stdin=req.stdin or "", timeout_sec=req.timeout_sec or 5.0)

@app.post("/api/analyze", response_model=AnalysisResponse)
def analyze_code(req: AnalyzeRequest):
    lang_key = req.language.lower()
    engine = LANGUAGE_ADAPTERS.get(lang_key)
    if not engine:
        raise HTTPException(status_code=400, detail=f"Unsupported language '{req.language}'.")

    # 1. Execute code & measure runtime metrics
    exec_res = engine.execute(req.code, stdin=req.stdin or "")

    # 2. Static complexity analysis
    complexity_res = engine.analyze_complexity(req.code)

    # 3. Line-by-line analysis
    lines_res = engine.analyze_lines(req.code)

    # 4. Code quality & cyclomatic complexity
    quality_res = engine.evaluate_quality(req.code)

    # 5. Security audit
    security_res = engine.audit_security(req.code)

    # 6. Empirical benchmark (if Python and requested)
    benchmark_res = None
    if req.run_empirical_benchmark and lang_key in ("python", "py") and exec_res.status == "success":
        benchmark_res = BenchmarkEngine.benchmark_python_code(req.code)

    # 7. AI Insights and Optimization suggestions
    ai_insights = None
    if exec_res.status == "success":
        ai_insights = AIOptimizer.generate_insights(lang_key, req.code, complexity_res.time_complexity)

    return AnalysisResponse(
        language=lang_key,
        execution=exec_res,
        complexity=complexity_res,
        line_analysis=lines_res,
        quality=quality_res,
        security=security_res,
        benchmark=benchmark_res,
        ai_insights=ai_insights
    )

@app.post("/api/optimize", response_model=OptimizeResponse)
def optimize_code(req: OptimizeRequest):
    lang_key = req.language.lower()
    engine = LANGUAGE_ADAPTERS.get(lang_key)
    if not engine:
        raise HTTPException(status_code=400, detail=f"Unsupported language '{req.language}'.")

    complexity = engine.analyze_complexity(req.code)
    insights = AIOptimizer.generate_insights(lang_key, req.code, complexity.time_complexity)

    opt_code = insights.optimized_code or req.code
    opt_big_o = insights.optimized_big_o or complexity.time_complexity

    diff_summary = [
        f"Original Time Complexity: {complexity.time_complexity}",
        f"Optimized Time Complexity: {opt_big_o}",
        insights.why_faster or "Refactored algorithm logic."
    ]

    return OptimizeResponse(
        original_code=req.code,
        optimized_code=opt_code,
        original_big_o=complexity.time_complexity,
        optimized_big_o=opt_big_o,
        explanation=insights.algorithmic_breakdown or "Optimization applied.",
        diff_summary=diff_summary
    )
