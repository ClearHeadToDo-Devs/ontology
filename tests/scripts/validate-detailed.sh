#!/bin/bash

echo "=========================================="
echo "Detailed SHACL Validation Report"
echo "=========================================="

# Function to run validation and show detailed results
validate_file() {
    local file=$1
    local description=$2
    
    echo ""
    echo "Testing: $description"
    echo "File: $file"
    echo "-----------------------------------"
    
    # Run validation with verbose output
    pyshacl -s actions-shapes.ttl -d "$file" -f turtle -v 2>&1 | tee "${file%.ttl}-validation.log"
    
    exit_code=$?
    if [ $exit_code -eq 0 ]; then
        echo "✅ CONFORMS - No violations found"
    else
        echo "❌ VIOLATIONS - See details above"
    fi
    
    return $exit_code
}

# Test individual constraint violations
echo "Creating specific constraint violation tests..."

# Test 1: Root action with wrong depth
cat > test-root-depth.ttl << 'EOF'
@prefix actions: <https://vocab.example.org/actions/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

actions:test1 a actions:RootAction ;
    actions:depth 1 ;
    actions:priority 2 ;
    actions:state actions:NotStarted ;
    actions:context "@computer" .
EOF

validate_file "test-root-depth.ttl" "Root action with incorrect depth"

# Test 2: Missing required properties
cat > test-missing-props.ttl << 'EOF'
@prefix actions: <https://vocab.example.org/actions/> .

actions:test2 a actions:RootAction ;
    actions:depth 0 ;
    actions:context "@computer" .
    # Missing priority and state
EOF

validate_file "test-missing-props.ttl" "Action missing required properties"

# Test 3: Invalid priority range
cat > test-invalid-priority.ttl << 'EOF'
@prefix actions: <https://vocab.example.org/actions/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

actions:test3 a actions:RootAction ;
    actions:depth 0 ;
    actions:priority 0 ;
    actions:state actions:NotStarted ;
    actions:context "@computer" .
EOF

validate_file "test-invalid-priority.ttl" "Action with invalid priority (0)"

# Test 4: Child action without parent
cat > test-orphan-child.ttl << 'EOF'
@prefix actions: <https://vocab.example.org/actions/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

actions:test4 a actions:ChildAction ;
    actions:depth 2 ;
    actions:priority 1 ;
    actions:state actions:NotStarted ;
    actions:context "@computer" .
    # Missing parentAction
EOF

validate_file "test-orphan-child.ttl" "Child action without parent"

# Test 5: Leaf action with children
cat > test-leaf-with-child.ttl << 'EOF'
@prefix actions: <https://vocab.example.org/actions/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

actions:parent a actions:ChildAction ;
    actions:depth 4 ;
    actions:priority 1 ;
    actions:state actions:NotStarted ;
    actions:context "@work" ;
    actions:childAction actions:leaf .

actions:leaf a actions:LeafAction ;
    actions:depth 5 ;
    actions:priority 1 ;
    actions:state actions:NotStarted ;
    actions:context "@work" ;
    actions:parentAction actions:parent ;
    actions:childAction actions:invalid_child .

actions:invalid_child a actions:ChildAction ;
    actions:depth 6 ;
    actions:priority 1 ;
    actions:state actions:NotStarted ;
    actions:context "@work" ;
    actions:parentAction actions:leaf .
EOF

validate_file "test-leaf-with-child.ttl" "Leaf action with children (should fail)"

# Test 6: Valid example (should pass)
cat > test-valid-simple.ttl << 'EOF'
@prefix actions: <https://vocab.example.org/actions/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

actions:root a actions:RootAction ;
    actions:depth 0 ;
    actions:priority 1 ;
    actions:project "Test Project" ;
    actions:state actions:NotStarted ;
    actions:context "@computer", "@office" .
EOF

validate_file "test-valid-simple.ttl" "Simple valid root action (should pass)"

echo ""
echo "=========================================="
echo "Individual test files created:"
echo "- test-root-depth.ttl"
echo "- test-missing-props.ttl"  
echo "- test-invalid-priority.ttl"
echo "- test-orphan-child.ttl"
echo "- test-leaf-with-child.ttl"
echo "- test-valid-simple.ttl"
echo ""
echo "Validation logs saved with .log extension"
echo "=========================================="

# Cleanup temporary test files (optional)
echo ""
read -p "Delete temporary test files? (y/N): " cleanup
if [[ $cleanup =~ ^[Yy]$ ]]; then
    rm test-*.ttl test-*.log 2>/dev/null
    echo "Temporary files cleaned up."
fi
