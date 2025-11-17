.PHONY: help install install-dev test lint format clean run-demo setup-db docker-build docker-run

help: ## Show this help message
	@echo "SQL Agent - Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	pip install -e .

install-dev: ## Install development dependencies
	pip install -e ".[dev,all]"

setup-db: ## Initialize sample database
	sqlite3 data/sample.db < data/schema.sql
	@echo "Database initialized!"

verify: ## Verify setup
	python setup_verify.py

test: ## Run tests
	pytest tests/ -v

test-cov: ## Run tests with coverage
	pytest tests/ --cov=src --cov-report=html --cov-report=term

lint: ## Run linters
	ruff check src/ tests/ examples/
	mypy src/

format: ## Format code
	black src/ tests/ examples/
	ruff check --fix src/ tests/ examples/

clean: ## Clean build artifacts
	rm -rf build/ dist/ *.egg-info .pytest_cache .coverage htmlcov/
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

run-demo: ## Run basic demo
	python examples/demo_basic.py

run-demo-advanced: ## Run advanced demo
	python examples/demo_advanced.py

docker-build: ## Build Docker image
	docker build -t sql-agent:latest .

docker-run: ## Run Docker container
	docker run --rm -e OPENAI_API_KEY=$${OPENAI_API_KEY} sql-agent:latest

check: lint test ## Run all checks (lint + test)

ci: clean install-dev check ## Run CI pipeline locally

