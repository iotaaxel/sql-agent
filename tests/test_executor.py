"""Tests for query executor."""
import unittest
import os
import tempfile
import sqlite3
from src.executor import QueryExecutor, QueryResult


class TestQueryExecutor(unittest.TestCase):
    """Test cases for QueryExecutor."""
    
    def setUp(self):
        """Set up test database."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name
        
        # Create test database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                value INTEGER
            )
        """)
        cursor.execute("INSERT INTO test_table (name, value) VALUES ('test1', 10)")
        cursor.execute("INSERT INTO test_table (name, value) VALUES ('test2', 20)")
        conn.commit()
        conn.close()
        
        self.executor = QueryExecutor(
            db_path=self.db_path,
            safe_mode=True
        )
    
    def tearDown(self):
        """Clean up test database."""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
    
    def test_valid_select_query(self):
        """Test executing a valid SELECT query."""
        result = self.executor.execute("SELECT * FROM test_table")
        
        self.assertTrue(result.success)
        self.assertEqual(result.row_count, 2)
        self.assertIsNotNone(result.data)
        self.assertEqual(len(result.data), 2)
    
    def test_blocked_keyword(self):
        """Test that blocked keywords are rejected."""
        result = self.executor.execute("DELETE FROM test_table WHERE id = 1")
        
        self.assertFalse(result.success)
        self.assertIn("blocked keyword", result.error.lower())
    
    def test_sql_syntax_error(self):
        """Test handling of SQL syntax errors."""
        result = self.executor.execute("SELECT * FROM nonexistent_table")
        
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error)
    
    def test_query_validation(self):
        """Test query validation."""
        is_valid, error = self.executor.validate_query("SELECT * FROM test_table")
        self.assertTrue(is_valid)
        self.assertIsNone(error)
        
        is_valid, error = self.executor.validate_query("DELETE FROM test_table")
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
    
    def test_explain_query_plan(self):
        """Test query plan explanation."""
        plan = self.executor.explain_query_plan("SELECT * FROM test_table WHERE value > 10")
        self.assertIsNotNone(plan)
        self.assertIsInstance(plan, str)


if __name__ == '__main__':
    unittest.main()

