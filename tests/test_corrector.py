"""Tests for error corrector."""
import unittest
from unittest.mock import Mock, MagicMock
from src.error_corrector import ErrorCorrector


class TestErrorCorrector(unittest.TestCase):
    """Test cases for ErrorCorrector."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_llm = Mock()
        self.corrector = ErrorCorrector(self.mock_llm)
    
    def test_extract_sql_from_markdown(self):
        """Test extracting SQL from markdown code blocks."""
        response = "```sql\nSELECT * FROM table\n```"
        sql = self.corrector._extract_sql_from_response(response)
        self.assertEqual(sql, "SELECT * FROM table")
    
    def test_extract_sql_from_plain_text(self):
        """Test extracting SQL from plain text."""
        response = "SELECT * FROM table"
        sql = self.corrector._extract_sql_from_response(response)
        self.assertEqual(sql, "SELECT * FROM table")
    
    def test_correct_query(self):
        """Test query correction."""
        self.mock_llm.generate.return_value = "SELECT * FROM employees WHERE id = 1"
        
        corrected = self.corrector.correct_query(
            "SELECT * FROM employee WHERE id = 1",
            "no such table: employee"
        )
        
        self.assertEqual(corrected, "SELECT * FROM employees WHERE id = 1")
        self.mock_llm.generate.assert_called_once()


if __name__ == '__main__':
    unittest.main()

