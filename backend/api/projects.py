import os
import io
import time
import uuid
import zipfile
import json
from typing import List, Dict, Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/projects", tags=["Cloud Projects, Versioning & Sync"])

class ProjectFile(BaseModel):
    name: str
    language: str
    content: str

class SaveProjectRequest(BaseModel):
    project_id: Optional[str] = None
    title: str = Field(..., description="Project name")
    description: Optional[str] = ""
    language: str = "python"
    files: List[ProjectFile] = []
    is_autosave: Optional[bool] = False

class ProjectMetadata(BaseModel):
    id: str
    title: str
    description: str
    language: str
    files_count: int
    updated_at: float
    created_at: float
    versions_count: int = 1

class ProjectDetails(BaseModel):
    id: str
    title: str
    description: str
    language: str
    files: List[ProjectFile]
    updated_at: float
    created_at: float
    versions_count: int = 1

class ProjectVersion(BaseModel):
    id: str
    project_id: str
    version_tag: str
    summary: str
    files_count: int
    total_loc: int
    created_at: float
    files: List[ProjectFile]

class CreateSnapshotRequest(BaseModel):
    version_tag: str = Field(default="Manual Snapshot", description="Version label")
    summary: Optional[str] = ""

class ShareProjectResponse(BaseModel):
    share_token: str
    share_url: str
    project_title: str
    language: str
    created_at: float

class ProjectTemplate(BaseModel):
    id: str
    title: str
    description: str
    language: str
    difficulty: str
    category: str
    files: List[Dict[str, str]]

# In-memory storage with version history and shared links
PROJECTS_STORE: Dict[str, Dict] = {
    "proj_bubble_sort": {
        "id": "proj_bubble_sort",
        "title": "Bubble Sort & Complexity Analysis",
        "description": "Standard sorting algorithm with O(n²) comparison profiling",
        "language": "python",
        "files": [
            {
                "name": "main.py",
                "language": "python",
                "content": """def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

numbers = [64, 34, 25, 12, 22, 11, 90]
print("Sorted Array:", bubble_sort(numbers))
"""
            },
            {
                "name": "tests.py",
                "language": "python",
                "content": """from main import bubble_sort

def test_sort():
    assert bubble_sort([3, 2, 1]) == [1, 2, 3]
    assert bubble_sort([]) == []
    print("All unit tests passed!")

if __name__ == "__main__":
    test_sort()
"""
            }
        ],
        "created_at": time.time() - 3600,
        "updated_at": time.time() - 3600
    },
    "proj_cpp_matrix": {
        "id": "proj_cpp_matrix",
        "title": "C++ High Performance Vector Scan",
        "description": "Native C++ GCC benchmark with vector traversal",
        "language": "cpp",
        "files": [
            {
                "name": "solution.cpp",
                "language": "cpp",
                "content": """#include <iostream>
#include <vector>

int findMax(const std::vector<int>& arr) {
    int maxVal = arr[0];
    for (int x : arr) {
        if (x > maxVal) maxVal = x;
    }
    return maxVal;
}

int main() {
    std::vector<int> numbers = {10, 20, 5, 30, 99, 42};
    std::cout << "Maximum element: " << findMax(numbers) << std::endl;
    return 0;
}
"""
            }
        ],
        "created_at": time.time() - 1800,
        "updated_at": time.time() - 1800
    }
}

# Version Snapshots: project_id -> List[ProjectVersionDict]
PROJECT_VERSIONS: Dict[str, List[Dict]] = {
    "proj_bubble_sort": [
        {
            "id": "ver_init_1",
            "project_id": "proj_bubble_sort",
            "version_tag": "Initial Commit",
            "summary": "Project initialized with sorting algorithm",
            "files": PROJECTS_STORE["proj_bubble_sort"]["files"],
            "files_count": 2,
            "total_loc": 25,
            "created_at": time.time() - 3600
        }
    ],
    "proj_cpp_matrix": [
        {
            "id": "ver_init_2",
            "project_id": "proj_cpp_matrix",
            "version_tag": "Initial Commit",
            "summary": "C++ Vector scanner initialization",
            "files": PROJECTS_STORE["proj_cpp_matrix"]["files"],
            "files_count": 1,
            "total_loc": 18,
            "created_at": time.time() - 1800
        }
    ]
}

# Shareable tokens: token -> project_id
SHARED_PROJECTS: Dict[str, str] = {}

# Built-in Starter Templates
STARTER_TEMPLATES: List[ProjectTemplate] = [
    ProjectTemplate(
        id="tmpl_py_algorithms",
        title="Algorithms & Big-O Benchmark",
        description="Multi-file sorting and binary search implementations with unit tests",
        language="python",
        difficulty="Intermediate",
        category="Data Structures & Algorithms",
        files=[
            {
                "name": "main.py",
                "language": "python",
                "content": """import time
from search import binary_search

def linear_scan(arr, target):
    for i, x in enumerate(arr):
        if x == target:
            return i
    return -1

numbers = list(range(1, 100000))
target = 99995

# Benchmark
idx = binary_search(numbers, target)
print(f"Target {target} found at index: {idx}")
"""
            },
            {
                "name": "search.py",
                "language": "python",
                "content": """def binary_search(arr, target):
    low = 0
    high = len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1
"""
            }
        ]
    ),
    ProjectTemplate(
        id="tmpl_cpp_graph",
        title="Graph BFS / DFS Traversal",
        description="Graph adjacency list traversal using modern C++17 STL",
        language="cpp",
        difficulty="Advanced",
        category="Graph Algorithms",
        files=[
            {
                "name": "main.cpp",
                "language": "cpp",
                "content": """#include <iostream>
#include <vector>
#include <queue>

void bfs(int start, const std::vector<std::vector<int>>& adj) {
    std::vector<bool> visited(adj.size(), false);
    std::queue<int> q;
    visited[start] = true;
    q.push(start);

    std::cout << "BFS Order: ";
    while (!q.empty()) {
        int u = q.front();
        q.pop();
        std::cout << u << " ";
        for (int v : adj[u]) {
            if (!visited[v]) {
                visited[v] = true;
                q.push(v);
            }
        }
    }
    std::cout << std::endl;
}

int main() {
    std::vector<std::vector<int>> adj = {
        {1, 2},
        {0, 3, 4},
        {0, 4},
        {1, 5},
        {1, 2, 5},
        {3, 4}
    };
    bfs(0, adj);
    return 0;
}
"""
            }
        ]
    ),
    ProjectTemplate(
        id="tmpl_java_bst",
        title="Binary Search Tree (OOP)",
        description="Clean Object-Oriented Java 25 BST with in-order traversal",
        language="java",
        difficulty="Intermediate",
        category="Tree Structures",
        files=[
            {
                "name": "Main.java",
                "language": "java",
                "content": """class Node {
    int val;
    Node left, right;
    Node(int v) { val = v; }
}

public class Main {
    static Node insert(Node root, int val) {
        if (root == null) return new Node(val);
        if (val < root.val) root.left = insert(root.left, val);
        else root.right = insert(root.right, val);
        return root;
    }

    static void inOrder(Node root) {
        if (root != null) {
            inOrder(root.left);
            System.out.print(root.val + " ");
            inOrder(root.right);
        }
    }

    public static void main(String[] args) {
        int[] vals = {50, 30, 20, 40, 70, 60, 80};
        Node root = null;
        for (int v : vals) root = insert(root, v);
        System.out.print("In-Order Traversal: ");
        inOrder(root);
        System.out.println();
    }
}
"""
            }
        ]
    ),
    ProjectTemplate(
        id="tmpl_ts_async",
        title="Async Event Pipeline",
        description="TypeScript Promise concurrency and batch transformer",
        language="typescript",
        difficulty="Beginner",
        category="Web & Backend",
        files=[
            {
                "name": "server.ts",
                "language": "typescript",
                "content": """interface EventItem {
    id: string;
    payload: string;
    timestamp: number;
}

async function processEvents(events: EventItem[]): Promise<number> {
    let processed = 0;
    for (const evt of events) {
        await new Promise((r) => setTimeout(r, 10));
        processed++;
    }
    return processed;
}

const batch: EventItem[] = [
    { id: "e1", payload: "UserLogin", timestamp: Date.now() },
    { id: "e2", payload: "CodeCompile", timestamp: Date.now() }
];

processEvents(batch).then(count => console.log(`Processed ${count} events cleanly.`));
"""
            }
        ]
    )
]

def calculate_total_loc(files: List[Dict]) -> int:
    return sum(len(f.get("content", "").split("\n")) for f in files)

# --- ROUTES ---

@router.get("", response_model=List[ProjectMetadata])
def list_projects():
    """Lists all cloud projects with version snapshot counts."""
    res = []
    for pid, p in PROJECTS_STORE.items():
        v_count = len(PROJECT_VERSIONS.get(pid, []))
        res.append(ProjectMetadata(
            id=p["id"],
            title=p["title"],
            description=p.get("description", ""),
            language=p.get("language", "python"),
            files_count=len(p.get("files", [])),
            updated_at=p.get("updated_at", time.time()),
            created_at=p.get("created_at", time.time()),
            versions_count=max(1, v_count)
        ))
    res.sort(key=lambda x: x.updated_at, reverse=True)
    return res

@router.get("/templates", response_model=List[ProjectTemplate])
def get_project_templates():
    """Returns curated starter project templates across multiple languages."""
    return STARTER_TEMPLATES

@router.get("/{project_id}", response_model=ProjectDetails)
def get_project(project_id: str):
    """Retrieves full project with multi-file workspace source code."""
    if project_id not in PROJECTS_STORE:
        raise HTTPException(status_code=404, detail="Project not found.")
    p = PROJECTS_STORE[project_id]
    v_count = len(PROJECT_VERSIONS.get(project_id, []))
    return ProjectDetails(
        id=p["id"],
        title=p["title"],
        description=p.get("description", ""),
        language=p.get("language", "python"),
        files=[ProjectFile(**f) for f in p.get("files", [])],
        updated_at=p.get("updated_at", time.time()),
        created_at=p.get("created_at", time.time()),
        versions_count=max(1, v_count)
    )

@router.post("/save", response_model=ProjectDetails)
def save_project(req: SaveProjectRequest):
    """Creates or updates a cloud project with automatic real-time autosave & revision tracking."""
    now = time.time()
    pid = req.project_id or f"proj_{int(now * 1000)}"
    
    created_at = PROJECTS_STORE[pid]["created_at"] if pid in PROJECTS_STORE else now
    raw_files = [f.model_dump() for f in req.files]

    project_data = {
        "id": pid,
        "title": req.title,
        "description": req.description or "",
        "language": req.language,
        "files": raw_files,
        "created_at": created_at,
        "updated_at": now
    }
    PROJECTS_STORE[pid] = project_data

    # Record automatic version snapshot
    if pid not in PROJECT_VERSIONS:
        PROJECT_VERSIONS[pid] = []

    last_v = PROJECT_VERSIONS[pid][-1] if PROJECT_VERSIONS[pid] else None
    if not last_v or (now - last_v["created_at"]) > 30 or not req.is_autosave:
        tag = "Autosave" if req.is_autosave else "Manual Save"
        v_entry = {
            "id": f"ver_{uuid.uuid4().hex[:8]}",
            "project_id": pid,
            "version_tag": tag,
            "summary": f"{tag} with {len(raw_files)} file(s)",
            "files": raw_files,
            "files_count": len(raw_files),
            "total_loc": calculate_total_loc(raw_files),
            "created_at": now
        }
        PROJECT_VERSIONS[pid].append(v_entry)
        if len(PROJECT_VERSIONS[pid]) > 25:
            PROJECT_VERSIONS[pid] = PROJECT_VERSIONS[pid][-25:]

    return ProjectDetails(
        id=pid,
        title=req.title,
        description=req.description or "",
        language=req.language,
        files=req.files,
        updated_at=now,
        created_at=created_at,
        versions_count=len(PROJECT_VERSIONS.get(pid, []))
    )

# --- VERSIONING / SNAPSHOTS ---

@router.get("/{project_id}/versions", response_model=List[ProjectVersion])
def get_project_versions(project_id: str):
    """Retrieves full version history / revision snapshots for a project."""
    if project_id not in PROJECTS_STORE:
        raise HTTPException(status_code=404, detail="Project not found.")
    versions = PROJECT_VERSIONS.get(project_id, [])
    res = []
    for v in reversed(versions):
        res.append(ProjectVersion(
            id=v["id"],
            project_id=v["project_id"],
            version_tag=v["version_tag"],
            summary=v["summary"],
            files_count=v["files_count"],
            total_loc=v["total_loc"],
            created_at=v["created_at"],
            files=[ProjectFile(**f) for f in v["files"]]
        ))
    return res

@router.post("/{project_id}/versions/snapshot", response_model=ProjectVersion)
def create_project_snapshot(project_id: str, req: CreateSnapshotRequest):
    """Creates a named milestone snapshot (e.g. 'v1.0 Milestone', 'Before Refactor')."""
    if project_id not in PROJECTS_STORE:
        raise HTTPException(status_code=404, detail="Project not found.")
    
    p = PROJECTS_STORE[project_id]
    now = time.time()
    raw_files = p.get("files", [])
    
    v_entry = {
        "id": f"snap_{uuid.uuid4().hex[:8]}",
        "project_id": project_id,
        "version_tag": req.version_tag or "Named Snapshot",
        "summary": req.summary or "Milestone snapshot created by user",
        "files": raw_files,
        "files_count": len(raw_files),
        "total_loc": calculate_total_loc(raw_files),
        "created_at": now
    }
    
    if project_id not in PROJECT_VERSIONS:
        PROJECT_VERSIONS[project_id] = []
    
    PROJECT_VERSIONS[project_id].append(v_entry)
    
    return ProjectVersion(
        id=v_entry["id"],
        project_id=v_entry["project_id"],
        version_tag=v_entry["version_tag"],
        summary=v_entry["summary"],
        files_count=v_entry["files_count"],
        total_loc=v_entry["total_loc"],
        created_at=v_entry["created_at"],
        files=[ProjectFile(**f) for f in v_entry["files"]]
    )

@router.post("/{project_id}/versions/{version_id}/restore", response_model=ProjectDetails)
def restore_project_version(project_id: str, version_id: str):
    """Restores the project code to a previous snapshot."""
    if project_id not in PROJECTS_STORE:
        raise HTTPException(status_code=404, detail="Project not found.")
    
    versions = PROJECT_VERSIONS.get(project_id, [])
    target_v = next((v for v in versions if v["id"] == version_id), None)
    if not target_v:
        raise HTTPException(status_code=404, detail="Version snapshot not found.")
    
    now = time.time()
    curr_files = PROJECTS_STORE[project_id]["files"]
    PROJECT_VERSIONS[project_id].append({
        "id": f"ver_prerestore_{uuid.uuid4().hex[:8]}",
        "project_id": project_id,
        "version_tag": "Pre-Restore Safety Point",
        "summary": f"Automatic snapshot prior to restoring {target_v['version_tag']}",
        "files": curr_files,
        "files_count": len(curr_files),
        "total_loc": calculate_total_loc(curr_files),
        "created_at": now
    })

    PROJECTS_STORE[project_id]["files"] = target_v["files"]
    PROJECTS_STORE[project_id]["updated_at"] = now

    return ProjectDetails(
        id=project_id,
        title=PROJECTS_STORE[project_id]["title"],
        description=PROJECTS_STORE[project_id]["description"],
        language=PROJECTS_STORE[project_id]["language"],
        files=[ProjectFile(**f) for f in target_v["files"]],
        updated_at=now,
        created_at=PROJECTS_STORE[project_id]["created_at"],
        versions_count=len(PROJECT_VERSIONS.get(project_id, []))
    )

# --- EXPORT & SHARING ---

@router.get("/{project_id}/export")
def export_project_zip(project_id: str):
    """Exports the entire project as a clean .zip download."""
    if project_id not in PROJECTS_STORE:
        raise HTTPException(status_code=404, detail="Project not found.")
    
    p = PROJECTS_STORE[project_id]
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in p.get("files", []):
            zf.writestr(f["name"], f["content"])
        meta = {
            "title": p["title"],
            "language": p["language"],
            "exported_at": time.time(),
            "generator": "CodePrism Universal Cloud Compiler"
        }
        zf.writestr("codeprism.json", json.dumps(meta, indent=2))
    
    buffer.seek(0)
    filename = f"{p['title'].lower().replace(' ', '_')}.zip"
    return StreamingResponse(
        buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.post("/{project_id}/share", response_model=ShareProjectResponse)
def share_project(project_id: str):
    """Generates a shareable portfolio link for the project."""
    if project_id not in PROJECTS_STORE:
        raise HTTPException(status_code=404, detail="Project not found.")
    
    token = f"share_{uuid.uuid4().hex[:10]}"
    SHARED_PROJECTS[token] = project_id
    p = PROJECTS_STORE[project_id]
    
    return ShareProjectResponse(
        share_token=token,
        share_url=f"/share/{token}",
        project_title=p["title"],
        language=p["language"],
        created_at=time.time()
    )

@router.get("/shared/{share_token}", response_model=ProjectDetails)
def get_shared_project(share_token: str):
    """Public read endpoint to view and run shared projects."""
    if share_token not in SHARED_PROJECTS:
        raise HTTPException(status_code=404, detail="Shared link expired or not found.")
    
    project_id = SHARED_PROJECTS[share_token]
    return get_project(project_id)

@router.delete("/{project_id}")
def delete_project(project_id: str):
    if project_id in PROJECTS_STORE:
        del PROJECTS_STORE[project_id]
        if project_id in PROJECT_VERSIONS:
            del PROJECT_VERSIONS[project_id]
        return {"success": True, "message": "Project and revision history deleted."}
    raise HTTPException(status_code=404, detail="Project not found.")
