# Contributing to SQL Agent

Thank you for your interest in contributing to SQL Agent! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Celebrate diverse perspectives

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/sql-agent.git`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Install development dependencies: `make install-dev`
5. Initialize the database: `make setup-db`

## Development Workflow

### Code Style

We use:
- **Black** for code formatting
- **Ruff** for linting
- **mypy** for type checking

Format your code before committing:
```bash
make format
```

Check code quality:
```bash
make lint
```

### Testing

Write tests for new features:
```bash
make test
```

Run with coverage:
```bash
make test-cov
```

### Commit Messages

Follow conventional commits:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation
- `test:` for tests
- `refactor:` for code refactoring
- `chore:` for maintenance

Example:
```
feat: add PostgreSQL support
fix: handle None values in query results
docs: update README with new examples
```

## Pull Request Process

1. Ensure all tests pass: `make check`
2. Update documentation if needed
3. Add changelog entry if applicable
4. Create a pull request with a clear description
5. Respond to review feedback

## Project Structure

```
sql-agent/
├── src/              # Core source code
├── examples/         # Example scripts
├── tests/            # Test suite
├── data/             # Sample data
└── docs/             # Additional documentation
```

## Adding New Features

1. Discuss major changes in an issue first
2. Implement with tests
3. Update documentation
4. Add examples if applicable
5. Update CHANGELOG.md

## Reporting Bugs

Use the GitHub issue tracker and include:
- Description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Environment details (Python version, OS, etc.)
- Error messages or logs

## Questions?

Open a discussion or issue on GitHub. We're happy to help!

