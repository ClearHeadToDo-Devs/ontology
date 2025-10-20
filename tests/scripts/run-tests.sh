#!/bin/bash

echo "=========================================="
echo "SHACL Validation Test Suite"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if pySHACL is installed
if ! command -v pyshacl &> /dev/null; then
    echo -e "${RED}ERROR: pyshacl is not installed${NC}"
    echo "Please run: pip install pyshacl"
    exit 1
fi

echo "Testing VALID data (should pass)..."
echo "-----------------------------------"

# Test valid data
pyshacl -s ../../actions-shapes.ttl -d ../data/valid-simple.ttl -f turtle > valid-results.ttl 2>&1
VALID_EXIT_CODE=$?

if [ $VALID_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ VALID data test PASSED${NC}"
    echo "All valid test cases conform to SHACL shapes"
else
    echo -e "${RED}❌ VALID data test FAILED${NC}"
    echo "Some valid test cases failed validation:"
    cat valid-results.ttl
fi

echo ""
echo "Testing INVALID data (should fail)..."
echo "------------------------------------"

# Test invalid data  
pyshacl -s ../../actions-shapes.ttl -d ../data/invalid-simple.ttl -f turtle > invalid-results.ttl 2>&1
INVALID_EXIT_CODE=$?

if [ $INVALID_EXIT_CODE -ne 0 ]; then
    echo -e "${GREEN}✅ INVALID data test PASSED${NC}"
    echo "Invalid test cases properly failed validation"
    echo ""
    echo -e "${YELLOW}Validation errors found (as expected):${NC}"
    cat invalid-results.ttl | head -20
    echo "... (see invalid-results.ttl for full output)"
else
    echo -e "${RED}❌ INVALID data test FAILED${NC}"
    echo "Invalid test cases should have failed but didn't!"
fi

echo ""
echo "=========================================="
echo "Test Summary:"
if [ $VALID_EXIT_CODE -eq 0 ] && [ $INVALID_EXIT_CODE -ne 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED${NC}"
    echo "✅ Valid data conforms to shapes"
    echo "✅ Invalid data properly rejected"
else
    echo -e "${RED}❌ SOME TESTS FAILED${NC}"
    echo "Check the results above and fix any issues"
fi
echo "=========================================="
