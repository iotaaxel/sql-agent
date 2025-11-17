"""Main SQL Agent with agent loop and memory."""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from .error_corrector import ErrorCorrector
from .executor import QueryExecutor, QueryResult
from .llm import LLMProvider
from .schema_introspection import SchemaIntrospector
from .tools import ToolRegistry

logger = logging.getLogger(__name__)


@dataclass
class AgentMemory:
    """Short-term memory for the agent."""

    interactions: List[Dict[str, Any]] = field(default_factory=list)
    max_size: int = 10

    def add(self, user_query: str, sql_query: str, result: QueryResult):
        """Add an interaction to memory."""
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "user_query": user_query,
            "sql_query": sql_query,
            "success": result.success,
            "row_count": result.row_count if result.success else 0,
            "error": result.error if not result.success else None,
        }
        self.interactions.append(interaction)

        # Keep only recent interactions
        if len(self.interactions) > self.max_size:
            self.interactions.pop(0)

    def get_recent(self, n: int = 5) -> List[Dict[str, Any]]:
        """Get recent interactions."""
        return self.interactions[-n:]

    def get_context(self) -> str:
        """Get memory context as string for prompts."""
        if not self.interactions:
            return ""

        context_parts = ["## Recent Query History\n"]
        for i, interaction in enumerate(self.get_recent(), 1):
            context_parts.append(f"{i}. User: {interaction['user_query']}")
            context_parts.append(f"   SQL: {interaction['sql_query']}")
            if interaction["success"]:
                context_parts.append(f"   Result: {interaction['row_count']} rows returned")
            else:
                context_parts.append(f"   Error: {interaction['error']}")
            context_parts.append("")

        return "\n".join(context_parts)


class SQLAgent:
    """Main SQL Agent that converts natural language to SQL and executes queries."""

    def __init__(
        self,
        llm_provider: LLMProvider,
        executor: QueryExecutor,
        schema_introspector: SchemaIntrospector,
        error_corrector: Optional[ErrorCorrector] = None,
        tool_registry: Optional[ToolRegistry] = None,
        enable_error_correction: bool = True,
        enable_tools: bool = True,
        max_iterations: int = 5,
        memory_size: int = 10,
    ):
        """Initialize SQL Agent.

        Args:
            llm_provider: LLM provider for SQL generation
            executor: Query executor
            schema_introspector: Schema introspector
            error_corrector: Error corrector (optional, created if None)
            tool_registry: Tool registry (optional)
            enable_error_correction: Enable automatic error correction
            enable_tools: Enable tool usage
            max_iterations: Maximum iterations for error correction loop
            memory_size: Size of agent memory
        """
        self.llm_provider = llm_provider
        self.executor = executor
        self.schema_introspector = schema_introspector
        self.error_corrector = error_corrector or ErrorCorrector(llm_provider)
        self.tool_registry = tool_registry
        self.enable_error_correction = enable_error_correction
        self.enable_tools = enable_tools
        self.max_iterations = max_iterations
        self.memory = AgentMemory(max_size=memory_size)

        # Get schema context
        self.schema_context = self.schema_introspector.get_schema_prompt()

        logger.info("SQL Agent initialized")

    def generate_sql(self, user_query: str) -> str:
        """Generate SQL query from natural language.

        Args:
            user_query: Natural language query

        Returns:
            Generated SQL query
        """
        # Build prompt
        prompt_parts = [
            "Convert the following natural language query to SQL:",
            "",
            f"Query: {user_query}",
            "",
            self.schema_context,
        ]

        # Add memory context
        memory_context = self.memory.get_context()
        if memory_context:
            prompt_parts.append(memory_context)

        # Add tool information if enabled
        if self.enable_tools and self.tool_registry:
            tool_list = self.tool_registry.list_tools()
            if tool_list:
                prompt_parts.append("## Available Tools\n")
                for tool in tool_list:
                    prompt_parts.append(f"- {tool['name']}: {tool['description']}")
                prompt_parts.append("")

        prompt_parts.append(
            "Provide ONLY the SQL query. Do not include any explanation or markdown formatting."
        )

        prompt = "\n".join(prompt_parts)

        system_prompt = """You are an expert SQL developer. Your task is to convert natural language queries to accurate SQL queries.

Rules:
1. Generate valid SQL syntax
2. Use appropriate JOINs when needed
3. Use proper WHERE clauses for filtering
4. Return ONLY the SQL query, no explanations
5. Do not include markdown code blocks
6. Use SELECT statements only (read-only queries)"""

        try:
            sql_query = self.llm_provider.generate(prompt=prompt, system_prompt=system_prompt)

            # Clean up SQL query (remove markdown if present)
            sql_query = self._clean_sql_query(sql_query)

            logger.info(f"Generated SQL: {sql_query[:100]}...")
            return sql_query

        except Exception as e:
            logger.error(f"Error generating SQL: {e}")
            raise

    def _clean_sql_query(self, sql: str) -> str:
        """Clean SQL query from LLM response."""
        import re

        # Remove markdown code blocks
        sql = re.sub(r"```(?:sql)?\s*", "", sql)
        sql = re.sub(r"```\s*", "", sql)

        # Remove leading/trailing whitespace
        sql = sql.strip()

        # Remove trailing semicolon if present (optional)
        if sql.endswith(";"):
            sql = sql[:-1].strip()

        return sql

    def query(self, user_query: str, use_tools: bool = True) -> Dict[str, Any]:
        """Process a natural language query.

        Args:
            user_query: Natural language query
            use_tools: Whether to use tools for post-processing

        Returns:
            Dictionary with query results and metadata
        """
        logger.info(f"Processing query: {user_query}")

        iteration = 0
        current_query = None
        last_error = None

        while iteration < self.max_iterations:
            iteration += 1

            try:
                # Generate SQL
                if current_query is None:
                    sql_query = self.generate_sql(user_query)
                # Use error corrector if we have a previous error
                elif self.enable_error_correction and last_error:
                    logger.info("Attempting to correct query...")
                    previous_queries = [iq["sql_query"] for iq in self.memory.get_recent(3)]
                    sql_query = self.error_corrector.correct_query(
                        current_query, last_error, self.schema_context, previous_queries
                    )
                else:
                    sql_query = current_query

                # Execute query
                result = self.executor.execute(sql_query)

                # Store in memory
                self.memory.add(user_query, sql_query, result)

                # If successful, return result
                if result.success:
                    response = {
                        "success": True,
                        "user_query": user_query,
                        "sql_query": sql_query,
                        "data": result.data,
                        "columns": result.columns,
                        "row_count": result.row_count,
                        "execution_time": result.execution_time,
                        "iterations": iteration,
                    }

                    # Apply tools if enabled
                    if use_tools and self.enable_tools and self.tool_registry:
                        # Optionally summarize results
                        if result.data and len(result.data) > 0:
                            try:
                                summary_result = self.tool_registry.execute(
                                    "summarize_results",
                                    query=sql_query,
                                    results=result.data,
                                    columns=result.columns or [],
                                )
                                if summary_result.success:
                                    response["summary"] = summary_result.output
                            except Exception as e:
                                logger.warning(f"Tool execution failed: {e}")

                    return response

                # If failed, prepare for retry
                last_error = result.error
                current_query = sql_query

                if not self.enable_error_correction:
                    # Return error if correction is disabled
                    return {
                        "success": False,
                        "user_query": user_query,
                        "sql_query": sql_query,
                        "error": result.error,
                        "execution_time": result.execution_time,
                        "iterations": iteration,
                    }

                logger.warning(f"Query failed (iteration {iteration}): {result.error}")

            except Exception as e:
                logger.error(f"Error in query processing: {e}")
                return {
                    "success": False,
                    "user_query": user_query,
                    "error": str(e),
                    "iterations": iteration,
                }

        # Max iterations reached
        return {
            "success": False,
            "user_query": user_query,
            "sql_query": current_query or "N/A",
            "error": f"Failed after {self.max_iterations} iterations. Last error: {last_error}",
            "iterations": iteration,
        }

    def use_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Use a tool directly.

        Args:
            tool_name: Name of the tool
            **kwargs: Tool arguments

        Returns:
            Tool result
        """
        if not self.tool_registry:
            return {"success": False, "error": "No tool registry available"}

        result = self.tool_registry.execute(tool_name, **kwargs)
        return {"success": result.success, "output": result.output, "data": result.data}

    def get_memory(self) -> List[Dict[str, Any]]:
        """Get agent memory."""
        return self.memory.interactions

    def clear_memory(self):
        """Clear agent memory."""
        self.memory.interactions.clear()
        logger.info("Agent memory cleared")
