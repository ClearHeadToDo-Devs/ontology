# Actions Vocabulary: Bash to Pytest Migration

This document summarizes the migration from bash script testing to pytest-based testing for the Actions Vocabulary SHACL validation.

## 🎯 **Completed Goals**

✅ **Python Project Setup with uv**
- Created proper `pyproject.toml` with dependencies (pytest, pyshacl, rdflib) 
- Used uv for dependency management instead of global pip installs
- Project structure follows Python testing best practices

✅ **Test Data Organization** 
- Moved inline test strings from code to dedicated `.ttl` files
- Organized into `tests/data/valid/` and `tests/data/invalid/` directories
- Created focused test scenarios with individual files:
  - `minimal-root-action.ttl` - Basic valid root action
  - `root-with-project.ttl` - Root action with project
  - `recurrence-action.ttl` - Recurring action patterns
  - `hierarchy-complete.ttl` - Full 5-level hierarchy
  - `invalid-priority.ttl` - Priority out of range
  - `invalid-context-format.ttl` - Context not following GTD format
  - `temporal-inconsistency.ttl` - Completion before schedule
  - And more focused test cases

✅ **PyShacl Library Integration**
- Replaced CLI calls with direct `pyshacl.validate()` library usage
- Created fixtures for ontology and shapes graph loading
- Implemented proper test report generation and saving

✅ **CLI Compatibility**
- Created `run_tests.py` with same interface as original `test-runner.sh`
- Supports `--verbose`, `--quick`, `--verbose-validation` flags
- Added `Makefile` with convenient targets (`make test`, `make test-quick`, etc.)

✅ **Improved Test Structure**
- Parametrized tests for testing multiple scenarios efficiently
- Test classes organized by functionality (valid files, invalid files, etc.)
- Proper pytest fixtures and configuration
- Better error reporting with violation details

## 🚧 **Current Status & Challenges**

### **SHACL Validation Complexity**
The migration revealed that SHACL validation has different behaviors when:

1. **Without Ontology** (CLI default): Faster, fewer datatype conflicts, but misses some constraints
2. **With Ontology** (library with inference): More comprehensive, but can have datatype mismatches

**Key Finding**: Some constraints require ontology inference to work properly:
- Priority range validation (`maxInclusive 4`) works better with ontology
- Context pattern validation works regardless 
- SPARQL-based constraints need ontology for class hierarchy understanding

### **Datatype Issues Identified**
- SHACL shapes expect specific XSD datatypes (`xsd:nonNegativeInteger`, `xsd:positiveInteger`)
- Test data uses `xsd:integer` which can cause validation conflicts
- Solution: Created smart validation that tries both approaches

## 🔧 **Project Structure**

```
ontology/
├── pyproject.toml              # uv project config with dependencies
├── run_tests.py               # Main test runner (CLI equivalent)  
├── Makefile                   # Convenient make targets
├── actions-vocabulary.ttl     # Ontology (unchanged)
├── actions-shapes.ttl         # SHACL shapes (unchanged)
└── tests/
    ├── __init__.py
    ├── conftest.py           # Pytest fixtures and configuration
    ├── utils.py              # Test utilities (validation helpers)
    ├── test_shacl_validation.py     # Basic SHACL validation tests
    ├── test_smart_validation.py     # Advanced validation scenarios
    ├── test_ontology_consistency.py # Ontology structure tests
    ├── results/              # Validation reports saved here
    └── data/
        ├── valid/           # Valid test cases
        │   ├── minimal-root-action.ttl
        │   ├── root-with-project.ttl
        │   ├── recurrence-action.ttl
        │   └── hierarchy-complete.ttl
        └── invalid/         # Invalid test cases
            ├── invalid-priority.ttl
            ├── invalid-context-format.ttl
            ├── temporal-inconsistency.ttl
            └── recurrence-both-termination.ttl
```

## 🚀 **Usage Examples**

### **Basic Testing**
```bash
# Install dependencies
uv sync

# Run all tests
./run_tests.py

# Quick tests only 
./run_tests.py --quick

# Verbose SHACL output
./run_tests.py --verbose-validation

# Using make
make test
make test-quick  
make test-verbose
```

### **Advanced Testing**
```bash
# Test specific files
./run_tests.py -- -k "test_valid"
./run_tests.py -- -k "TestSmartValidation"

# Test with coverage
make coverage
```

## ✨ **Key Improvements Over Bash Version**

1. **Better Error Reporting**: Detailed violation messages with focus nodes and paths
2. **Parametrized Testing**: Easy to test multiple scenarios without code duplication
3. **Smart Validation**: Handles both ontology-dependent and independent constraints
4. **Fixture System**: Reusable test components (graph loading, validators)
5. **Organized Test Data**: Focused test files instead of large mixed files
6. **Python Ecosystem**: Integration with IDEs, debuggers, coverage tools

## 🏁 **Getting Started**

1. **Setup**: `uv sync` to install dependencies
2. **Run Tests**: `./run_tests.py` or `make test`
3. **Review Reports**: Check `tests/results/` for detailed SHACL validation reports
4. **Add Tests**: Create new `.ttl` files in `tests/data/valid/` or `tests/data/invalid/`

## 📋 **Next Steps** 

- [ ] Resolve remaining datatype constraint conflicts
- [ ] Add integration tests with real-world ontology usage scenarios  
- [ ] Create test data generation utilities
- [ ] Add performance benchmarking against bash version
- [ ] Document constraint testing patterns for future ontology work

---

The pytest migration provides a solid foundation for ontology testing with better organization, reporting, and extensibility than the original bash approach.