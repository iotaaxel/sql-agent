"""Error correction for SQL queries."""
import re
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class ErrorCorrector:
    """Corrects SQL syntax errors using LLM feedback."""
    
    def __init__(self, llm_provider):
        """Initialize error corrector.
        
        Args:
            llm_provider: LLMProvider instance for generating corrections
        """
        self.llm_provider = llm_provider
    
    def correct_query(self, original_query: str, error_message: str, 
                     schema_context: Optional[str] = None,
                     previous_queries: Optional[list] = None) -> str:
        """Correct a SQL query based on error message.
        
        Args:
            original_query: The SQL query that failed
            error_message: Error message from database
            schema_context: Schema information for context
            previous_queries: List of previous queries for context
            
        Returns:
            Corrected SQL query
        """
        correction_prompt = self._build_correction_prompt(
            original_query, error_message, schema_context, previous_queries
        )
        
        system_prompt = """You are a SQL expert. Your task is to fix SQL syntax errors.
Given a SQL query that failed with an error, provide ONLY the corrected SQL query.
Do not include any explanation, just the SQL query itself.
Make sure the corrected query is valid and follows SQL syntax rules."""
        
        try:
            corrected_query = self.llm_provider.generate(
                prompt=correction_prompt,
                system_prompt=system_prompt
            )
            
            # Extract SQL query from response (in case LLM adds explanation)
            corrected_query = self._extract_sql_from_response(corrected_query)
            
            logger.info("Query corrected successfully")
            return corrected_query
            
        except Exception as e:
            logger.error(f"Error during query correction: {e}")
            return original_query  # Return original if correction fails
    
    def _build_correction_prompt(self, query: str, error: str, 
                                 schema: Optional[str],
                                 previous_queries: Optional[list]) -> str:
        """Build prompt for error correction."""
        prompt_parts = [
            "Fix the following SQL query that produced an error:",
            "",
            f"Original Query:",
            f"```sql",
            query,
            f"```",
            "",
            f"Error Message:",
            error,
            ""
        ]
        
        if schema:
            prompt_parts.extend([
                "Database Schema:",
                schema,
                ""
            ])
        
        if previous_queries:
            prompt_parts.extend([
                "Previous queries for context:",
                "\n".join([f"- {q}" for q in previous_queries[-3:]]),  # Last 3 queries
                ""
            ])
        
        prompt_parts.append("Provide the corrected SQL query:")
        
        return "\n".join(prompt_parts)
    
    def _extract_sql_from_response(self, response: str) -> str:
        """Extract SQL query from LLM response."""
        # Try to find SQL in code blocks
        sql_block_match = re.search(r'```(?:sql)?\s*(.*?)\s*```', response, re.DOTALL)
        if sql_block_match:
            return sql_block_match.group(1).strip()
        
        # Try to find SQL between backticks
        backtick_match = re.search(r'`([^`]+)`', response)
        if backtick_match:
            candidate = backtick_match.group(1).strip()
            if candidate.upper().startswith(('SELECT', 'WITH')):
                return candidate
        
        # Look for lines that look like SQL
        lines = response.split('\n')
        sql_lines = []
        in_sql = False
        
        for line in lines:
            line_upper = line.strip().upper()
            if line_upper.startswith(('SELECT', 'WITH', 'INSERT', 'UPDATE', 'DELETE')):
                in_sql = True
                sql_lines.append(line)
            elif in_sql:
                if line.strip() and not line.strip().startswith('#'):
                    sql_lines.append(line)
                if line.strip().endswith(';'):
                    break
        
        if sql_lines:
            return '\n'.join(sql_lines).strip()
        
        # Fallback: return response as-is (might be just SQL)
        return response.strip()

