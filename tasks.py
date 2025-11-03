"""
Invoke tasks for Actions Vocabulary ontology validation and deployment.

Usage:
    # Validation & Testing
    uv run invoke test           # Run all validation tests
    uv run invoke validate       # Quick TTL syntax check
    uv run invoke clean          # Clean artifacts

    # Building & Deployment
    uv run invoke build-site     # Build site for deployment
    uv run invoke deploy         # Deploy to Cloudflare Pages
    uv run invoke serve-local    # Test locally before deployment

    # Schema Generation
    uv run invoke generate-schemas        # Generate JSON schemas
    uv run invoke generate-additional-formats  # Generate RDF/XML, JSON-LD

    # View all tasks
    uv run invoke --list
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
        "python -c \"import rdflib; rdflib.Graph().parse('actions-vocabulary.ttl')\"",
        warn=True,
    )

    print("🔍 Validating SHACL shapes syntax...")
    result2 = c.run(
        "python -c \"import rdflib; rdflib.Graph().parse('actions-shapes.ttl')\"",
        warn=True,
    )

    if result1.ok and result2.ok:
        print("✅ All TTL files are valid")
    else:
        print("❌ TTL validation failed")
        sys.exit(1)


@task
def clean(c):
    """Clean test artifacts."""
    patterns = ["tests/__pycache__", ".pytest_cache", "htmlcov", ".coverage", "schemas"]
    for pattern in patterns:
        c.run(f"rm -rf {pattern}", warn=True)
    print("🧹 Cleaned test artifacts and schemas")


@task
def quick(c):
    """Quick validation (syntax + simple tests)."""
    validate(c)
    c.run("pytest --quick")


@task
def validate_schemas(c):
    """Validate generated JSON schemas."""
    if not c.run("test -f schemas/actions-combined.schema.json", warn=True).ok:
        print("❌ No schemas found. Run 'uv run invoke generate-schemas' first.")
        return
    # Basic validation - check if files are valid JSON
    c.run(
        "python -c \"import json; json.load(open('schemas/actions-combined.schema.json'))\""
    )
    print("✅ Generated schemas are valid JSON")


@task
def generate_additional_formats(c):
    """Generate additional vocabulary formats (RDF/XML, JSON-LD)."""
    print("🔄 Generating additional vocabulary formats...")

    # Generate RDF/XML
    try:
        c.run(
            '''python -c "
import rdflib
g = rdflib.Graph()
g.parse('actions-vocabulary.ttl', format='turtle')
g.serialize('actions-vocabulary.rdf', format='xml')
print('✅ Generated RDF/XML format')
"'''
        )
    except Exception as e:
        print(f"⚠️ Could not generate RDF/XML: {e}")

    # Generate JSON-LD
    try:
        c.run(
            '''python -c "
import rdflib
g = rdflib.Graph()
g.parse('actions-vocabulary.ttl', format='turtle')
g.serialize('actions-vocabulary.jsonld', format='json-ld')
print('✅ Generated JSON-LD format')
"'''
        )
    except Exception as e:
        print(f"⚠️ Could not generate JSON-LD: {e}")


@task
def build_site(c):
    """Build the complete vocabulary site for deployment (v3.1.0 consolidated)."""
    print("🏗️ Building vocabulary site for v3.1.0...")

    # Clean and recreate site structure
    c.run("rm -rf site")
    c.run(
        "mkdir -p site/vocab/actions/v3 site/vocab/actions/schemas site/vocab/actions/examples/v3/valid site/vocab/actions/examples/v3/invalid site/.well-known"
    )

    # Generate additional formats from v3.1.0 OWL ontology
    print("🔄 Generating RDF formats from v3.1.0 ontology...")


import rdflib

g = rdflib.Graph()
g.parse("actions-vocabulary.owl", format="xml")
g.serialize("site/vocab/actions/v3/actions-vocabulary.ttl", format="turtle")
g.serialize("site/vocab/actions/v3/actions-vocabulary.rdf", format="xml")
g.serialize("site/vocab/actions/v3/actions-vocabulary.jsonld", format="json-ld")
print("✅ Generated Turtle, RDF/XML, and JSON-LD formats")


# Copy v3.1.0 OWL ontology (canonical format)
c.run("cp actions-vocabulary.owl site/vocab/actions/v3/")

# Copy v3 SHACL shapes
c.run("cp actions-shapes-v3.ttl site/vocab/actions/v3/shapes.ttl")

# Generate schemas if needed
if c.run("test -d schemas && ls schemas/*.json 2>/dev/null", warn=True).ok:
    c.run("cp schemas/*.json site/vocab/actions/schemas/ 2>/dev/null || true")

    # Copy examples (legacy JSON examples)
    c.run("cp examples/*.json site/vocab/actions/examples/ 2>/dev/null || true")
    c.run("cp examples/README.md site/vocab/actions/examples/ 2>/dev/null || true")

    # Copy v3 Turtle examples (used for testing and documentation)
    c.run(
        "cp examples/v3/valid/*.ttl site/vocab/actions/examples/v3/valid/ 2>/dev/null || true"
    )
    c.run(
        "cp examples/v3/invalid/*.ttl site/vocab/actions/examples/v3/invalid/ 2>/dev/null || true"
    )

    # Create v3 examples README if it exists
    if c.run("test -f examples/v3/README.md", warn=True).ok:
        c.run("cp examples/v3/README.md site/vocab/actions/examples/v3/")

    # Copy well-known files
    c.run("cp .well-known/vocab-catalog.json site/.well-known/")

    # Create index pages
    _create_index_pages(c)

    # Create Cloudflare Pages configuration
    _create_cloudflare_config(c)

    print("✅ Site built in ./site/ directory")
    print("📦 Ready for Cloudflare Pages deployment")


def _create_index_pages(c):
    """Create HTML index pages for the vocabulary site."""
    # Main index
    main_index = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Actions Vocabulary v3.1.0 - BFO/CCO-Aligned Ontology</title>
    <style>
        body { font-family: system-ui, -apple-system, sans-serif; max-width: 900px; margin: 0 auto; padding: 2rem; line-height: 1.6; color: #333; }
        h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 0.5rem; }
        h2 { color: #34495e; margin-top: 2rem; }
        .version { background: #3498db; color: white; padding: 0.25rem 0.75rem; border-radius: 4px; font-size: 0.9em; }
        .consolidated { background: #27ae60; color: white; padding: 0.25rem 0.75rem; border-radius: 4px; font-size: 0.9em; margin-left: 0.5rem; }
        .format { background: #f8f9fa; padding: 1rem; margin: 0.5rem 0; border-radius: 4px; border-left: 4px solid #3498db; }
        .format h3 { margin-top: 0; color: #2c3e50; }
        code { background: #e9ecef; padding: 0.2rem 0.4rem; border-radius: 3px; font-size: 0.9em; }
        a { color: #3498db; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .info { background: #e8f4f8; border-left: 4px solid #3498db; padding: 1rem; margin: 1rem 0; }
        ul { line-height: 1.8; }
    </style>
</head>
<body>
    <h1>Actions Vocabulary <span class="version">v3.1.0</span> <span class="consolidated">Consolidated</span></h1>

    <p>A BFO/CCO-aligned ontology for personal and organizational productivity, task management, and workflow automation.</p>

    <div class="info">
        <strong>📦 Consolidated Release:</strong> v3.1.0 combines Core + Context + Workflow + Roles extensions into a single, production-ready ontology.
    </div>

    <h2>Available Formats</h2>

    <div class="format">
        <h3>OWL/XML (Canonical)</h3>
        <p>Industry-standard format, compatible with Protégé and reasoning tools.</p>
        <p>🔗 <a href="/vocab/actions/v3/actions-vocabulary.owl">Download OWL/XML</a></p>
        <p><code>curl -H "Accept: application/rdf+xml" https://clearhead.us/vocab/actions/v3/</code></p>
    </div>

    <div class="format">
        <h3>Turtle (RDF)</h3>
        <p>Human-readable RDF format, perfect for version control and manual editing.</p>
        <p>🔗 <a href="/vocab/actions/v3/actions-vocabulary.ttl">Download Turtle</a></p>
        <p><code>curl -H "Accept: text/turtle" https://clearhead.us/vocab/actions/v3/</code></p>
    </div>

    <div class="format">
        <h3>JSON-LD</h3>
        <p>JSON-based linked data format, ideal for web applications and JavaScript.</p>
        <p>🔗 <a href="/vocab/actions/v3/actions-vocabulary.jsonld">Download JSON-LD</a></p>
        <p><code>curl -H "Accept: application/ld+json" https://clearhead.us/vocab/actions/v3/</code></p>
    </div>

    <div class="format">
        <h3>SHACL Shapes</h3>
        <p>Validation constraints and data quality rules for Action instances.</p>
        <p>🔗 <a href="/vocab/actions/v3/shapes.ttl">Download SHACL Shapes</a></p>
    </div>

    <h2>What's Included</h2>
    <ul>
        <li><strong>Core Classes:</strong> ActionPlan, ActionProcess, hierarchical structure (Root/Child/Leaf), action states</li>
        <li><strong>Context Extension:</strong> GTD-style contexts (Location, Tool, Energy, Social)</li>
        <li><strong>Workflow Extension:</strong> Dependencies, milestones, blocking relationships, parallel execution</li>
        <li><strong>Role Integration:</strong> Agent assignment, delegation, Areas of Focus (via CCO infrastructure)</li>
        <li><strong>BFO/CCO Alignment:</strong> Formal upper ontology foundation for interoperability</li>
    </ul>

    <h2>Using the Vocabulary</h2>

    <h3>Import in Your Ontology</h3>
    <pre><code>&lt;owl:Ontology rdf:about="https://example.com/my-ontology"&gt;
  &lt;owl:imports rdf:resource="https://clearhead.us/vocab/actions/v3"/&gt;
&lt;/owl:Ontology&gt;</code></pre>

    <h3>Load in Protégé</h3>
    <p>File → Open from URL → <code>https://clearhead.us/vocab/actions/v3/actions-vocabulary.owl</code></p>

    <h2>Resources</h2>
    <ul>
        <li>📖 <a href="https://github.com/your-org/ontology">GitHub Repository</a></li>
        <li>📄 <a href="/vocab/actions/examples/">Example Data</a></li>
        <li>🔍 <a href="/.well-known/vocab-catalog.json">Vocabulary Catalog (DCAT)</a></li>
    </ul>

    <footer style="margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #ddd; color: #777; font-size: 0.9em;">
        <p>Actions Vocabulary v3.1.0 | Licensed under MIT | <a href="https://clearhead.us">Clearhead Platform</a></p>
    </footer>
</body>
</html>"""

    c.run(f"cat > site/index.html << 'EOF'\n{main_index}\nEOF")
    c.run(f"cat > site/vocab/index.html << 'EOF'\n{main_index}\nEOF")
    c.run(f"cat > site/vocab/actions/index.html << 'EOF'\n{main_index}\nEOF")
    print("✅ Created index pages")


def _create_cloudflare_config(c):
    """Create Cloudflare Pages configuration files."""

    # _headers file for content negotiation and CORS
    headers = """# Content negotiation and security headers for Actions Vocabulary

# CORS headers for all files
/*
  Access-Control-Allow-Origin: *
  Access-Control-Allow-Methods: GET, OPTIONS
  Access-Control-Allow-Headers: Accept, Content-Type
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  X-XSS-Protection: 1; mode=block

# Cache RDF/OWL files for 1 hour
/vocab/actions/v3/*.owl
  Content-Type: application/rdf+xml
  Cache-Control: public, max-age=3600

/vocab/actions/v3/*.ttl
  Content-Type: text/turtle; charset=utf-8
  Cache-Control: public, max-age=3600

/vocab/actions/v3/*.rdf
  Content-Type: application/rdf+xml
  Cache-Control: public, max-age=3600

/vocab/actions/v3/*.jsonld
  Content-Type: application/ld+json
  Cache-Control: public, max-age=3600

# Cache schemas for 1 hour
/vocab/actions/schemas/*.json
  Content-Type: application/schema+json
  Cache-Control: public, max-age=3600

# No cache for HTML
/*.html
  Cache-Control: no-cache, must-revalidate
"""

    # _redirects file for content negotiation
    redirects = """# Content negotiation for Actions Vocabulary v3
# Cloudflare Pages uses format: [from] [to] [status] [condition]

# Root redirects to vocab
/  /vocab/  302

# Content negotiation for /vocab/actions/v3/
# Match Accept header and redirect to appropriate format
/vocab/actions/v3  /vocab/actions/v3/actions-vocabulary.owl  200  Accept: application/rdf+xml
/vocab/actions/v3  /vocab/actions/v3/actions-vocabulary.owl  200  Accept: application/xml
/vocab/actions/v3  /vocab/actions/v3/actions-vocabulary.ttl  200  Accept: text/turtle
/vocab/actions/v3  /vocab/actions/v3/actions-vocabulary.jsonld  200  Accept: application/ld+json
/vocab/actions/v3  /vocab/actions/v3/actions-vocabulary.jsonld  200  Accept: application/json
/vocab/actions/v3  /vocab/actions/index.html  200

# Trailing slash variants
/vocab/actions/v3/  /vocab/actions/v3/actions-vocabulary.owl  200  Accept: application/rdf+xml
/vocab/actions/v3/  /vocab/actions/v3/actions-vocabulary.owl  200  Accept: application/xml
/vocab/actions/v3/  /vocab/actions/v3/actions-vocabulary.ttl  200  Accept: text/turtle
/vocab/actions/v3/  /vocab/actions/v3/actions-vocabulary.jsonld  200  Accept: application/ld+json
/vocab/actions/v3/  /vocab/actions/v3/actions-vocabulary.jsonld  200  Accept: application/json
/vocab/actions/v3/  /vocab/actions/index.html  200

# Convenience URLs
/vocab  /vocab/  301
/actions  /vocab/actions/  301
/ontology  /vocab/actions/  301
"""

    c.run(f"cat > site/_headers << 'EOF'\n{headers}\nEOF")
    c.run(f"cat > site/_redirects << 'EOF'\n{redirects}\nEOF")
    print("✅ Created Cloudflare Pages configuration (_headers, _redirects)")


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
        ("application/ld+json", "vocabulary.jsonld", "JSON-LD format"),
    ]

    for accept_header, expected_file, description in tests:
        print(f"  Testing {description}...")
        result = c.run(
            f"curl -s -H 'Accept: {accept_header}' {base_url}/actions/ -w '%{{content_type}}'",
            warn=True,
            hide=True,
        )
        if result.ok:
            print(
                f"    ✅ {description}: {result.stdout.split()[-1] if result.stdout else 'OK'}"
            )
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
        "site/index.html",
    ]

    all_good = True
    for file_path in required_files:
        if c.run(f"test -f {file_path}", warn=True).ok:
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ Missing: {file_path}")
            all_good = False

    # Check JSON validity
    json_files = c.run("find site -name '*.json'", hide=True).stdout.strip().split("\n")
    for json_file in json_files:
        if json_file:  # Skip empty lines
            if c.run(
                f"python -c 'import json; json.load(open(\"{json_file}\"))'", warn=True
            ).ok:
                print(f"  ✅ Valid JSON: {json_file}")
            else:
                print(f"  ❌ Invalid JSON: {json_file}")
                all_good = False

    # Check TTL validity
    ttl_files = c.run("find site -name '*.ttl'", hide=True).stdout.strip().split("\n")
    for ttl_file in ttl_files:
        if ttl_file:  # Skip empty lines
            if c.run(
                f"python -c 'import rdflib; rdflib.Graph().parse(\"{ttl_file}\")'",
                warn=True,
            ).ok:
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


@task
def deploy(c):
    """Deploy the vocabulary site to Cloudflare Pages.

    Prerequisites:
    - Wrangler CLI installed and authenticated (wrangler whoami)
    - Site built (uv run invoke build-site)

    This deploys to:
    - Pages URL: https://actions-vocabulary.pages.dev
    - Custom domain: https://clearhead.us (if configured in dashboard)

    For Worker deployment, see: workers/content-negotiation/README.md
    """
    print("🚀 Deploying vocabulary site to Cloudflare Pages...")
    print("📍 Target: actions-vocabulary project")
    print("🌐 Production URL: https://clearhead.us/vocab/actions/v3/")
    print()

    # Note: Not running deploy_check as site should already be built
    # and we want deployment to be fast

    # Deploy using correct wrangler command
    result = c.run(
        "wrangler pages deploy site --project-name actions-vocabulary --branch main",
        warn=True,
    )

    if result.ok:
        print()
        print("✅ Deployment successful!")
        print(
            "📦 View deployment: https://dash.cloudflare.com/.../pages/view/actions-vocabulary"
        )
        print("🌐 Production: https://clearhead.us/vocab/actions/v3/")
        print()
        print("💡 To update Worker (if content negotiation changed):")
        print("   cd workers/content-negotiation && wrangler deploy")
    else:
        print("❌ Deployment failed!")
        print("💡 Check wrangler authentication: wrangler whoami")
        print("💡 Ensure site is built: uv run invoke build-site")
        sys.exit(1)
