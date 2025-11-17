#!/usr/bin/env python3
"""Basic demo of SQL Agent."""
import sys
import os
import logging

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config import Config
from src.llm import create_llm_provider
from src.executor import QueryExecutor
from src.schema_introspection import SchemaIntrospector
from src.tools import create_tool_registry
from src.agent import SQLAgent

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Run basic demo."""
    print("=" * 60)
    print("SQL Agent - Basic Demo")
    print("=" * 60)
    print()
    
    # Load configuration
    config = Config.from_env()
    
    # Override with defaults if no API key
    if not config.llm.api_key:
        print("Warning: No API key found. Using mock mode.")
        print("Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable.")
        print()
        # For demo purposes, we'll show the structure even without API key
        # In production, you'd want to handle this differently
    
    # Initialize components
    try:
        llm_provider = create_llm_provider(config.llm)
    except Exception as e:
        print(f"Error initializing LLM provider: {e}")
        print("\nTo run this demo, you need:")
        print("1. Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable")
        print("2. Or configure a local LLM provider")
        return
    
    executor = QueryExecutor(
        db_path=config.database.path,
        db_type=config.database.type,
        safe_mode=config.safety.safe_mode,
        blocked_keywords=config.safety.blocked_keywords,
        max_query_length=config.safety.max_query_length
    )
    
    schema_introspector = SchemaIntrospector(
        db_path=config.database.path,
        db_type=config.database.type
    )
    
    tool_registry = create_tool_registry(executor, llm_provider, schema_introspector)
    
    # Create agent
    agent = SQLAgent(
        llm_provider=llm_provider,
        executor=executor,
        schema_introspector=schema_introspector,
        tool_registry=tool_registry if config.agent.enable_tools else None,
        enable_error_correction=config.agent.enable_error_correction,
        enable_tools=config.agent.enable_tools,
        max_iterations=config.agent.max_iterations,
        memory_size=config.agent.memory_size
    )
    
    # Example queries
    queries = [
        "How many employees are in the Engineering department?",
        "What is the average salary by department?",
        "Show me all active projects and the employees working on them",
    ]
    
    print("Running example queries...\n")
    
    for i, query in enumerate(queries, 1):
        print(f"Query {i}: {query}")
        print("-" * 60)
        
        result = agent.query(query)
        
        if result["success"]:
            print(f"SQL: {result['sql_query']}")
            print(f"Rows returned: {result['row_count']}")
            print(f"Execution time: {result['execution_time']:.3f}s")
            
            if result.get("data"):
                print("\nResults:")
                # Show first few rows
                for row in result["data"][:5]:
                    print(f"  {row}")
                if len(result["data"]) > 5:
                    print(f"  ... and {len(result['data']) - 5} more rows")
            
            if result.get("summary"):
                print(f"\nSummary:\n{result['summary']}")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
        
        print("\n")
    
    print("=" * 60)
    print("Demo completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()

