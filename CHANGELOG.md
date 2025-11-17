# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-11-16

### Added
- Initial release of SQL Agent
- Natural language to SQL conversion using LLMs
- Support for OpenAI, Anthropic, and local LLM providers
- Database schema introspection and reflection
- Query execution engine with safety checks
- Automatic error correction with retry loop
- Short-term memory for agent context
- Optional tools: Explain Query Plan, Fix Query, Summarize Results
- YAML and environment variable configuration
- Comprehensive logging to console and file
- Streaming LLM response support
- Sample database and schema
- Basic and advanced demo examples
- Unit tests for core components
- Docker support
- Comprehensive README with architecture diagrams and examples

### Security
- Safe mode blocks destructive SQL operations (DELETE, DROP, ALTER, etc.)
- Query validation and length limits
- Read-only mode support

### Documentation
- Full README with quickstart guide
- Architecture diagrams
- Example conversations
- Troubleshooting guide
- Performance benchmarks
- API documentation

