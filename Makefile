# Actions Vocabulary Testing Makefile

.PHONY: help install test test-quick test-verbose clean lint format check

help:  ## Show this help message
	@echo "Actions Vocabulary SHACL Testing"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Examples:"
	@echo "  make test                              # Run all tests"
	@echo "  make test-quick                        # Run quick tests"
	@echo "  make test-specific TEST=TestValidDataFiles::test_all_valid_files_pass"
	@echo "  make coverage                          # Generate coverage report"
	@echo "  make validate-syntax                   # Check TTL syntax"
	@echo "  make lint && make test                 # Full check"

# Project status
status:  ## Show project status overview
	@echo "📊 Actions Vocabulary Project Status"
	@echo "======================================="
	@echo "🗂️  Core Files:"
	@ls -la actions-*.ttl | awk '{print "  " $$NF " (" $$5 " bytes)"}'
	@echo ""
	@echo "🧪 Test Files:"
	@find tests/data -name "*.ttl" | wc -l | awk '{print "  " $$1 " test data files"}'
	@echo ""
	@echo "📝 Last Test Run:"
	@if [ -f .pytest_cache/CACHEDIR.TAG ]; then \
		echo "  Cache exists (tests have been run)"; \
	else \
		echo "  No test cache found (run: make test)"; \
	fi
	@echo ""
	@echo "💡 Quick commands: make test, make coverage, make help"

install:  ## Install dependencies with uv
	uv sync
	@echo "✅ Dependencies installed"

install-dev:  ## Install with dev dependencies  
	uv sync --extra dev
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
	@if [ -z "$(TEST)" ]; then echo "❌ Usage: make test-specific TEST=test_name"; exit 1; fi
	uv run pytest tests/test_shacl_validation.py::$(TEST)

test-valid:  ## Test only valid data files
	uv run pytest -k "TestValidDataFiles"

test-invalid:  ## Test only invalid data files  
	uv run pytest -k "TestInvalidDataFiles"

test-consistency:  ## Test only ontology consistency
	uv run pytest tests/test_ontology_consistency.py

clean:  ## Clean test artifacts
	rm -rf tests/__pycache__
	rm -rf .pytest_cache
	rm -rf htmlcov/
	rm -rf .coverage
	@echo "🧹 Cleaned test artifacts"

lint:  ## Run linting (if dev dependencies installed)
	@echo "🔍 Running code linting..."
	uv run --extra dev isort tests/ --check-only
	uv run --extra dev black tests/ --check
	@echo "✅ Linting passed"

format:  ## Format code (if dev dependencies installed)
	@echo "🎨 Formatting code..."
	uv run --extra dev isort tests/
	uv run --extra dev black tests/
	@echo "✅ Code formatted"

check: lint test  ## Run linting and tests

# Direct validation commands
validate-ontology:  ## Validate ontology syntax
	@echo "🔍 Validating ontology syntax..."
	uv run python -c "import rdflib; g = rdflib.Graph(); g.parse('actions-vocabulary.ttl', format='turtle'); print('✅ Ontology syntax is valid')"

validate-shapes:  ## Validate SHACL shapes syntax
	@echo "🔍 Validating SHACL shapes syntax..."
	uv run python -c "import rdflib; g = rdflib.Graph(); g.parse('actions-shapes.ttl', format='turtle'); print('✅ SHACL shapes syntax is valid')"

validate-syntax: validate-ontology validate-shapes  ## Validate all TTL file syntax

# Quick validation without full test suite
quick-validate:  ## Quick validation of core files against shapes
	@echo "⚡ Running quick SHACL validation..."
	uv run python -c "\
	import pyshacl; \
	import rdflib; \
	g = rdflib.Graph(); \
	g.parse('tests/data/valid-simple.ttl', format='turtle'); \
	s = rdflib.Graph(); \
	s.parse('actions-shapes.ttl', format='turtle'); \
	o = rdflib.Graph(); \
	o.parse('actions-vocabulary.ttl', format='turtle'); \
	r = pyshacl.validate(g, shacl_graph=s, ont_graph=o, abort_on_first=False); \
	print('✅ Quick validation passed' if r[0] else '❌ Quick validation failed')"

# Show ontology structure
show-structure:  ## Show class hierarchy from ontology
	@echo "📋 Ontology Class Structure:"
	@uv run python -c "import rdflib; from rdflib import RDF, OWL; g = rdflib.Graph(); g.parse('actions-vocabulary.ttl', format='turtle'); [print(f'  {str(cls).split(\"/\")[-1]}') for cls in g.subjects(RDF.type, OWL.Class) if 'actions' in str(cls)]"

# Development shortcuts
dev-install:  ## Install with dev dependencies
	uv sync --extra dev
	@echo "✅ Dev dependencies installed"

# File watching (requires entr or inotify-tools)
watch:  ## Watch files and run tests on changes
	@echo "👀 Starting file watcher..."
	@if command -v entr >/dev/null 2>&1; then \
		find tests/ actions-*.ttl -name "*.py" -o -name "*.ttl" | entr -c make test-quick; \
	elif command -v inotifywait >/dev/null 2>&1; then \
		echo "📝 Using inotifywait for file watching..."; \
		while true; do \
			inotifywait -e modify tests/ actions-*.ttl --format '%w%f' -q && make test-quick; \
		done; \
	else \
		echo "❌ File watcher not available. Install: 'sudo apt install entr' or 'sudo apt install inotify-tools'"; \
		exit 1; \
	fi

# Coverage reporting (if pytest-cov installed)
coverage:  ## Run tests with coverage reporting
	@echo "📊 Running tests with coverage..."
	uv run --extra dev pytest --cov=tests --cov-report=html --cov-report=term-missing
	@echo "📊 Coverage report generated in htmlcov/"
