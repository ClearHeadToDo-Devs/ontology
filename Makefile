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

test:  ## Run all tests
	./run_tests.py

test-quick:  ## Run only quick tests (skip slow ones)
	./run_tests.py --quick

test-verbose:  ## Run tests with verbose output
	./run_tests.py --verbose --verbose-validation

test-specific:  ## Run specific test (use TEST=test_name)
	./run_tests.py tests/test_shacl_validation.py::$(TEST)

test-valid:  ## Test only valid data files
	./run_tests.py -k "TestValidDataFiles"

test-invalid:  ## Test only invalid data files  
	./run_tests.py -k "TestInvalidDataFiles"

test-consistency:  ## Test only ontology consistency
	./run_tests.py tests/test_ontology_consistency.py

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
	./run_tests.py --cov=tests --cov-report=html
	@echo "Coverage report generated in htmlcov/"