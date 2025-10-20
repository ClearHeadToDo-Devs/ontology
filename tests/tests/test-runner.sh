#!/bin/bash

# SHACL Test Runner for Actions Vocabulary
# Usage: ./test-runner.sh [--verbose] [--quick] [--help]

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SHAPES_FILE="actions-shapes.ttl"
VERBOSE=false
QUICK=false
TEST_DIR="$(dirname "$0")"
DATA_DIR="$TEST_DIR/data"
SCRIPTS_DIR="$TEST_DIR/scripts"
RESULTS_DIR="$TEST_DIR/results"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --quick|-q)
            QUICK=true
            shift
            ;;
        --help|-h)
            echo "SHACL Test Runner for Actions Vocabulary"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -v, --verbose    Show detailed validation output"
            echo "  -q, --quick      Run only basic tests (skip complex cases)"
            echo "  -h, --help       Show this help message"
            echo ""
            echo "Test files:"
            echo "  data/valid-*.ttl     - Should pass validation"
            echo "  data/invalid-*.ttl   - Should fail validation"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Utility functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

log_error() {
    echo -e "${RED}[FAIL]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Setup results directory
mkdir -p "$RESULTS_DIR"

# Check dependencies
check_dependencies() {
    if ! command -v pyshacl &> /dev/null; then
        log_error "pyshacl is not installed. Install with: pip install pyshacl"
        exit 1
    fi
    
    if [ ! -f "$SHAPES_FILE" ]; then
        log_error "SHACL shapes file not found: $SHAPES_FILE"
        exit 1
    fi
}

# Test a single file
test_file() {
    local file="$1"
    local should_pass="$2"
    local test_name="$(basename "$file" .ttl)"
    
    log_info "Testing: $test_name"
    
    # Run validation
    local output_file="$RESULTS_DIR/${test_name}-result.ttl"
    local validation_cmd="pyshacl -s \"$SHAPES_FILE\" -d \"$file\""
    
    if [ "$VERBOSE" = true ]; then
        validation_cmd="$validation_cmd -v"
    fi
    
    # Capture both output and exit code
    if eval "$validation_cmd" > "$output_file" 2>&1; then
        local exit_code=0
    else
        local exit_code=1
    fi
    
    # Check if result matches expectation
    if [ "$should_pass" = true ] && [ $exit_code -eq 0 ]; then
        log_success "$test_name - Validation passed as expected"
        return 0
    elif [ "$should_pass" = false ] && [ $exit_code -ne 0 ]; then
        log_success "$test_name - Validation failed as expected"
        return 0
    else
        if [ "$should_pass" = true ]; then
            log_error "$test_name - Expected to pass but failed"
        else
            log_error "$test_name - Expected to fail but passed"
        fi
        
        if [ "$VERBOSE" = true ]; then
            echo "--- Validation output ---"
            cat "$output_file"
            echo "--- End validation output ---"
        fi
        return 1
    fi
}

# Main test execution
main() {
    echo "=========================================="
    echo "SHACL Validation Test Suite"
    echo "Actions Vocabulary $(date)"
    echo "=========================================="
    echo ""
    
    check_dependencies
    
    local total_tests=0
    local passed_tests=0
    local failed_tests=0
    
    # Test valid files (should pass)
    log_info "Testing VALID examples (should pass validation)..."
    for file in "$DATA_DIR"/valid-*.ttl; do
        if [ -f "$file" ]; then
            if [ "$QUICK" = true ] && [[ "$file" == *"complex"* ]]; then
                log_warning "Skipping complex test in quick mode: $(basename "$file")"
                continue
            fi
            
            ((total_tests++))
            if test_file "$file" true; then
                ((passed_tests++))
            else
                ((failed_tests++))
            fi
        fi
    done
    
    echo ""
    
    # Test invalid files (should fail)
    log_info "Testing INVALID examples (should fail validation)..."
    for file in "$DATA_DIR"/invalid-*.ttl; do
        if [ -f "$file" ]; then
            if [ "$QUICK" = true ] && [[ "$file" == *"examples"* ]]; then
                log_warning "Skipping complex test in quick mode: $(basename "$file")"
                continue
            fi
            
            ((total_tests++))
            if test_file "$file" false; then
                ((passed_tests++))
            else
                ((failed_tests++))
            fi
        fi
    done
    
    # Summary
    echo ""
    echo "=========================================="
    echo "Test Summary:"
    echo "Total tests: $total_tests"
    echo "Passed: $passed_tests"
    echo "Failed: $failed_tests"
    
    if [ $failed_tests -eq 0 ]; then
        log_success "🎉 ALL TESTS PASSED!"
        echo "✅ Valid data conforms to shapes"
        echo "✅ Invalid data properly rejected"
    else
        log_error "❌ $failed_tests TEST(S) FAILED"
        echo "Check validation results in: $RESULTS_DIR/"
    fi
    echo "=========================================="
    
    # Exit with error code if any tests failed
    exit $failed_tests
}

main "$@"
