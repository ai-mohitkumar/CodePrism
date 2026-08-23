import os
import time
import shutil
import psutil
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from api.compile import router as compile_router
from api.execute import router as execute_router
from api.analyze import router as analyze_router
from api.upload import router as upload_router
from api.jobs import router as jobs_router
from api.debug import router as debug_router
from api.ai import router as ai_router
from api.projects import router as projects_router
from api.mobile import router as mobile_router
from languages.registry import LanguageRegistry

START_TIME = time.time()

app = FastAPI(
    title="CodePrism 🔮 — Universal Intelligent Compiler & Multi-Device Cloud Platform",
    description="Shared Compiler & Code Intelligence Backend for Web/PC (Monaco IDE) and Mobile (Flutter/React Native): Native Toolchains, Bytecode, AST, Big-O Complexity, Profiler, Debugger, and Cross-Device Cloud Sync",
    version="1.1.0"
)

# CORS middleware for local development and production deployments
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(compile_router)
app.include_router(execute_router)
app.include_router(analyze_router)
app.include_router(upload_router)
app.include_router(jobs_router)
app.include_router(debug_router)
app.include_router(ai_router)
app.include_router(projects_router)
app.include_router(mobile_router)

# Health & Production Diagnostics
@app.get("/health")
def health_check():
    """Production health check probe for Kubernetes / Cloud Run / Railway / Render."""
    uptime_sec = round(time.time() - START_TIME, 2)
    mem = psutil.virtual_memory()
    return {
        "status": "healthy",
        "uptime_seconds": uptime_sec,
        "service": "CodePrism Universal Compiler Engine",
        "version": "1.1.0",
        "system": {
            "cpu_count": psutil.cpu_count(logical=True),
            "memory_used_percent": mem.percent,
            "memory_available_mb": round(mem.available / (1024 * 1024), 2)
        },
        "compilers": {
            "python": shutil.which("python") is not None or shutil.which("python3") is not None,
            "gcc_cpp": shutil.which("g++") is not None or shutil.which("gcc") is not None,
            "java_jdk": shutil.which("javac") is not None,
            "dotnet": shutil.which("dotnet") is not None,
            "rust": shutil.which("rustc") is not None,
            "go": shutil.which("go") is not None,
            "node": shutil.which("node") is not None
        }
    }

@app.get("/")
def get_root(request: Request):
    accept_header = request.headers.get("accept", "")
    # If a browser requests HTML and frontend/dist/index.html is built
    if "text/html" in accept_header and os.path.exists(os.path.join(FRONTEND_DIST, "index.html")):
        return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))
    return get_api_info()

@app.get("/api/info")
def get_api_info():
    return {
        "service": "CodePrism 🔮 — Shared Compiler & Intelligence Engine",
        "tagline": "Code once. Compile anywhere. Understand everything.",
        "clients": {
            "web_pc": "React + TypeScript + Monaco Full IDE",
            "mobile": "Flutter (Android + iOS) Task-Focused Mobile IDE"
        },
        "version": "1.1.0",
        "status": "online",
        "languages_count": len(LanguageRegistry.list_metadata()),
        "cloud_sync": True
    }

@app.get("/api/languages")
def get_languages():
    return {
        "languages": [m.model_dump() for m in LanguageRegistry.list_metadata()],
        "templates": LanguageRegistry.get_templates()
    }

# SPA Production Static Files Serving
FRONTEND_DIST = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))
ASSETS_DIR = os.path.join(FRONTEND_DIST, "assets")

if os.path.exists(ASSETS_DIR):
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="static_assets")

@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """Serves compiled frontend SPA in production with index.html fallback for client-side routing."""
    if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("openapi.json") or full_path.startswith("health"):
        return JSONResponse(status_code=404, content={"detail": "Not Found"})
    
    if os.path.exists(FRONTEND_DIST):
        target_file = os.path.join(FRONTEND_DIST, full_path)
        if full_path and os.path.isfile(target_file):
            return FileResponse(target_file)
        
        index_file = os.path.join(FRONTEND_DIST, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)

    return get_api_info()
