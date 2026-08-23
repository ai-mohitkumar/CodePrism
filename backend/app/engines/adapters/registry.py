from typing import Dict, List, Any
from app.engines.python_engine import PythonLanguageEngine
from app.engines.cpp_engine import CppLanguageEngine
from app.engines.java_engine import JavaLanguageEngine
from app.engines.javascript_engine import JavaScriptLanguageEngine
from app.engines.adapters.csharp_adapter import CSharpAdapter
from app.engines.adapters.ts_adapter import TypeScriptAdapter
from app.engines.adapters.rust_adapter import RustAdapter
from app.engines.adapters.go_adapter import GoAdapter
from app.engines.adapters.script_adapters import (
    KotlinAdapter, PHPAdapter, RubyAdapter, DartAdapter, RAdapter, SwiftAdapter
)
from app.engines.adapters.sql_adapter import SQLAdapter
from app.engines.base import BaseLanguageEngine

# Global registry of language adapters
LANGUAGE_ADAPTERS: Dict[str, BaseLanguageEngine] = {
    # Tier 1 - Essential
    "python": PythonLanguageEngine(),
    "py": PythonLanguageEngine(),
    "cpp": CppLanguageEngine(),
    "c++": CppLanguageEngine(),
    "c": CppLanguageEngine(),
    "java": JavaLanguageEngine(),
    "javascript": JavaScriptLanguageEngine(),
    "js": JavaScriptLanguageEngine(),
    "typescript": TypeScriptAdapter(),
    "ts": TypeScriptAdapter(),
    "csharp": CSharpAdapter(),
    "cs": CSharpAdapter(),
    "rust": RustAdapter(),
    "rs": RustAdapter(),
    "go": GoAdapter(),
    "golang": GoAdapter(),
    "kotlin": KotlinAdapter(),
    "kt": KotlinAdapter(),
    "php": PHPAdapter(),
    "ruby": RubyAdapter(),
    "rb": RubyAdapter(),
    "dart": DartAdapter(),
    "r": RAdapter(),
    "swift": SwiftAdapter(),
    # Tier 3 - Special Purpose
    "sql": SQLAdapter()
}

TEMPLATES: Dict[str, Dict[str, str]] = {
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
        "binary_search": '''def binary_search(arr, target):
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

data = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]
print(f"Element 23 found at index: {binary_search(data, 23)}")
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
'''
    },
    "c": {
        "find_max": '''#include <stdio.h>

int findMax(int arr[], int n) {
    int maxVal = arr[0];
    for (int i = 1; i < n; i++) {
        if (arr[i] > maxVal) maxVal = arr[i];
    }
    return maxVal;
}

int main() {
    int numbers[] = {10, 20, 5, 30};
    int n = sizeof(numbers) / sizeof(numbers[0]);
    printf("Maximum element: %d\\n", findMax(numbers, n));
    return 0;
}
'''
    },
    "java": {
        "find_max": '''public class Main {
    public static int findMax(int[] arr) {
        int maximum = arr[0];
        for (int x : arr) {
            if (x > maximum) maximum = x;
        }
        return maximum;
    }

    public static void main(String[] args) {
        int[] numbers = {10, 20, 5, 30};
        System.out.println("Maximum element: " + findMax(numbers));
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

public class Program {
    public static int FindMax(int[] arr) {
        int maxVal = arr[0];
        foreach (int x in arr) {
            if (x > maxVal) maxVal = x;
        }
        return maxVal;
    }

    public static void Main(string[] args) {
        int[] numbers = { 10, 20, 5, 30 };
        Console.WriteLine($"Maximum element: {FindMax(numbers)}");
    }
}
'''
    },
    "rust": {
        "find_max": '''fn find_max(arr: &[i32]) -> i32 {
    let mut max_val = arr[0];
    for &x in arr.iter() {
        if x > max_val {
            max_val = x;
        }
    }
    max_val
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
    maxVal := arr[0]
    for _, x := range arr {
        if x > maxVal {
            maxVal = x
        }
    }
    return maxVal
}

func main() {
    numbers := []int{10, 20, 5, 30}
    fmt.Printf("Maximum element: %d\\n", findMax(numbers))
}
'''
    },
    "kotlin": {
        "find_max": '''fun findMax(arr: IntArray): Int {
    var maxVal = arr[0]
    for (x in arr) {
        if (x > maxVal) maxVal = x
    }
    return maxVal
}

fun main() {
    val numbers = intArrayOf(10, 20, 5, 30)
    println("Maximum element: ${findMax(numbers)}")
}
'''
    },
    "php": {
        "find_max": '''<?php
function findMax($arr) {
    $max = $arr[0];
    foreach ($arr as $x) {
        if ($x > $max) $max = $x;
    }
    return $max;
}

$numbers = [10, 20, 5, 30];
echo "Maximum element: " . findMax($numbers) . "\\n";
'''
    },
    "ruby": {
        "find_max": '''def find_max(arr)
    maximum = arr[0]
    arr.each do |x|
        maximum = x if x > maximum
    end
    maximum
end

numbers = [10, 20, 5, 30]
puts "Maximum element: #{find_max(numbers)}"
'''
    },
    "dart": {
        "find_max": '''int findMax(List<int> arr) {
    int maxVal = arr[0];
    for (var x in arr) {
        if (x > maxVal) maxVal = x;
    }
    return maxVal;
}

void main() {
    var numbers = [10, 20, 5, 30];
    print("Maximum element: ${findMax(numbers)}");
}
'''
    },
    "r": {
        "find_max": '''find_max <- function(arr) {
    max_val <- arr[1]
    for (x in arr) {
        if (x > max_val) {
            max_val <- x
        }
    }
    return(max_val)
}

numbers <- c(10, 20, 5, 30)
cat("Maximum element:", find_max(numbers), "\\n")
'''
    },
    "swift": {
        "find_max": r'''func findMax(_ arr: [Int]) -> Int {
    var maxVal = arr[0]
    for x in arr {
        if x > maxVal {
            maxVal = x
        }
    }
    return maxVal
}

let numbers = [10, 20, 5, 30]
print("Maximum element: \(findMax(numbers))")
'''
    },
    "sql": {
        "find_max": '''-- Create sample table and query maximum value
CREATE TABLE sales (
    id INTEGER PRIMARY KEY,
    product_name TEXT,
    revenue INTEGER
);

INSERT INTO sales (product_name, revenue) VALUES 
    ('Widget A', 10),
    ('Widget B', 20),
    ('Widget C', 5),
    ('Widget D', 30);

-- Query maximum revenue
SELECT MAX(revenue) AS maximum_revenue FROM sales;
'''
    }
}

def get_all_languages_metadata() -> List[Dict[str, Any]]:
    # Distinct unique languages list
    seen = set()
    result = []
    
    unique_keys = [
        # Tier 1
        "python", "c", "cpp", "java", "javascript", "typescript", "csharp", 
        "go", "rust", "kotlin", "swift", "php", "ruby", "dart", "r",
        # Special Purpose
        "sql"
    ]

    for key in unique_keys:
        engine = LANGUAGE_ADAPTERS.get(key)
        if engine and key not in seen:
            seen.add(key)
            if hasattr(engine, "get_metadata"):
                result.append(engine.get_metadata())
            else:
                # Built-in standard engines
                names = {
                    "python": ("Python 3.12", "Scripted / JIT", "py", "🐍"),
                    "c": ("C (GCC)", "Compiled Native", "c", "⚡"),
                    "cpp": ("C++ (GCC)", "Compiled Native", "cpp", "⚡"),
                    "java": ("Java (JDK 25)", "Managed VM (.NET / JVM)", "java", "☕"),
                    "javascript": ("JavaScript (Node.js)", "Scripted / JIT", "js", "🌐")
                }
                info = names.get(key, (key.capitalize(), "General", key, "⚡"))
                result.append({
                    "id": key,
                    "name": info[0],
                    "family": info[1],
                    "tier": 1,
                    "extension": info[2],
                    "icon": info[3],
                    "is_installed": True,
                    "toolchain_cmd": key
                })
    return result
