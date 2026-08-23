import os
import re
from typing import Optional, List, Dict, Any
from app.models import AIInsight, OptimizeResponse

class AIOptimizer:
    """
    Generates intelligent algorithmic explanations, optimization suggestions,
    and automatic code refactoring using Gemini API or built-in heuristics.
    """

    @classmethod
    def generate_insights(cls, language: str, code: str, current_big_o: str) -> AIInsight:
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            try:
                from google import genai
                client = genai.Client(api_key=api_key)
                prompt = f"""You are CodePrism AI, an expert algorithm optimization engine.
Analyze the following {language} code:
```{language}
{code}
```
Current detected Time Complexity: {current_big_o}

Provide your analysis in this exact format:
SUMMARY: <1-2 sentences summarizing what the code does>
BREAKDOWN: <2-3 sentences explaining the algorithmic flow and why it runs in {current_big_o}>
SUGGESTIONS:
- <Suggestion 1>
- <Suggestion 2>
OPTIMIZED_BIG_O: <e.g. O(n) or O(n log n) or O(1)>
WHY_FASTER: <Explanation of how the optimization reduces time or space>
OPTIMIZED_CODE:
```{language}
<Full optimized code here>
```
"""
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                text = response.text
                return cls._parse_ai_response(text, current_big_o, code, language)
            except Exception:
                pass

        # Offline heuristic fallback
        return cls._heuristic_insights(language, code, current_big_o)

    @classmethod
    def _parse_ai_response(cls, text: str, current_big_o: str, original_code: str, language: str) -> AIInsight:
        summary = ""
        breakdown = ""
        suggestions: List[str] = []
        opt_big_o = "O(n log n)"
        why_faster = ""
        opt_code = None

        if "SUMMARY:" in text:
            summary = text.split("SUMMARY:")[1].split("BREAKDOWN:")[0].strip()
        if "BREAKDOWN:" in text:
            breakdown = text.split("BREAKDOWN:")[1].split("SUGGESTIONS:")[0].strip()
        if "SUGGESTIONS:" in text:
            sug_part = text.split("SUGGESTIONS:")[1].split("OPTIMIZED_BIG_O:")[0].strip()
            suggestions = [line.strip("- ").strip() for line in sug_part.splitlines() if line.strip()]
        if "OPTIMIZED_BIG_O:" in text:
            opt_big_o = text.split("OPTIMIZED_BIG_O:")[1].split("WHY_FASTER:")[0].strip()
        if "WHY_FASTER:" in text:
            why_faster = text.split("WHY_FASTER:")[1].split("OPTIMIZED_CODE:")[0].strip()
        
        # Extract code block
        code_blocks = re.findall(r'```(?:' + language + r')?\s*(.*?)\s*```', text, re.DOTALL)
        if code_blocks:
            opt_code = code_blocks[-1].strip()

        if not summary:
            return cls._heuristic_insights(language, original_code, current_big_o)

        return AIInsight(
            line_by_line_summary=summary,
            algorithmic_breakdown=breakdown,
            optimization_suggestions=suggestions if suggestions else ["Use hash table lookups to achieve O(1) retrieval."],
            optimized_code=opt_code,
            original_big_o=current_big_o,
            optimized_big_o=opt_big_o,
            why_faster=why_faster if why_faster else "Replaced nested iterations with vectorized/linear hash map data structures."
        )

    @classmethod
    def _heuristic_insights(cls, language: str, code: str, current_big_o: str) -> AIInsight:
        # Check patterns for common optimizations
        if current_big_o in ("O(n^2)", "O(n^3)"):
            if "for" in code and ("in arr" in code or "range(" in code):
                opt_code = """# Optimized using Hash Set / Hash Map for O(n) linear lookup
def find_duplicates_optimized(arr):
    seen = set()
    duplicates = []
    for x in arr:
        if x in seen:
            duplicates.append(x)
        seen.add(x)
    return duplicates

numbers = [10, 20, 5, 30, 20, 10]
print(find_duplicates_optimized(numbers))
""" if language == "python" else None

                return AIInsight(
                    line_by_line_summary="The algorithm processes elements using multiple nested loops, re-evaluating inner elements for each outer step.",
                    algorithmic_breakdown="Nested iterations over the dataset cause total operations to scale with N² (e.g. comparing all pairs).",
                    optimization_suggestions=[
                        "Use a Hash Set or Hash Map (O(1) average lookup) to eliminate the inner scan loop.",
                        "Sort the collection once in O(n log n) and utilize two-pointer traversal.",
                        "Leverage built-in vectorized utilities (e.g. list comprehension, std::unordered_set)."
                    ],
                    optimized_code=opt_code,
                    original_big_o=current_big_o,
                    optimized_big_o="O(n)",
                    why_faster="Substituting the O(n) inner loop search with an O(1) hash table lookup reduces overall runtime from O(n²) to O(n)."
                )

        if current_big_o == "O(2^n)":
            opt_code = """# Optimized using Memoization / Dynamic Programming (O(n) time, O(n) space)
from functools import lru_cache

@lru_cache(maxsize=None)
def fib_memo(n):
    if n <= 1:
        return n
    return fib_memo(n - 1) + fib_memo(n - 2)

print(fib_memo(30))
""" if language == "python" else None

            return AIInsight(
                line_by_line_summary="The recursive function recalculates identical subproblems repeatedly across multiple activation branches.",
                algorithmic_breakdown="Naive recursion forms a binary branching tree with 2^N leaf nodes, causing exponential time complexity.",
                optimization_suggestions=[
                    "Apply Dynamic Programming or Memoization (@lru_cache / memo table) to cache overlapping subproblems.",
                    "Convert recursion to an iterative loop with two rolling variables for O(n) time and O(1) auxiliary space."
                ],
                optimized_code=opt_code,
                original_big_o="O(2^n)",
                optimized_big_o="O(n)",
                why_faster="Memoization ensures each subproblem is computed exactly once, collapsing the 2^N call tree into N linear table lookups."
            )

        return AIInsight(
            line_by_line_summary=f"The program executes with {current_big_o} asymptotic scaling.",
            algorithmic_breakdown="Operations traverse data structures in single passes or constant-time memory instructions.",
            optimization_suggestions=[
                "Ensure in-place operations to preserve O(1) auxiliary space.",
                "Use generator expressions to stream large datasets without full in-memory buffering."
            ],
            optimized_code=None,
            original_big_o=current_big_o,
            optimized_big_o=current_big_o,
            why_faster="Algorithm is already well-optimized for time complexity."
        )
