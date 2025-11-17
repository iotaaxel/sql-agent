"""SQL query execution engine with safety checks."""

import logging
import re
import sqlite3
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class QueryResult:
    """Result of a SQL query execution."""

    success: bool
    data: Optional[List[Dict[str, Any]]] = None
    columns: Optional[List[str]] = None
    row_count: int = 0
    error: Optional[str] = None
    execution_time: float = 0.0


class QueryExecutor:
    """Executes SQL queries with safety checks."""

    def __init__(
        self,
        db_path: str,
        db_type: str = "sqlite",
        safe_mode: bool = True,
        blocked_keywords: Optional[List[str]] = None,
        max_query_length: int = 10000,
    ):
        """Initialize query executor.

        Args:
            db_path: Path to database file
            db_type: Type of database
            safe_mode: Enable safety checks
            blocked_keywords: List of SQL keywords to block
            max_query_length: Maximum query length
        """
        self.db_path = db_path
        self.db_type = db_type
        self.safe_mode = safe_mode
        self.blocked_keywords = blocked_keywords or [
            "DELETE",
            "DROP",
            "ALTER",
            "TRUNCATE",
            "CREATE",
            "INSERT",
            "UPDATE",
        ]
        self.max_query_length = max_query_length

    def get_connection(self):
        """Get database connection."""
        if self.db_type == "sqlite":
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            return conn
        raise ValueError(f"Unsupported database type: {self.db_type}")

    def validate_query(self, query: str) -> Tuple[bool, Optional[str]]:
        """Validate query for safety.

        Args:
            query: SQL query to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check query length
        if len(query) > self.max_query_length:
            return False, f"Query exceeds maximum length of {self.max_query_length} characters"

        if not self.safe_mode:
            return True, None

        # Normalize query for keyword checking
        query_upper = query.upper().strip()

        # Remove comments and strings to avoid false positives
        query_clean = self._remove_sql_comments(query_upper)

        # Check for blocked keywords
        for keyword in self.blocked_keywords:
            # Use word boundaries to avoid matching keywords inside other words
            pattern = r"\b" + re.escape(keyword) + r"\b"
            if re.search(pattern, query_clean):
                return False, f"Query contains blocked keyword: {keyword}"

        return True, None

    def _remove_sql_comments(self, query: str) -> str:
        """Remove SQL comments from query."""
        # Remove single-line comments
        query = re.sub(r"--.*", "", query)
        # Remove multi-line comments
        query = re.sub(r"/\*.*?\*/", "", query, flags=re.DOTALL)
        return query

    def execute(self, query: str) -> QueryResult:
        """Execute a SQL query.

        Args:
            query: SQL query to execute

        Returns:
            QueryResult object
        """
        import time

        start_time = time.time()

        # Validate query
        is_valid, error = self.validate_query(query)
        if not is_valid:
            return QueryResult(success=False, error=error, execution_time=time.time() - start_time)

        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Execute query
            cursor.execute(query)

            # Check if query returns results (SELECT) or modifies data
            if query.strip().upper().startswith("SELECT"):
                # Fetch results
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description] if cursor.description else []

                # Convert rows to dictionaries
                data = [dict(row) for row in rows]

                result = QueryResult(
                    success=True,
                    data=data,
                    columns=columns,
                    row_count=len(data),
                    execution_time=time.time() - start_time,
                )
            else:
                # For non-SELECT queries, commit if needed
                conn.commit()
                result = QueryResult(
                    success=True,
                    data=None,
                    columns=None,
                    row_count=cursor.rowcount if hasattr(cursor, "rowcount") else 0,
                    execution_time=time.time() - start_time,
                )

            conn.close()
            logger.info(f"Query executed successfully in {result.execution_time:.3f}s")
            return result

        except sqlite3.Error as e:
            error_msg = str(e)
            logger.error(f"SQL execution error: {error_msg}")
            return QueryResult(
                success=False, error=error_msg, execution_time=time.time() - start_time
            )
        except Exception as e:
            error_msg = f"Unexpected error: {e!s}"
            logger.error(error_msg)
            return QueryResult(
                success=False, error=error_msg, execution_time=time.time() - start_time
            )

    def explain_query_plan(self, query: str) -> Optional[str]:
        """Get query execution plan.

        Args:
            query: SQL query to explain

        Returns:
            Query plan as string, or None if error
        """
        if self.db_type != "sqlite":
            return None

        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Use EXPLAIN QUERY PLAN
            explain_query = f"EXPLAIN QUERY PLAN {query}"
            cursor.execute(explain_query)
            plan_rows = cursor.fetchall()

            conn.close()

            # Format plan
            plan_lines = []
            for row in plan_rows:
                plan_lines.append(f"{row[0]} | {row[1]} | {row[2]} | {row[3]}")

            return "\n".join(plan_lines)

        except Exception as e:
            logger.error(f"Error getting query plan: {e}")
            return None
