import os
import re
import ast
import zipfile
import tempfile
import shutil
import subprocess
from typing import List, Dict, Tuple, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from models import (
    FileUploadResponse, FileStats, UniversalResult,
    ProjectReportResponse, ProjectFileSummary, DependencyEdge,
    GitHubRepoRequest
)
from languages.registry import LanguageRegistry

router = APIRouter(prefix="/api", tags=["Upload & Project Analyzers"])

EXTENSION_LANG_MAP = {
    ".py": "python",
    ".pyw": "python",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".c": "cpp",
    ".h": "cpp",
    ".hpp": "cpp",
    ".java": "java",
    ".js": "javascript",
    ".jsx": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".cs": "csharp",
    ".rs": "rust",
    ".go": "go",
    ".kt": "kotlin",
    ".swift": "swift",
    ".php": "php",
    ".rb": "ruby",
    ".dart": "dart",
    ".r": "r",
    ".sql": "sql",
}

def detect_language(filename: str, code: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    if ext in EXTENSION_LANG_MAP:
        return EXTENSION_LANG_MAP[ext]

    lines = code.splitlines()[:20]
    head = "\n".join(lines)

    if "#include <" in head or "std::cout" in head or "using namespace std" in head:
        return "cpp"
    if "public class " in head or "System.out.println" in head:
        return "java"
    if "def " in head or "import " in head or "__name__" in head:
        return "python"
    if "console.log" in head or "const " in head or "function " in head:
        return "javascript"
    if "using System;" in head or "namespace " in head:
        return "csharp"
    if "fn main()" in head:
        return "rust"
    if "package main" in head:
        return "go"

    return "python"

def compute_file_stats(code: str, language: str) -> FileStats:
    lines = [l for l in code.splitlines() if l.strip() and not l.strip().startswith(("#", "//", "/*", "*"))]
    loc = len(lines)
    functions_count = 0
    classes_count = 0
    loops_count = 0

    if language == "python":
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    functions_count += 1
                elif isinstance(node, ast.ClassDef):
                    classes_count += 1
                elif isinstance(node, (ast.For, ast.While, ast.AsyncFor)):
                    loops_count += 1
        except SyntaxError:
            functions_count = len(re.findall(r'^\s*def\s+\w+', code, re.MULTILINE))
            classes_count = len(re.findall(r'^\s*class\s+\w+', code, re.MULTILINE))
            loops_count = len(re.findall(r'^\s*(for|while)\s+', code, re.MULTILINE))
    else:
        functions_count = len(re.findall(r'\b(function|void|int|double|bool|auto|func|fn|def)\s+\w+\s*\(', code))
        classes_count = len(re.findall(r'\b(class|struct|interface|type)\s+\w+', code))
        loops_count = len(re.findall(r'\b(for|while|foreach|loop)\b', code))

    return FileStats(
        loc=loc,
        functions_count=functions_count,
        classes_count=classes_count,
        loops_count=loops_count
    )

def analyze_source_tree(extract_dir: str, project_name: str) -> ProjectReportResponse:
    files_summary: List[ProjectFileSummary] = []
    lang_counts: Dict[str, int] = {}
    total_loc = 0
    total_functions = 0
    total_classes = 0
    all_complexities: List[str] = []
    all_quality_scores: List[float] = []
    security_summary = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    dependency_graph: List[DependencyEdge] = []
    optimizations: List[str] = []

    ignore_dirs = {".git", "node_modules", "venv", ".venv", "__pycache__", "dist", "build", ".idea", ".vscode", "target", "bin", "obj"}

    for root, dirs, filenames in os.walk(extract_dir):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        for fname in filenames:
            ext = os.path.splitext(fname)[1].lower()
            if ext in EXTENSION_LANG_MAP:
                full_path = os.path.join(root, fname)
                rel_path = os.path.relpath(full_path, extract_dir).replace("\\", "/")

                try:
                    with open(full_path, "r", encoding="utf-8", errors="replace") as sf:
                        code_content = sf.read()
                except Exception:
                    continue

                if not code_content.strip():
                    continue

                lang = detect_language(fname, code_content)
                lang_counts[lang] = lang_counts.get(lang, 0) + 1

                stats = compute_file_stats(code_content, lang)
                total_loc += stats.loc
                total_functions += stats.functions_count
                total_classes += stats.classes_count

                adapter = LanguageRegistry.get(lang)
                if adapter:
                    analysis = adapter.run_full_analysis(code_content, filename=fname)
                    time_comp = analysis.complexity.time
                    all_complexities.append(time_comp)
                    qual_score = analysis.quality.maintainability
                    all_quality_scores.append(qual_score)

                    security_summary["Critical"] += analysis.security.critical
                    security_summary["High"] += analysis.security.high
                    security_summary["Medium"] += analysis.security.medium
                    security_summary["Low"] += analysis.security.low

                    if time_comp in ("O(n²)", "O(n³)", "O(2^n)"):
                        optimizations.append(f"`{rel_path}` contains high complexity {time_comp} ({analysis.complexity.reason})")

                    # Extract dependencies
                    if lang == "python":
                        for line in code_content.splitlines()[:30]:
                            if line.strip().startswith(("import ", "from ")):
                                target = line.strip().split()[1].split(".")[0]
                                dependency_graph.append(DependencyEdge(
                                    source=rel_path,
                                    target=target,
                                    import_statement=line.strip()
                                ))
                    elif lang in ("javascript", "typescript"):
                        for line in code_content.splitlines()[:30]:
                            if "require(" in line or "from " in line:
                                dependency_graph.append(DependencyEdge(
                                    source=rel_path,
                                    target=fname,
                                    import_statement=line.strip()
                                ))

                    files_summary.append(ProjectFileSummary(
                        path=rel_path,
                        filename=fname,
                        language=lang,
                        loc=stats.loc,
                        time_complexity=time_comp,
                        security_issues_count=len(analysis.security.issues),
                        maintainability_score=qual_score,
                        code_snippet=code_content[:1000]
                    ))

    highest_comp = "O(1)"
    for comp in ("O(2^n)", "O(n³)", "O(n²)", "O(n log n)", "O(n)", "O(log n)"):
        if comp in all_complexities:
            highest_comp = comp
            break

    avg_qual = round((sum(all_quality_scores) / len(all_quality_scores)) * 10, 1) if all_quality_scores else 85.0

    return ProjectReportResponse(
        project_name=project_name,
        files_analyzed_count=len(files_summary),
        languages_distribution=lang_counts,
        total_loc=total_loc,
        total_functions=total_functions,
        total_classes=total_classes,
        highest_complexity=highest_comp,
        average_complexity="O(n log n)" if "O(n log n)" in all_complexities or "O(n²)" in all_complexities else "O(n)",
        overall_quality_score=avg_qual,
        security_summary=security_summary,
        optimization_opportunities=optimizations[:10] if optimizations else ["Project architecture exhibits optimal Big-O algorithmic scaling."],
        files=files_summary,
        dependency_graph=dependency_graph[:30]
    )

@router.post("/analyze/upload", response_model=FileUploadResponse)
@router.post("/files/upload", response_model=FileUploadResponse)
async def analyze_uploaded_file(file: UploadFile = File(...)):
    content_bytes = await file.read()
    try:
        code = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        code = content_bytes.decode("latin-1", errors="replace")

    filename = file.filename or "solution.py"
    detected_lang = detect_language(filename, code)
    stats = compute_file_stats(code, detected_lang)

    adapter = LanguageRegistry.get(detected_lang)
    if not adapter:
        raise HTTPException(status_code=400, detail=f"Unsupported language '{detected_lang}'.")

    result = adapter.run_full_analysis(code, filename=filename)

    return FileUploadResponse(
        filename=filename,
        language=detected_lang,
        code=code,
        stats=stats,
        result=result
    )

@router.post("/analyze/project", response_model=ProjectReportResponse)
@router.post("/projects/upload", response_model=ProjectReportResponse)
async def analyze_project_zip(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Project upload requires a .zip archive.")

    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = os.path.join(temp_dir, "project.zip")
        with open(zip_path, "wb") as f:
            f.write(await file.read())

        extract_dir = os.path.join(temp_dir, "extracted")
        os.makedirs(extract_dir, exist_ok=True)

        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid or corrupted ZIP archive: {str(e)}")

        project_name = file.filename.replace(".zip", "")
        return analyze_source_tree(extract_dir, project_name)

@router.post("/projects/github", response_model=ProjectReportResponse)
async def analyze_github_repo(req: GitHubRepoRequest):
    if not req.repo_url.startswith("https://github.com/"):
        raise HTTPException(status_code=400, detail="Invalid GitHub repository URL.")

    with tempfile.TemporaryDirectory() as temp_dir:
        clone_dir = os.path.join(temp_dir, "repo")
        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", "-b", req.branch, req.repo_url, clone_dir],
                check=True,
                capture_output=True,
                timeout=25.0
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to clone GitHub repository: {str(e)}")

        repo_name = req.repo_url.rstrip("/").split("/")[-1]
        return analyze_source_tree(clone_dir, repo_name)
