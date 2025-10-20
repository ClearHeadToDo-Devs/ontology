#!/usr/bin/env python3
"""
Test JSON Schema validation with example data.

This script demonstrates how to use the generated JSON schemas
to validate action data in your applications.
"""

import json
import sys
from pathlib import Path

try:
    from jsonschema import validate, ValidationError
except ImportError:
    print("❌ jsonschema not installed. Run: pip install jsonschema")
    sys.exit(1)

def test_validation():
    """Test validation of example data against generated schemas."""
    
    examples_dir = Path(__file__).parent
    schemas_dir = examples_dir.parent / "schemas"
    
    # Test cases: (schema_file, data_file, should_be_valid)
    test_cases = [
        ("action.schema.json", "valid-action.json", True),
        ("rootaction.schema.json", "valid-rootaction.json", True), 
        ("childaction.schema.json", "valid-childaction.json", True),
    ]
    
    print("🧪 Testing JSON Schema validation...")
    print("=" * 40)
    
    total_tests = 0
    passed_tests = 0
    
    for schema_file, data_file, should_be_valid in test_cases:
        total_tests += 1
        
        try:
            # Load schema
            with open(schemas_dir / schema_file) as f:
                schema = json.load(f)
                
            # Load test data
            with open(examples_dir / data_file) as f:
                data = json.load(f)
                
            # Validate
            validate(instance=data, schema=schema)
            
            if should_be_valid:
                print(f"✅ {data_file} validates against {schema_file}")
                passed_tests += 1
            else:
                print(f"❌ {data_file} should have failed validation against {schema_file}")
                
        except ValidationError as e:
            if not should_be_valid:
                print(f"✅ {data_file} correctly failed validation: {e.message}")
                passed_tests += 1
            else:
                print(f"❌ {data_file} failed validation unexpectedly: {e.message}")
                
        except FileNotFoundError as e:
            print(f"⚠️  Skipping test - file not found: {e}")
            continue
            
        except Exception as e:
            print(f"❌ Unexpected error testing {data_file}: {e}")
    
    # Test some specific validation scenarios
    print(f"\n🔍 Testing specific constraints...")
    
    # Test invalid priority
    try:
        schema_path = schemas_dir / "action.schema.json"
        with open(schema_path) as f:
            action_schema = json.load(f)
            
        invalid_data = {
            "uuid": "01936194-d5b0-7890-8000-123456789abc",
            "name": "Test action",
            "priority": 5,  # Invalid - should be 1-4
            "state": "active"
        }
        
        validate(instance=invalid_data, schema=action_schema)
        print("❌ Should have failed: priority > 4")
        
    except ValidationError as e:
        print("✅ Correctly rejected invalid priority (> 4)")
        passed_tests += 1
        total_tests += 1
    
    # Test missing required field
    try:
        missing_data = {
            "uuid": "01936194-d5b0-7890-8000-123456789abc",
            "description": "Missing required fields"
            # Missing name, priority, state
        }
        
        validate(instance=missing_data, schema=action_schema)
        print("❌ Should have failed: missing required fields")
        
    except ValidationError as e:
        print("✅ Correctly rejected data missing required fields")
        passed_tests += 1
        total_tests += 1
    
    # Summary
    print(f"\n📊 VALIDATION RESULTS:")
    print(f"Tests passed: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("🎉 All validation tests passed!")
        return True
    else:
        print("❌ Some validation tests failed")
        return False

def show_schema_info():
    """Show information about available schemas."""
    schemas_dir = Path(__file__).parent.parent / "schemas"
    
    if not schemas_dir.exists():
        print("❌ Schemas directory not found. Run 'uv run invoke generate-schemas' first.")
        return
        
    print("\n📋 AVAILABLE SCHEMAS:")
    print("=" * 30)
    
    schema_files = list(schemas_dir.glob("*.schema.json"))
    
    for schema_file in sorted(schema_files):
        try:
            with open(schema_file) as f:
                schema = json.load(f)
                
            title = schema.get('title', schema_file.stem)
            description = schema.get('description', 'No description')
            
            # Count properties
            prop_count = 0
            if 'properties' in schema:
                prop_count = len(schema['properties'])
            elif 'allOf' in schema:
                for item in schema['allOf']:
                    if isinstance(item, dict) and 'properties' in item:
                        prop_count += len(item['properties'])
                        
            required = schema.get('required', [])
            
            print(f"📄 {schema_file.name}")
            print(f"   Title: {title}")
            print(f"   Properties: {prop_count}")
            print(f"   Required: {len(required)} ({', '.join(required[:3])}{'...' if len(required) > 3 else ''})")
            print(f"   Description: {description[:80]}{'...' if len(description) > 80 else ''}")
            print()
            
        except Exception as e:
            print(f"❌ Error reading {schema_file.name}: {e}")

if __name__ == "__main__":
    show_schema_info()
    
    if test_validation():
        print("\n🚀 Ready to use schemas for validation!")
        print("See examples/README.md for integration examples")
    else:
        sys.exit(1)