#!/usr/bin/env python3
"""Setup verification script for SQL Agent."""
import os
import sys

def check_imports():
    """Check if all required modules can be imported."""
    print("Checking imports...")
    try:
        from src.config import Config
        from src.llm import create_llm_provider
        from src.executor import QueryExecutor
        from src.schema_introspection import SchemaIntrospector
        from src.tools import create_tool_registry
        from src.agent import SQLAgent
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def check_database():
    """Check if sample database exists."""
    print("Checking database...")
    db_path = "data/sample.db"
    if os.path.exists(db_path):
        print(f"✓ Database found: {db_path}")
        return True
    else:
        print(f"✗ Database not found: {db_path}")
        print("  Run: sqlite3 data/sample.db < data/schema.sql")
        return False

def check_dependencies():
    """Check if required packages are installed."""
    print("Checking dependencies...")
    required = ['yaml', 'sqlite3']
    optional = ['openai', 'anthropic', 'requests']
    
    missing_required = []
    for pkg in required:
        try:
            __import__(pkg)
            print(f"✓ {pkg}")
        except ImportError:
            missing_required.append(pkg)
            print(f"✗ {pkg} (required)")
    
    for pkg in optional:
        try:
            __import__(pkg)
            print(f"✓ {pkg} (optional)")
        except ImportError:
            print(f"○ {pkg} (optional, not installed)")
    
    if missing_required:
        print(f"\nMissing required packages: {', '.join(missing_required)}")
        return False
    
    return True

def check_api_keys():
    """Check if API keys are configured."""
    print("Checking API keys...")
    openai_key = os.getenv('OPENAI_API_KEY')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    
    if openai_key:
        print("✓ OPENAI_API_KEY found")
        return True
    elif anthropic_key:
        print("✓ ANTHROPIC_API_KEY found")
        return True
    else:
        print("○ No API keys found (set OPENAI_API_KEY or ANTHROPIC_API_KEY)")
        print("  For local models, ensure Ollama or similar is running")
        return False

def main():
    """Run all checks."""
    print("=" * 60)
    print("SQL Agent Setup Verification")
    print("=" * 60)
    print()
    
    checks = [
        ("Imports", check_imports),
        ("Dependencies", check_dependencies),
        ("Database", check_database),
        ("API Keys", check_api_keys),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n{name}:")
        print("-" * 60)
        result = check_func()
        results.append((name, result))
    
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{name}: {status}")
        if not result:
            all_passed = False
    
    print()
    if all_passed:
        print("✓ All checks passed! You're ready to run the demos.")
        print("\nTry: python examples/demo_basic.py")
    else:
        print("✗ Some checks failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()

