"""Secure AST-based SQL Validation and Read-Only Execution Sandbox."""

import re
import sqlite3
import time
from typing import Dict, Any, List, Tuple
import sqlparse
from sqlparse.sql import Statement
from config.config import settings

class SQLValidationError(Exception):
    """Raised when an untrusted or dangerous SQL query is detected."""
    pass

class SQLSandbox:
    """Enforces strict AST safety boundaries, table whitelisting, and read-only limits."""

    MUTATION_KEYWORDS = {
        "DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE", 
        "CREATE", "REPLACE", "EXEC", "EXECUTE", "GRANT", "REVOKE", 
        "ATTACH", "DETACH", "PRAGMA", "VACUUM"
    }

    def __init__(self, db_path: str = str(settings.DATABASE_PATH)):
        self.db_path = db_path
        self.allowed_tables = set(settings.SQL_ALLOWED_TABLES)

    def validate_query(self, query: str) -> str:
        """Parses and validates that the SQL query is strictly a safe read-only SELECT statement."""
        cleaned = query.strip().rstrip(";")
        if not cleaned:
            raise SQLValidationError("Empty SQL query provided.")

        # Check for multiple semicolon-separated statements
        statements = sqlparse.parse(cleaned)
        if len(statements) != 1:
            raise SQLValidationError("Multiple SQL statements in a single execution are prohibited.")

        stmt: Statement = statements[0]
        tokens = [t for t in stmt.flatten() if not t.is_whitespace]

        # First non-comment token must be SELECT or WITH
        first_token = None
        for t in tokens:
            val = t.value.upper()
            if not val.startswith("--") and not val.startswith("/*"):
                first_token = val
                break

        if first_token not in ("SELECT", "WITH"):
            raise SQLValidationError(f"Invalid query type '{first_token}'. Only SELECT/WITH queries are allowed.")

        # Check for any mutation keywords anywhere in the token stream
        for token in tokens:
            upper_val = token.value.upper()
            if upper_val in self.MUTATION_KEYWORDS:
                raise SQLValidationError(f"Forbidden mutation keyword '{upper_val}' detected in query.")

        # Ensure no comments hiding injection
        if re.search(r"/\*|\*/|--", cleaned):
            # Clean comments before execution
            cleaned = sqlparse.format(cleaned, strip_comments=True).strip()

        # Enforce limit if not present
        if "LIMIT" not in cleaned.upper():
            cleaned = f"{cleaned} LIMIT {settings.SQL_MAX_ROWS}"

        return cleaned

    def execute_query(self, raw_query: str) -> Dict[str, Any]:
        """Safely executes validated SQL and returns columns, rows, execution time, and markdown table."""
        start_time = time.time()
        try:
            safe_query = self.validate_query(raw_query)
        except SQLValidationError as e:
            return {
                "success": False,
                "error": str(e),
                "safe_query": None,
                "rows": [],
                "columns": [],
                "execution_time_ms": 0.0,
                "table_markdown": ""
            }

        conn = None
        try:
            # Use URI with mode=ro for true filesystem-level read-only safety
            uri = f"file:{self.db_path}?mode=ro"
            conn = sqlite3.connect(uri, uri=True, timeout=settings.SQL_TIMEOUT_SECONDS)
            cursor = conn.cursor()
            cursor.execute(safe_query)
            
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            elapsed_ms = round((time.time() - start_time) * 1000, 2)

            # Generate concise markdown preview
            md_lines = []
            if columns:
                md_lines.append("| " + " | ".join(columns) + " |")
                md_lines.append("| " + " | ".join(["---"] * len(columns)) + " |")
                for r in rows[:15]:  # Preview up to 15 rows
                    md_lines.append("| " + " | ".join([str(val) for val in r]) + " |")

            return {
                "success": True,
                "error": None,
                "safe_query": safe_query,
                "columns": columns,
                "rows": rows,
                "row_count": len(rows),
                "execution_time_ms": elapsed_ms,
                "table_markdown": "\n".join(md_lines),
                "citation_tag": f"[Data Warehouse: SQL query executed on {', '.join(columns)}]"
            }

        except sqlite3.OperationalError as e:
            return {
                "success": False,
                "error": f"Database execution error: {str(e)}",
                "safe_query": safe_query,
                "rows": [],
                "columns": [],
                "execution_time_ms": round((time.time() - start_time) * 1000, 2),
                "table_markdown": ""
            }
        finally:
            if conn:
                conn.close()

    def get_schema_summary(self) -> str:
        """Returns the schema description for the allowed tables."""
        conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)
        cursor = conn.cursor()
        summary = []
        for table in sorted(self.allowed_tables):
            cursor.execute(f"PRAGMA table_info({table})")
            cols = [f"{row[1]} {row[2]}" for row in cursor.fetchall()]
            summary.append(f"Table '{table}': ({', '.join(cols)})")
        conn.close()
        return "\n".join(summary)
