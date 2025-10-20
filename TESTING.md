# Testing Guide

This project uses pytest for SHACL validation testing of the Actions Vocabulary ontology.

## Quick Start

```bash
# Install dependencies
uv sync

# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Skip slow tests
uv run pytest --quick

# Show detailed SHACL validation reports
uv run pytest --verbose-validation
```

## Using Make (Optional)

```bash
make test              # Run all tests
make test-quick        # Skip slow tests  
make test-verbose      # Verbose output with SHACL details
make test-help         # Show pytest help
```

## Common Pytest Patterns

```bash
# Test specific files
uv run pytest tests/test_shacl_validation.py

# Test specific classes
uv run pytest -k "TestValidDataFiles"

# Test specific methods
uv run pytest -k "test_specific_valid_file"

# Run tests matching pattern
uv run pytest -k "valid and not complex"

# Stop on first failure
uv run pytest -x

# Show local variables on failures
uv run pytest -l

# Quiet mode (less output)
uv run pytest -q

# Very verbose mode
uv run pytest -vv
```

## Test Organization

```
tests/
├── data/
│   ├── valid/          # Test data that should pass validation
│   └── invalid/        # Test data that should fail validation  
├── results/            # SHACL validation reports (auto-generated)
├── conftest.py         # Pytest configuration and fixtures
├── utils.py            # Test utilities
├── test_shacl_validation.py     # Core SHACL validation tests
└── test_ontology_consistency.py # Ontology structure tests
```

## Custom Options

- `--quick` - Skip slow/complex tests (same as `-m "not slow"`)
- `--verbose-validation` - Show detailed SHACL violation reports

## Examples

```bash
# Run only validation tests, skip slow ones, show details
uv run pytest --quick --verbose-validation -k "validation"

# Test only invalid data with verbose output
uv run pytest -v -k "invalid"

# Run tests and generate HTML coverage report
uv run pytest --cov=tests --cov-report=html

# Debug specific failing test
uv run pytest -vv -s tests/test_shacl_validation.py::TestValidDataFiles::test_specific_valid_file
```

## Adding New Tests

1. **Valid data**: Add `.ttl` files to `tests/data/valid/`
2. **Invalid data**: Add `.ttl` files to `tests/data/invalid/`
3. **Custom tests**: Add to existing test classes or create new ones

The test system automatically discovers and tests all files in the data directories.