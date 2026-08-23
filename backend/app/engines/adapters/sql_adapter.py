import sqlite3
import re
import time
from app.engines.adapters.base_adapter import UniversalLanguageAdapter, LanguageFamily
from app.models import ExecutionResult, ComplexityResult, LineAnalysisItem, SecurityIssue, QualityMetric

class SQLAdapter(UniversalLanguageAdapter):
    def __init__(self):
        super().__init__(
            lang_id="sql",
            display_name="SQL (SQLite / ANSI)",
            family=LanguageFamily.SPECIAL_PURPOSE,
            tier=3,
            extension="sql",
            toolchain_cmd="sqlite3",
            icon="🗄️"
        )

    def execute(self, code: str, stdin: str = "", timeout_sec: float = 5.0) -> ExecutionResult:
        start_time = time.perf_counter()
        conn = None
        try:
            conn = sqlite3.connect(":memory:")
            cursor = conn.cursor()
            
            statements = [s.strip() for s in code.split(';') if s.strip()]
            outputs = []
            
            for stmt in statements:
                cursor.execute(stmt)
                if stmt.upper().startswith("SELECT") or stmt.upper().startswith("EXPLAIN"):
                    rows = cursor.fetchall()
                    if rows:
                        headers = [d[0] for d in cursor.description] if cursor.description else []
                        header_str = " | ".join(headers)
                        div_str = "-+-".join(["-" * len(h) for h in headers])
                        row_strs = [" | ".join(str(v) for v in r) for r in rows[:50]]
                        outputs.append(f"{header_str}\n{div_str}\n" + "\n".join(row_strs))
                    else:
                        outputs.append("(0 rows returned)")
                else:
                    outputs.append(f"Statement executed successfully ({cursor.rowcount} rows affected).")

            conn.commit()
            elapsed = time.perf_counter() - start_time
            return ExecutionResult(
                status="success",
                stdout="\n\n".join(outputs) if outputs else "SQL schema initialized.",
                stderr="",
                exit_code=0,
                execution_time_sec=round(elapsed, 4),
                peak_memory_mb=6.2
            )
        except Exception as e:
            elapsed = time.perf_counter() - start_time
            return ExecutionResult(
                status="compilation_error",
                stdout="",
                stderr=str(e),
                exit_code=-1,
                execution_time_sec=round(elapsed, 4),
                peak_memory_mb=0.0,
                error_type="SQL Execution Error",
                error_message=str(e)
            )
        finally:
            if conn:
                conn.close()

    def analyze_complexity(self, code: str) -> ComplexityResult:
        upper = code.upper()
        # Check joins, cartesian products, scans
        join_count = len(re.findall(r'\bJOIN\b|,', upper))
        has_full_scan = bool(re.search(r'LIKE\s+[\'"]%.*%[\'"]|\bWHERE\b.*!=', upper))
        has_group_or_order = bool(re.search(r'\b(GROUP\s+BY|ORDER\s+BY|DISTINCT)\b', upper))

        if join_count >= 2 or re.search(r'\bCROSS\s+JOIN\b', upper):
            return ComplexityResult(
                time_complexity="O(n^2)",
                space_complexity="O(n)",
                confidence=0.88,
                explanation="Nested loop query plan or Cartesian product across multiple relational tables.",
                nested_depth=2,
                details=["Cross table join operations perform O(N × M) row comparisons."]
            )
        elif has_group_or_order:
            return ComplexityResult(
                time_complexity="O(n log n)",
                space_complexity="O(n)",
                confidence=0.92,
                explanation="Sorting / Index scan for ORDER BY, GROUP BY, or DISTINCT aggregation.",
                nested_depth=1,
                details=["Sorting relational records requires O(n log n) comparisons."]
            )
        elif has_full_scan or "SELECT" in upper:
            return ComplexityResult(
                time_complexity="O(n)",
                space_complexity="O(1)",
                confidence=0.95,
                explanation="Sequential table scan traversing all N rows in the table.",
                nested_depth=1,
                details=["Linear scan over table records."]
            )
        return ComplexityResult(
            time_complexity="O(1)",
            space_complexity="O(1)",
            confidence=0.98,
            explanation="Constant time schema operation or single-row primary key lookup."
        )
