#!/usr/bin/env python3
"""Advanced demo of SQL Agent with tools and error correction."""
import logging
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.agent import SQLAgent
from src.config import Config
from src.executor import QueryExecutor
from src.llm import create_llm_provider
from src.schema_introspection import SchemaIntrospector
from src.tools import create_tool_registry

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def main():
    """Run advanced demo."""
    print("=" * 60)
    print("SQL Agent - Advanced Demo")
    print("=" * 60)
    print()

    # Load configuration
    config = Config.from_env()

    # Initialize components
    try:
        llm_provider = create_llm_provider(config.llm)
    except Exception as e:
        print(f"Error initializing LLM provider: {e}")
        return

    executor = QueryExecutor(
        db_path=config.database.path,
        db_type=config.database.type,
        safe_mode=config.safety.safe_mode,
    )

    schema_introspector = SchemaIntrospector(
        db_path=config.database.path, db_type=config.database.type
    )

    tool_registry = create_tool_registry(executor, llm_provider, schema_introspector)

    # Create agent
    agent = SQLAgent(
        llm_provider=llm_provider,
        executor=executor,
        schema_introspector=schema_introspector,
        tool_registry=tool_registry,
        enable_error_correction=True,
        enable_tools=True,
        max_iterations=5,
        memory_size=10,
    )

    # Interactive mode
    print("Enter natural language queries (type 'quit' to exit, 'memory' to see history)")
    print("=" * 60)
    print()

    while True:
        try:
            user_query = input("Query: ").strip()

            if not user_query:
                continue

            if user_query.lower() == "quit":
                break

            if user_query.lower() == "memory":
                memory = agent.get_memory()
                print("\nAgent Memory:")
                for i, interaction in enumerate(memory, 1):
                    print(f"{i}. {interaction['user_query']}")
                    print(f"   SQL: {interaction['sql_query']}")
                    print(f"   Success: {interaction['success']}")
                print()
                continue

            # Process query
            result = agent.query(user_query, use_tools=True)

            print("\n" + "-" * 60)
            if result["success"]:
                print(f"✓ Success (iterations: {result['iterations']})")
                print(f"SQL: {result['sql_query']}")
                print(f"Rows: {result['row_count']} | Time: {result['execution_time']:.3f}s")

                if result.get("data"):
                    print("\nResults:")
                    for row in result["data"][:10]:
                        print(f"  {row}")
                    if len(result["data"]) > 10:
                        print(f"  ... {len(result['data']) - 10} more rows")

                if result.get("summary"):
                    print(f"\nSummary:\n{result['summary']}")
            else:
                print("✗ Failed")
                print(f"Error: {result.get('error', 'Unknown error')}")
                print(f"SQL: {result.get('sql_query', 'N/A')}")

            print("-" * 60 + "\n")

        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {e}\n")

    print("=" * 60)
    print("Demo completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
