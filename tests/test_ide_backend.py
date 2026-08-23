import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from main import app

client = TestClient(app)

def test_api_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "CodePrism" in data["service"]

def test_execute_python():
    response = client.post("/api/execute", json={
        "language": "python",
        "code": "print('Hello CodePrism')"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "Hello CodePrism" in data["execution"]["stdout"]
    assert data["execution"]["runtime_ms"] > 0
    assert data["execution"]["memory_mb"] > 0

def test_execute_cpp():
    response = client.post("/api/execute", json={
        "language": "cpp",
        "code": """#include <iostream>
int main() {
    std::cout << "C++ Native Works!" << std::endl;
    return 0;
}"""
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "C++ Native Works!" in data["execution"]["stdout"]

def test_execute_javascript():
    response = client.post("/api/execute", json={
        "language": "javascript",
        "code": "console.log(2 + 3 * 4);"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "14" in data["execution"]["stdout"]

def test_error_diagnosis_ascii_pointer():
    code = """for i in range(10)
    print(i)"""
    response = client.post("/api/analyze/errors", json={
        "language": "python",
        "code": code
    })
    assert response.status_code == 200
    data = response.json()
    assert data["has_error"] is True
    assert data["line"] == 1
    assert data["pointer"] is not None
    assert data["suggested_fix"] == "for i in range(10):"

def test_ast_analysis():
    code = """def square(x):
    return x * x

for i in range(5):
    print(square(i))
"""
    response = client.post("/api/analyze/ast", json={
        "language": "python",
        "code": code
    })
    assert response.status_code == 200
    data = response.json()
    assert data["root"] is not None
    assert len(data["root"]["children"]) >= 2
    assert any("square" in str(c) for c in data["root"]["children"])

def test_complexity_linear_and_nested():
    # Linear
    r1 = client.post("/api/analyze/complexity", json={
        "language": "python",
        "code": "for x in arr: print(x)"
    })
    assert r1.status_code == 200
    assert r1.json()["time_complexity"] == "O(n)"

    # Nested
    r2 = client.post("/api/analyze/complexity", json={
        "language": "python",
        "code": "for i in range(n):\n    for j in range(n):\n        pass"
    })
    assert r2.status_code == 200
    assert r2.json()["time_complexity"] == "O(n²)"
    assert r2.json()["confidence"] >= 0.90

def test_debug_step():
    code = """a = 10
b = 20
c = a + b
print(c)
"""
    response = client.post("/api/debug/step", json={
        "language": "python",
        "code": code,
        "line_number": 1,
        "breakpoints": [3],
        "variables": {}
    })
    assert response.status_code == 200
    data = response.json()
    assert "a" in data["variables"]
    assert data["variables"]["a"] == 10

def test_ai_assistant_explain():
    response = client.post("/api/ai/assistant", json={
        "language": "python",
        "code": "def find_max(arr): return max(arr)",
        "prompt_type": "explain"
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data["title"]) > 0
    assert len(data["bullet_points"]) > 0
