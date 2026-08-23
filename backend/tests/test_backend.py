import pytest
from app.engines.python_engine import PythonLanguageEngine
from app.engines.cpp_engine import CppLanguageEngine
from app.engines.java_engine import JavaLanguageEngine
from app.engines.javascript_engine import JavaScriptLanguageEngine
from app.analyzers.complexity import ComplexityAnalyzer
from app.analyzers.line_analyzer import LineAnalyzer
from app.analyzers.security import SecurityScanner
from app.analyzers.quality import QualityAuditor
from app.profiler.executor import CodeExecutor

def test_python_big_o_linear():
    code = """
def find_max(arr):
    m = arr[0]
    for x in arr:
        if x > m:
            m = x
    return m
"""
    result = ComplexityAnalyzer.analyze_python_ast(code)
    assert result.time_complexity == "O(n)"
    assert result.space_complexity == "O(1)"
    assert result.nested_depth == 1

def test_python_big_o_quadratic():
    code = """
def count_pairs(arr):
    c = 0
    for i in range(len(arr)):
        for j in range(len(arr)):
            if arr[i] == arr[j]:
                c += 1
    return c
"""
    result = ComplexityAnalyzer.analyze_python_ast(code)
    assert result.time_complexity == "O(n^2)"
    assert result.nested_depth == 2

def test_python_big_o_logarithmic():
    code = """
def binary_search(arr, target):
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
    result = ComplexityAnalyzer.analyze_python_ast(code)
    assert result.time_complexity == "O(log n)"
    assert result.has_halving is True

def test_python_big_o_exponential():
    code = """
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)
"""
    result = ComplexityAnalyzer.analyze_python_ast(code)
    assert result.time_complexity == "O(2^n)"
    assert result.recursion_found is True

def test_python_syntax_error_pointer():
    engine = PythonLanguageEngine()
    code = """def calculate(a, b):
    result = a + b
    print(result

calculate(10, 20)"""
    exec_res = engine.execute(code)
    assert exec_res.status == "compilation_error"
    assert exec_res.error_line == 3
    assert exec_res.suggested_fix is not None

def test_python_execution_success():
    engine = PythonLanguageEngine()
    code = "print(10 + 25)"
    exec_res = engine.execute(code)
    assert exec_res.status == "success"
    assert "35" in exec_res.stdout
    assert exec_res.execution_time_sec > 0
    assert exec_res.peak_memory_mb > 0

def test_security_scanner_eval():
    code = """
user_inp = "2 + 2"
val = eval(user_inp)
"""
    issues = SecurityScanner.audit_python(code)
    assert len(issues) >= 1
    assert any(i.severity == "Critical" and "eval" in i.title for i in issues)

def test_cpp_engine_execution():
    engine = CppLanguageEngine()
    code = """#include <iostream>
int main() {
    std::cout << "Hello from C++ CodePrism!" << std::endl;
    return 0;
}
"""
    exec_res = engine.execute(code)
    assert exec_res.status == "success"
    assert "Hello from C++ CodePrism!" in exec_res.stdout

def test_java_engine_execution():
    engine = JavaLanguageEngine()
    code = """public class Main {
    public static void main(String[] args) {
        System.out.println("Hello from Java CodePrism!");
    }
}
"""
    exec_res = engine.execute(code)
    assert exec_res.status == "success"
    assert "Hello from Java CodePrism!" in exec_res.stdout

def test_javascript_engine_execution():
    engine = JavaScriptLanguageEngine()
    code = "console.log(Array.from({length: 5}, (_, i) => i * 2).join(', '));"
    exec_res = engine.execute(code)
    assert exec_res.status == "success"
    assert "0, 2, 4, 6, 8" in exec_res.stdout
