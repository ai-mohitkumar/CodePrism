import io
import zipfile
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from main import app

client = TestClient(app)

def test_single_file_upload_python():
    code = b"""def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

numbers = [64, 34, 25, 12, 22, 11, 90]
print(bubble_sort(numbers))
"""
    files = {
        'file': ('sort.py', code, 'text/x-python')
    }
    response = client.post("/api/analyze/upload", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "sort.py"
    assert data["language"] == "python"
    assert data["stats"]["loc"] > 0
    assert data["stats"]["functions_count"] == 1
    assert data["result"]["complexity"]["time"] == "O(n²)"
    assert data["result"]["status"] == "success"

def test_single_file_upload_cpp():
    code = b"""#include <iostream>
int main() {
    std::cout << "Uploaded C++ file executed successfully!" << std::endl;
    return 0;
}
"""
    files = {
        'file': ('main.cpp', code, 'text/x-c++src')
    }
    response = client.post("/api/analyze/upload", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "main.cpp"
    assert data["language"] == "cpp"
    assert "Uploaded C++" in data["result"]["execution"]["stdout"]

def test_project_zip_upload():
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('app/main.py', """from utils import helper
def process(data):
    for x in data:
        print(x)
""")
        zf.writestr('app/utils.py', """def helper():
    return 42
""")
        zf.writestr('client/index.js', """function init() {
    console.log("Client loaded");
}
""")

    zip_buffer.seek(0)
    files = {
        'file': ('my_project.zip', zip_buffer.getvalue(), 'application/zip')
    }
    response = client.post("/api/analyze/project", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["project_name"] == "my_project"
    assert data["files_analyzed_count"] == 3
    assert "python" in data["languages_distribution"]
    assert "javascript" in data["languages_distribution"]
    assert data["total_loc"] > 0
    assert len(data["files"]) == 3
    assert len(data["dependency_graph"]) >= 1
