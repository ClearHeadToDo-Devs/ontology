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
def test(c):
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