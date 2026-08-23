import pytest
import time
from fastapi.testclient import TestClient
import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from main import app

client = TestClient(app)

def test_universal_languages_registry():
    response = client.get("/api/languages")
    assert response.status_code == 200
    data = response.json()
    assert len(data["languages"]) >= 15
    ids = [l["id"] for l in data["languages"]]
    for expected in ("python", "cpp", "java", "javascript", "typescript", "csharp", "rust", "go", "sql"):
        assert expected in ids

def test_execute_java():
    java_code = """public class Main {
    public static void main(String[] args) {
        System.out.println("Java Cloud Adapter Works!");
    }
}"""
    response = client.post("/api/execute", json={
        "language": "java",
        "code": java_code
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "Java Cloud Adapter Works!" in data["execution"]["stdout"]

def test_execute_csharp():
    cs_code = """using System;
class Program {
    static void Main() {
        Console.WriteLine("C# .NET 9 Runner Active!");
    }
}"""
    response = client.post("/api/execute", json={
        "language": "csharp",
        "code": cs_code
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "C# .NET 9 Runner Active!" in data["execution"]["stdout"]

def test_execute_typescript():
    ts_code = "const nums: number[] = [1, 2, 3]; console.log('Sum:', nums.reduce((a, b) => a + b, 0));"
    response = client.post("/api/execute", json={
        "language": "typescript",
        "code": ts_code
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "Sum: 6" in data["execution"]["stdout"]

def test_execute_sql():
    sql_code = """CREATE TABLE items (id INT, name TEXT);
INSERT INTO items VALUES (1, 'Prism'), (2, 'Analyzer');
SELECT * FROM items;"""
    response = client.post("/api/execute", json={
        "language": "sql",
        "code": sql_code
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "Prism" in data["execution"]["stdout"]

def test_job_queue_workflow():
    # Submit job
    submit_res = client.post("/api/jobs/submit", json={
        "language": "python",
        "code": "print('Async Job Completed!')"
    })
    assert submit_res.status_code == 200
    job_id = submit_res.json()["job_id"]
    assert job_id.startswith("cp_")

    # Poll status until completed
    completed = False
    for _ in range(20):
        status_res = client.get(f"/api/jobs/{job_id}")
        assert status_res.status_code == 200
        status_data = status_res.json()
        if status_data["status"] == "completed":
            assert status_data["result"] is not None
            assert "Async Job Completed!" in status_data["result"]["execution"]["stdout"]
            completed = True
            break
        time.sleep(0.05)

    assert completed is True
