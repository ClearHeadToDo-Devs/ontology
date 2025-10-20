"""
Invoke tasks for Actions Vocabulary ontology validation.

Usage:
    uv run invoke test           # Run all validation tests
    uv run invoke validate       # Quick TTL syntax check  
    uv run invoke clean          # Clean artifacts
    uv run invoke --list         # Show all tasks
"""

from invoke import task
import sys


@task
def generate_schemas(c):
    """Generate JSON schemas from OWL ontology and SHACL shapes."""
    c.run("mkdir -p schemas")
    c.run("uv run python scripts/generate_json_schema.py")


@task
def validate_schemas(c):
    """Validate generated JSON schemas."""
    if not c.run("test -f schemas/actions-combined.schema.json", warn=True).ok:
        print("❌ No schemas found. Run 'uv run invoke generate-schemas' first.")
        return
    # Basic validation - check if files are valid JSON
    c.run("python -c \"import json; json.load(open('schemas/actions-combined.schema.json'))\"")
    print("✅ Generated schemas are valid JSON")
@task
def test(c):
@task
def test_examples(c):
    """Test JSON Schema validation with example data."""
    c.run("uv run python examples/test_validation.py")


@task
def full_pipeline(c):
    """Run complete pipeline: validate ontology -> generate schemas -> test examples."""
    print("🚀 Running full JSON Schema generation pipeline...")
    validate(c)
    generate_schemas(c)
    test_examples(c)
    print("🎉 Full pipeline completed successfully!")
    """Run all SHACL validation tests."""
    c.run("pytest")


@task  
def validate(c):
    """Validate TTL file syntax."""
    print("🔍 Validating ontology syntax...")
    result1 = c.run(
        'python -c "import rdflib; rdflib.Graph().parse(\'actions-vocabulary.ttl\')"',
        warn=True
    )
    
    print("🔍 Validating SHACL shapes syntax...")
    result2 = c.run(
        'python -c "import rdflib; rdflib.Graph().parse(\'actions-shapes.ttl\')"', 
        warn=True
    )
    
    if result1.ok and result2.ok:
        print("✅ All TTL files are valid")
    else:
        print("❌ TTL validation failed")
        sys.exit(1)


@task
def clean(c):
    """Clean test artifacts."""
    patterns = [
        "tests/__pycache__",
        ".pytest_cache", 
        "htmlcov",
        ".coverage"
    ]
    for pattern in patterns:
        c.run(f"rm -rf {pattern}", warn=True)
    print("🧹 Cleaned test artifacts")


@task
def quick(c):
    """Quick validation (syntax + simple tests)."""
    validate(c)
    c.run("pytest --quick")
