.PHONY: help install dev lint format type-check test test-cov check clean

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install the package in editable mode
	pip install -e .

dev: ## Install with all development dependencies
	pip install -e ".[dev,all-ai]"

lint: ## Run Ruff linter and formatter check
	ruff check .
	ruff format --check .

format: ## Auto-format code with Ruff
	ruff check --fix .
	ruff format .

type-check: ## Run mypy type checker
	mypy . --ignore-missing-imports

test: ## Run tests with pytest
	pytest

test-cov: ## Run tests with coverage report
	pytest --cov --cov-report=term-missing

check: lint type-check test ## Run all checks (lint + type-check + test)

clean: ## Remove build artefacts and caches
	rm -rf build/ dist/ *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
