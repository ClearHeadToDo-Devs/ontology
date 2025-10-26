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
        ".coverage",
        "schemas"
    ]
    for pattern in patterns:
        c.run(f"rm -rf {pattern}", warn=True)
    print("🧹 Cleaned test artifacts and schemas")


@task
def quick(c):
    """Quick validation (syntax + simple tests)."""
    validate(c)
    c.run("pytest --quick")


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


@task
def generate_additional_formats(c):
    """Generate additional vocabulary formats (RDF/XML, JSON-LD)."""
    print("🔄 Generating additional vocabulary formats...")
    
    # Generate RDF/XML
    try:
        c.run('''python -c "
import rdflib
g = rdflib.Graph()
g.parse('actions-vocabulary.ttl', format='turtle')
g.serialize('actions-vocabulary.rdf', format='xml')
print('✅ Generated RDF/XML format')
"''')
    except Exception as e:
        print(f"⚠️ Could not generate RDF/XML: {e}")
    
    # Generate JSON-LD
    try:
        c.run('''python -c "
import rdflib
g = rdflib.Graph()
g.parse('actions-vocabulary.ttl', format='turtle')
g.serialize('actions-vocabulary.jsonld', format='json-ld')
print('✅ Generated JSON-LD format')
"''')
    except Exception as e:
        print(f"⚠️ Could not generate JSON-LD: {e}")


@task
def build_site(c):
    """Build the complete vocabulary site for deployment."""
    print("🏗️ Building vocabulary site...")
    
    # Ensure schemas are generated
    generate_schemas(c)
    
    # Generate additional formats
    generate_additional_formats(c)
    
    # Create site structure
    c.run("mkdir -p site/actions/schemas site/actions/examples site/.well-known")
    
    # Copy vocabulary files
    c.run("cp actions-vocabulary.ttl site/actions/vocabulary.ttl")
    c.run("cp actions-shapes.ttl site/actions/shapes.ttl")
    c.run("cp actions-vocabulary.rdf site/actions/vocabulary.rdf || true")
    c.run("cp actions-vocabulary.jsonld site/actions/vocabulary.jsonld || true")
    
    # Copy schemas
    c.run("cp schemas/*.json site/actions/schemas/")
    
    # Copy examples
    c.run("cp -r examples/* site/actions/examples/")
    
    # Copy site files
    c.run("cp -r docs/vocab-site/* site/")
    
    # Copy well-known files
    c.run("cp -r .well-known/* site/.well-known/")
    
    print("✅ Site built in ./site/ directory")


@task
def serve_local(c, port=8000):
    """Serve the vocabulary site locally for testing."""
    print(f"🌐 Starting local server on port {port}...")
    print(f"📍 Visit: http://localhost:{port}")
    print("🔍 Test content negotiation with curl:")
    print(f"   curl -H 'Accept: text/turtle' http://localhost:{port}/actions/")
    print(f"   curl -H 'Accept: application/json' http://localhost:{port}/actions/")
    print("\n⏹️ Press Ctrl+C to stop")
    
    try:
        c.run(f"python -m http.server {port} --directory site")
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")


@task
def test_content_negotiation(c):
    """Test content negotiation locally (requires site to be running)."""
    print("🧪 Testing content negotiation...")
    base_url = "http://localhost:8000"
    
    tests = [
        ("text/turtle", "vocabulary.ttl", "TTL format"),
        ("application/json", "actions-combined.schema.json", "JSON Schema"),
        ("text/html", "index.html", "HTML documentation"),
        ("application/rdf+xml", "vocabulary.rdf", "RDF/XML format"),
        ("application/ld+json", "vocabulary.jsonld", "JSON-LD format")
    ]
    
    for accept_header, expected_file, description in tests:
        print(f"  Testing {description}...")
        result = c.run(
            f"curl -s -H 'Accept: {accept_header}' {base_url}/actions/ -w '%{{content_type}}'",
            warn=True,
            hide=True
        )
        if result.ok:
            print(f"    ✅ {description}: {result.stdout.split()[-1] if result.stdout else 'OK'}")
        else:
            print(f"    ❌ {description}: Failed")


@task
def deploy_check(c):
    """Validate deployment readiness."""
    print("🔍 Checking deployment readiness...")
    
    required_files = [
        "site/actions/vocabulary.ttl",
        "site/actions/shapes.ttl", 
        "site/actions/schemas/actions-combined.schema.json",
        "site/.well-known/vocab-catalog.json",
        "site/index.html"
    ]
    
    all_good = True
    for file_path in required_files:
        if c.run(f"test -f {file_path}", warn=True).ok:
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ Missing: {file_path}")
            all_good = False
    
    # Check JSON validity
    json_files = c.run("find site -name '*.json'", hide=True).stdout.strip().split('\n')
    for json_file in json_files:
        if json_file:  # Skip empty lines
            if c.run(f"python -c 'import json; json.load(open(\"{json_file}\"))'", warn=True).ok:
                print(f"  ✅ Valid JSON: {json_file}")
            else:
                print(f"  ❌ Invalid JSON: {json_file}")
                all_good = False
    
    # Check TTL validity
    ttl_files = c.run("find site -name '*.ttl'", hide=True).stdout.strip().split('\n')
    for ttl_file in ttl_files:
        if ttl_file:  # Skip empty lines
            if c.run(f"python -c 'import rdflib; rdflib.Graph().parse(\"{ttl_file}\")'", warn=True).ok:
                print(f"  ✅ Valid TTL: {ttl_file}")
            else:
                print(f"  ❌ Invalid TTL: {ttl_file}")
                all_good = False
    
    if all_good:
        print("\n🎉 Deployment ready!")
        return True
    else:
        print("\n❌ Deployment not ready - fix issues above")
        sys.exit(1)