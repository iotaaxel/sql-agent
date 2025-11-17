# Quick Start Guide

Get SQL Agent running in 5 minutes!

## Prerequisites

- Python 3.9 or higher
- pip
- An API key from OpenAI or Anthropic (or a local LLM setup)

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd sql-agent

# Install dependencies
pip install -e ".[all]"  # Installs all LLM providers

# Or install minimal dependencies
pip install -e .
pip install openai  # or anthropic, depending on your provider
```

## Setup

1. **Set your API key:**
   ```bash
   export OPENAI_API_KEY="sk-..."
   # or
   export ANTHROPIC_API_KEY="sk-ant-..."
   ```

2. **Initialize the sample database:**
   ```bash
   sqlite3 data/sample.db < data/schema.sql
   ```

3. **Verify setup:**
   ```bash
   python setup.py
   ```

## Your First Query

Create a file `quick_test.py`:

```python
from src.config import Config
from src.llm import create_llm_provider
from src.executor import QueryExecutor
from src.schema_introspection import SchemaIntrospector
from src.tools import create_tool_registry
from src.agent import SQLAgent

# Load config
config = Config.from_env()

# Initialize components
llm = create_llm_provider(config.llm)
executor = QueryExecutor(db_path=config.database.path, safe_mode=True)
schema = SchemaIntrospector(db_path=config.database.path)
tools = create_tool_registry(executor, llm, schema)

# Create agent
agent = SQLAgent(llm, executor, schema, tool_registry=tools)

# Ask a question!
result = agent.query("How many employees are in Engineering?")

if result["success"]:
    print(f"Found {result['row_count']} results")
    print(result["data"])
else:
    print(f"Error: {result['error']}")
```

Run it:
```bash
python quick_test.py
```

## Next Steps

- Read the [full README](README.md) for detailed documentation
- Try the [advanced demo](examples/demo_advanced.py) for interactive mode
- Check out [examples](examples/) for more use cases
- Read [CONTRIBUTING.md](CONTRIBUTING.md) to contribute

## Troubleshooting

**"No API key found"**
- Make sure you've set `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`
- Check with: `echo $OPENAI_API_KEY`

**"Database not found"**
- Run: `sqlite3 data/sample.db < data/schema.sql`

**"Module not found"**
- Install dependencies: `pip install -e ".[all]"`

**Need help?**
- Check the [troubleshooting section](README.md#troubleshooting) in the README
- Open an issue on GitHub

