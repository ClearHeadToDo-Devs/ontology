# Actions Vocabulary Testing Makefile

.PHONY: help install test test-quick test-verbose clean lint format check

help:  ## Show this help message
	@echo "Actions Vocabulary SHACL Testing"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies with uv
	uv sync
	@echo "✅ Dependencies installed"

install-dev:  ## Install with dev dependencies  
	uv sync --group dev
	@echo "✅ Dev dependencies installed"

# New pytest-based commands
test-help:  ## Show pytest help and available options
	uv run pytest --help

test:  ## Run all tests
	uv run pytest

test-quick:  ## Run only quick tests (skip slow ones)
	uv run pytest --quick

test-verbose:  ## Run tests with verbose output
	uv run pytest -v --verbose-validation

test-specific:  ## Run specific test (use TEST=test_name)
	uv run pytest tests/test_shacl_validation.py::$(TEST)

test-valid:  ## Test only valid data files
	uv run pytest -k "TestValidDataFiles"

test-invalid:  ## Test only invalid data files  
	uv run pytest -k "TestInvalidDataFiles"

test-consistency:  ## Test only ontology consistency
	uv run pytest tests/test_ontology_consistency.py

clean:  ## Clean test artifacts
	rm -rf tests/results/*
	rm -rf tests/__pycache__
	rm -rf .pytest_cache
	@echo "✅ Cleaned test artifacts"

lint:  ## Run linting (if dev dependencies installed)
	uv run --group dev isort tests/ --check-only
	uv run --group dev black tests/ --check

format:  ## Format code (if dev dependencies installed)
	uv run --group dev isort tests/
	uv run --group dev black tests/
	@echo "✅ Code formatted"

check: lint test  ## Run linting and tests

# Development shortcuts
dev-install:  ## Install with dev dependencies
	uv sync --group dev

# File watching (requires entr: brew install entr or apt install entr)
watch:  ## Watch files and run tests on changes
	find tests/ actions-*.ttl -name "*.py" -o -name "*.ttl" | entr -c make test-quick

# Coverage reporting (if pytest-cov installed)
coverage:  ## Run tests with coverage reporting
	uv run pytest --cov=tests --cov-report=html --cov-report=term
	@echo "Coverage report generated in htmlcov/"