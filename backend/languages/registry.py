from typing import Dict, List, Optional
from languages.base import BaseLanguageAdapter
from languages.python.adapter import PythonAdapter
from languages.cpp.adapter import CppAdapter
from languages.java.adapter import JavaAdapter
from languages.javascript.adapter import JavaScriptAdapter
from languages.typescript.adapter import TypeScriptAdapter
from languages.csharp.adapter import CSharpAdapter
from languages.rust.adapter import RustAdapter
from languages.go.adapter import GoAdapter
from languages.adapters_tier import (
    KotlinAdapter, SwiftAdapter, PHPAdapter,
    RubyAdapter, DartAdapter, RAdapter, SQLAdapter
)
from models import LanguageMetadata

class LanguageRegistry:
    _adapters: Dict[str, BaseLanguageAdapter] = {}

    @classmethod
    def initialize(cls):
        adapters = [
            PythonAdapter(),
            CppAdapter(),
            JavaAdapter(),
            JavaScriptAdapter(),
            TypeScriptAdapter(),
            CSharpAdapter(),
            RustAdapter(),
            GoAdapter(),
            KotlinAdapter(),
            SwiftAdapter(),
            PHPAdapter(),
            RubyAdapter(),
            DartAdapter(),
            RAdapter(),
            SQLAdapter()
        ]
        for a in adapters:
            cls._adapters[a.lang_id] = a

    @classmethod
    def get(cls, lang_id: str) -> Optional[BaseLanguageAdapter]:
        if not cls._adapters:
            cls.initialize()
        clean_id = lang_id.lower().strip()
        # Aliases
        alias_map = {
            "py": "python",
            "c++": "cpp",
            "c": "cpp",
            "js": "javascript",
            "ts": "typescript",
            "cs": "csharp",
            "c#": "csharp",
            "rs": "rust",
            "golang": "go",
            "kt": "kotlin",
            "rb": "ruby"
        }
        clean_id = alias_map.get(clean_id, clean_id)
        return cls._adapters.get(clean_id, cls._adapters.get("python"))

    @classmethod
    def list_metadata(cls) -> List[LanguageMetadata]:
        if not cls._adapters:
            cls.initialize()
        result = []
        for a in cls._adapters.values():
            result.append(LanguageMetadata(
                id=a.lang_id,
                name=a.name,
                tier=a.tier,
                family=a.family,
                extension=a.extension,
                icon=a.icon,
                is_installed=a.is_installed(),
                version=a.get_version(),
                capabilities=["Compilation", "Execution", "Static AST", "Big-O Complexity", "Security Audit", "Quality Scoring"]
            ))
        return result

    @classmethod
    def get_templates(cls) -> Dict[str, Dict[str, str]]:
        return {
            "python": {
                "find_max": '''def find_max(arr):
    maximum = arr[0]
    for x in arr:
        if x > maximum:
            maximum = x
    return maximum

numbers = [10, 20, 5, 30]
print(f"Maximum element: {find_max(numbers)}")
''',
                "nested_loops": '''def count_pairs(data):
    count = 0
    # O(n^2) Quadratic nested iterations
    for i in range(len(data)):
        for j in range(len(data)):
            if data[i] == data[j] and i != j:
                count += 1
    return count

numbers = [1, 2, 3, 2, 1, 4, 5, 3]
print(f"Duplicate pairs count: {count_pairs(numbers)}")
''',
                "syntax_error": '''for i in range(10)
    print(i)
'''
            },
            "cpp": {
                "find_max": '''#include <iostream>
#include <vector>

int findMax(const std::vector<int>& arr) {
    int maxVal = arr[0];
    for (int x : arr) {
        if (x > maxVal) maxVal = x;
    }
    return maxVal;
}

int main() {
    std::vector<int> numbers = {10, 20, 5, 30};
    std::cout << "Maximum element: " << findMax(numbers) << std::endl;
    return 0;
}
''',
                "syntax_error": '''#include <iostream>
int main() {
    int x = 10
    std::cout << x << std::endl;
    return 0;
}
'''
            },
            "java": {
                "find_max": '''public class Main {
    public static int findMax(int[] arr) {
        int max = arr[0];
        for (int x : arr) {
            if (x > max) max = x;
        }
        return max;
    }

    public static void main(String[] args) {
        int[] numbers = {10, 20, 5, 30};
        System.out.println("Maximum element: " + findMax(numbers));
    }
}
''',
                "nested_loops": '''public class Main {
    public static int countPairs(int[] data) {
        int count = 0;
        // O(n^2) Quadratic nested iterations
        for (int i = 0; i < data.length; i++) {
            for (int j = 0; j < data.length; j++) {
                if (data[i] == data[j] && i != j) {
                    count++;
                }
            }
        }
        return count;
    }

    public static void main(String[] args) {
        int[] numbers = {1, 2, 3, 2, 1, 4, 5, 3};
        System.out.println("Duplicate pairs count: " + countPairs(numbers));
    }
}
''',
                "syntax_error": '''public class Main {
    public static void main(String[] args) {
        int x = 10
        System.out.println(x);
    }
}
'''
            },
            "javascript": {
                "find_max": '''function findMax(arr) {
    let maximum = arr[0];
    for (let i = 0; i < arr.length; i++) {
        if (arr[i] > maximum) maximum = arr[i];
    }
    return maximum;
}

const numbers = [10, 20, 5, 30];
console.log("Maximum element:", findMax(numbers));
''',
                "syntax_error": '''function calculate(a, b) {
    let result = a + b
    console.log(result
}
calculate(10, 20);
'''
            },
            "typescript": {
                "find_max": '''function findMax(arr: number[]): number {
    let maximum = arr[0];
    for (const x of arr) {
        if (x > maximum) maximum = x;
    }
    return maximum;
}

const numbers: number[] = [10, 20, 5, 30];
console.log("Maximum element:", findMax(numbers));
'''
            },
            "csharp": {
                "find_max": '''using System;

class Program {
    static int FindMax(int[] arr) {
        int max = arr[0];
        foreach (int x in arr) {
            if (x > max) max = x;
        }
        return max;
    }

    static void Main() {
        int[] numbers = {10, 20, 5, 30};
        Console.WriteLine($"Maximum element: {FindMax(numbers)}");
    }
}
'''
            },
            "rust": {
                "find_max": '''fn find_max(arr: &[i32]) -> i32 {
    let mut max = arr[0];
    for &x in arr {
        if x > max { max = x; }
    }
    max
}

fn main() {
    let numbers = [10, 20, 5, 30];
    println!("Maximum element: {}", find_max(&numbers));
}
'''
            },
            "go": {
                "find_max": '''package main

import "fmt"

func findMax(arr []int) int {
    max := arr[0]
    for _, x := range arr {
        if x > max {
            max = x
        }
    }
    return max
}

func main() {
    numbers := []int{10, 20, 5, 30}
    fmt.Printf("Maximum element: %d\\n", findMax(numbers))
}
'''
            },
            "sql": {
                "find_max": '''CREATE TABLE employees (id INT PRIMARY KEY, name TEXT, salary INT);
INSERT INTO employees VALUES (1, 'Alice', 95000), (2, 'Bob', 120000), (3, 'Charlie', 88000);

SELECT name, salary FROM employees WHERE salary > 90000 ORDER BY salary DESC;
'''
            }
        }
