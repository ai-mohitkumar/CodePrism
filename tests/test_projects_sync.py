import pytest
from fastapi.testclient import TestClient
import sys
import os
import zipfile
import io

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from main import app

client = TestClient(app)

def test_list_cloud_projects():
    response = client.get("/api/projects")
    assert response.status_code == 200
    projects = response.json()
    assert len(projects) >= 2
    ids = [p["id"] for p in projects]
    assert "proj_bubble_sort" in ids

def test_save_and_retrieve_cloud_project():
    new_project = {
        "title": "QuickSort & Benchmark",
        "description": "Divide and conquer sorting algorithm",
        "language": "python",
        "files": [
            {
                "name": "quicksort.py",
                "language": "python",
                "content": "def quicksort(arr): return arr"
            }
        ]
    }
    # Save project
    save_res = client.post("/api/projects/save", json=new_project)
    assert save_res.status_code == 200
    saved = save_res.json()
    pid = saved["id"]
    assert saved["title"] == "QuickSort & Benchmark"
    assert len(saved["files"]) == 1

    # Retrieve project
    get_res = client.get(f"/api/projects/{pid}")
    assert get_res.status_code == 200
    data = get_res.json()
    assert data["id"] == pid
    assert data["files"][0]["name"] == "quicksort.py"

    # Delete project
    del_res = client.delete(f"/api/projects/{pid}")
    assert del_res.status_code == 200

def test_project_versioning_and_snapshot():
    # 1. Check initial version history of bubble sort project
    v_res = client.get("/api/projects/proj_bubble_sort/versions")
    assert v_res.status_code == 200
    versions = v_res.json()
    assert len(versions) >= 1

    # 2. Create a named snapshot milestone
    snap_res = client.post("/api/projects/proj_bubble_sort/versions/snapshot", json={
        "version_tag": "v1.0-Milestone",
        "summary": "Stable sorting algorithm verified"
    })
    assert snap_res.status_code == 200
    snap_data = snap_res.json()
    assert snap_data["version_tag"] == "v1.0-Milestone"
    assert snap_data["project_id"] == "proj_bubble_sort"

    # 3. Verify snapshot is now in version history
    v_res2 = client.get("/api/projects/proj_bubble_sort/versions")
    assert v_res2.status_code == 200
    assert len(v_res2.json()) >= 2
    assert any(v["version_tag"] == "v1.0-Milestone" for v in v_res2.json())

def test_project_version_restore():
    # 1. Create a snapshot before making a change
    snap = client.post("/api/projects/proj_bubble_sort/versions/snapshot", json={
        "version_tag": "Pre-Modification Snapshot",
        "summary": "Code before edits"
    }).json()
    v_id = snap["id"]

    # 2. Modify project files
    client.post("/api/projects/save", json={
        "project_id": "proj_bubble_sort",
        "title": "Bubble Sort Modified",
        "language": "python",
        "files": [{"name": "main.py", "language": "python", "content": "# modified code"}]
    })

    # 3. Restore to snapshot
    restore_res = client.post(f"/api/projects/proj_bubble_sort/versions/{v_id}/restore")
    assert restore_res.status_code == 200
    restored = restore_res.json()
    # Check that restored files contain original bubble sort code
    assert "bubble_sort" in restored["files"][0]["content"]

def test_project_templates():
    res = client.get("/api/projects/templates")
    assert res.status_code == 200
    templates = res.json()
    assert len(templates) >= 3
    langs = [t["language"] for t in templates]
    assert "python" in langs
    assert "cpp" in langs
    assert "java" in langs

def test_project_zip_export():
    res = client.get("/api/projects/proj_bubble_sort/export")
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/zip"
    # Verify valid zip archive
    zf = zipfile.ZipFile(io.BytesIO(res.content))
    namelist = zf.namelist()
    assert "main.py" in namelist
    assert "codeprism.json" in namelist

def test_project_sharing():
    # Share project
    share_res = client.post("/api/projects/proj_bubble_sort/share")
    assert share_res.status_code == 200
    share_data = share_res.json()
    token = share_data["share_token"]
    assert token.startswith("share_")

    # Access shared project
    view_res = client.get(f"/api/projects/shared/{token}")
    assert view_res.status_code == 200
    assert "Bubble Sort" in view_res.json()["title"]
