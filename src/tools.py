"""Optional tools for the SQL Agent."""
import logging
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ToolResult:
    """Result of a tool execution."""
    success: bool
    output: str
    data: Optional[Any] = None


class ToolRegistry:
    """Registry for agent tools."""
    
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
    
    def register(self, name: str, func: Callable, description: str):
        """Register a tool.
        
        Args:
            name: Tool name
            func: Tool function
            description: Tool description
        """
        func.description = description
        self.tools[name] = func
        logger.debug(f"Registered tool: {name}")
    
    def get_tool(self, name: str) -> Optional[Callable]:
        """Get a tool by name."""
        return self.tools.get(name)
    
    def list_tools(self) -> List[Dict[str, str]]:
        """List all available tools."""
        return [
            {"name": name, "description": func.description}
            for name, func in self.tools.items()
        ]
    
    def execute(self, name: str, **kwargs) -> ToolResult:
        """Execute a tool.
        
        Args:
            name: Tool name
            **kwargs: Tool arguments
            
        Returns:
            ToolResult
        """
        tool = self.get_tool(name)
        if not tool:
            return ToolResult(
                success=False,
                output=f"Tool '{name}' not found"
            )
        
        try:
            result = tool(**kwargs)
            if isinstance(result, ToolResult):
                return result
            elif isinstance(result, str):
                return ToolResult(success=True, output=result)
            else:
                return ToolResult(success=True, output=str(result), data=result)
        except Exception as e:
            logger.error(f"Error executing tool {name}: {e}")
            return ToolResult(
                success=False,
                output=f"Error executing tool: {str(e)}"
            )


def create_tool_registry(executor, llm_provider, schema_introspector) -> ToolRegistry:
    """Create and register default tools.
    
    Args:
        executor: QueryExecutor instance
        llm_provider: LLMProvider instance
        schema_introspector: SchemaIntrospector instance
        
    Returns:
        ToolRegistry with registered tools
    """
    registry = ToolRegistry()
    
    def explain_query_plan(query: str) -> ToolResult:
        """Explain the execution plan for a SQL query.
        
        Args:
            query: SQL query to explain
            
        Returns:
            ToolResult with query plan
        """
        plan = executor.explain_query_plan(query)
        if plan:
            return ToolResult(
                success=True,
                output=f"Query Execution Plan:\n{plan}",
                data=plan
            )
        else:
            return ToolResult(
                success=False,
                output="Could not generate query plan"
            )
    
    def fix_query(query: str, error: str) -> ToolResult:
        """Fix a SQL query that has syntax errors.
        
        Args:
            query: SQL query to fix
            error: Error message from the database
            
        Returns:
            ToolResult with fixed query
        """
        from .error_corrector import ErrorCorrector
        corrector = ErrorCorrector(llm_provider)
        schema_context = schema_introspector.get_schema_prompt()
        fixed_query = corrector.correct_query(query, error, schema_context)
        
        return ToolResult(
            success=True,
            output=f"Fixed Query:\n```sql\n{fixed_query}\n```",
            data=fixed_query
        )
    
    def summarize_results(query: str, results: List[Dict[str, Any]], 
                         columns: Optional[List[str]] = None) -> ToolResult:
        """Summarize query results using LLM.
        
        Args:
            query: Original SQL query
            results: Query results
            columns: Column names
            
        Returns:
            ToolResult with summary
        """
        # Limit results for summarization
        sample_results = results[:10]  # First 10 rows
        
        columns_str = ', '.join(columns) if columns else 'N/A'
        prompt = f"""Summarize the following SQL query results:

Query: {query}

Columns: {columns_str}

Results (showing first {len(sample_results)} of {len(results)} rows):
"""
        for i, row in enumerate(sample_results, 1):
            prompt += f"\nRow {i}: {dict(row)}\n"
        
        if len(results) > 10:
            prompt += f"\n... and {len(results) - 10} more rows\n"
        
        prompt += "\nProvide a concise summary of the results, highlighting key insights and patterns."
        
        system_prompt = "You are a data analyst. Summarize SQL query results in a clear, concise manner."
        
        try:
            summary = llm_provider.generate(prompt=prompt, system_prompt=system_prompt)
            return ToolResult(
                success=True,
                output=summary,
                data=summary
            )
        except Exception as e:
            logger.error(f"Error summarizing results: {e}")
            return ToolResult(
                success=False,
                output=f"Error generating summary: {str(e)}"
            )
    
    # Register tools
    registry.register(
        "explain_query_plan",
        explain_query_plan,
        "Explains the execution plan for a SQL query to help understand performance"
    )
    
    registry.register(
        "fix_query",
        fix_query,
        "Fixes SQL syntax errors in a query"
    )
    
    registry.register(
        "summarize_results",
        summarize_results,
        "Summarizes query results using natural language"
    )
    
    return registry

