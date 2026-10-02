import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from main import app

client = TestClient(app)

def test_compile_cpp_success():
    cpp_code = """#include <iostream>
int main() {
    std::cout << "Compile Test" << std::endl;
    return 0;
}"""
    response = client.post("/api/compile", json={
        "language": "cpp",
        "code": cpp_code,
        "compiler_flags": ["-O2", "-std=c++17"]
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["target_artifact"] == "prog.exe"
    assert "GCC" in data["compiler_name"]
    assert data["errors_count"] == 0
    assert len(data["ir_bytecode"]) > 0  # Assembly preview available

def test_compile_cpp_syntax_error():
    cpp_code = """#include <iostream>
int main() {
    std::cout << "Missing semicolon"
    return 0;
}"""
    response = client.post("/api/compile", json={
        "language": "cpp",
        "code": cpp_code
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["errors_count"] >= 1
    assert len(data["diagnostics"]) >= 1
    assert data["diagnostics"][0]["line"] == 4 or data["diagnostics"][0]["line"] == 3

def test_compile_java_success():
    java_code = """public class Calculator {
    public static int add(int a, int b) {
        return a + b;
    }
}"""
    response = client.post("/api/compile", json={
        "language": "java",
        "code": java_code
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["target_artifact"] == "Calculator.class"
    assert "javac" in data["compiler_name"] or "Java" in data["compiler_name"]

def test_execute_java_multi_class_and_package():
    java_code = """package com.codeprism.demo;
class Helper {
    static int multiply(int x) { return x * 3; }
}
public class Main {
    public static void main(String[] args) {
        System.out.println("Result: " + Helper.multiply(7));
    }
}"""
    response = client.post("/api/execute", json={
        "language": "java",
        "code": java_code
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "Result: 21" in data["execution"]["stdout"]

def test_analyze_java_ast():
    java_code = """class Node { int val; }
public class Main {
    public static void main(String[] args) {
        for (int i = 0; i < 5; i++) {
            System.out.println(i);
        }
    }
}"""
    response = client.post("/api/analyze/ast", json={
        "language": "java",
        "code": java_code
    })
    assert response.status_code == 200
    data = response.json()
    assert data["root"] is not None
    assert len(data["root"]["children"]) >= 2
    assert any("Main" in s or "Node" in s for s in data["summary"])

def test_compile_python_disassembly():
    py_code = """def multiply(x, y):
    return x * y
"""
    response = client.post("/api/compile", json={
        "language": "python",
        "code": py_code
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["target_artifact"] == "program.pyc"
    assert "BINARY_OP" in data["ir_bytecode"] or "LOAD_FAST" in data["ir_bytecode"]

