"""Tests for SQL Agent."""

import os
import sqlite3
import tempfile
import unittest
from unittest.mock import Mock

from src.agent import AgentMemory, SQLAgent
from src.executor import QueryExecutor
from src.schema_introspection import SchemaIntrospector


class TestAgentMemory(unittest.TestCase):
    """Test cases for AgentMemory."""

    def test_add_interaction(self):
        """Test adding interactions to memory."""
        memory = AgentMemory(max_size=5)

        mock_result = Mock()
        mock_result.success = True
        mock_result.row_count = 10
        mock_result.error = None

        memory.add("test query", "SELECT * FROM table", mock_result)

        self.assertEqual(len(memory.interactions), 1)
        self.assertEqual(memory.interactions[0]["user_query"], "test query")

    def test_memory_size_limit(self):
        """Test that memory respects size limit."""
        memory = AgentMemory(max_size=3)

        mock_result = Mock()
        mock_result.success = True
        mock_result.row_count = 1
        mock_result.error = None

        for i in range(5):
            memory.add(f"query {i}", f"SELECT {i}", mock_result)

        self.assertEqual(len(memory.interactions), 3)
        self.assertEqual(memory.interactions[0]["user_query"], "query 2")


class TestSQLAgent(unittest.TestCase):
    """Test cases for SQLAgent."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary database
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.db_path = self.temp_db.name

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE test (id INTEGER, name TEXT)")
        cursor.execute("INSERT INTO test VALUES (1, 'test')")
        conn.commit()
        conn.close()

        # Create mocks
        self.mock_llm = Mock()
        self.executor = QueryExecutor(db_path=self.db_path, safe_mode=True)
        self.schema_introspector = SchemaIntrospector(db_path=self.db_path)

        self.agent = SQLAgent(
            llm_provider=self.mock_llm,
            executor=self.executor,
            schema_introspector=self.schema_introspector,
            enable_error_correction=False,
            enable_tools=False,
        )

    def tearDown(self):
        """Clean up."""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_generate_sql(self):
        """Test SQL generation."""
        self.mock_llm.generate.return_value = "SELECT * FROM test"

        sql = self.agent.generate_sql("show all records")

        self.assertEqual(sql, "SELECT * FROM test")
        self.mock_llm.generate.assert_called_once()

    def test_query_success(self):
        """Test successful query execution."""
        self.mock_llm.generate.return_value = "SELECT * FROM test"

        result = self.agent.query("show all records")

        self.assertTrue(result["success"])
        self.assertEqual(result["row_count"], 1)

    def test_clean_sql_query(self):
        """Test SQL query cleaning."""
        # Test markdown removal
        sql = self.agent._clean_sql_query("```sql\nSELECT * FROM test\n```")
        self.assertEqual(sql, "SELECT * FROM test")

        # Test semicolon removal
        sql = self.agent._clean_sql_query("SELECT * FROM test;")
        self.assertEqual(sql, "SELECT * FROM test")


if __name__ == "__main__":
    unittest.main()
