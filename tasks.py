"""
Invoke tasks for Actions Vocabulary ontology validation and deployment.

Usage:
    # Validation & Testing
    uv run invoke test           # Run all validation tests
    uv run invoke validate       # Quick syntax check
    uv run invoke clean          # Clean artifacts

    # Building & Deployment
    uv run invoke build-site     # Build site for deployment
    uv run invoke deploy         # Deploy to Cloudflare Pages
    uv run invoke serve-local    # Test locally before deployment

    # View all tasks
    uv run invoke --list
"""

from invoke.tasks import task
import sys
import rdflib as rdf


@task
def test(c):
    """Run all SHACL validation tests """
    c.run("pytest")


@task
def validate(c):
    """Validate ontology and SHACL shapes syntax."""
    print("🔍 Validating ontology (OWL/XML)...")
    
    ontology = rdf.Graph().parse('v4/actions-vocabulary.owl', format='xml')
    shapes = rdf.Graph().parse('v4/actions-shapes-v4.ttl', format='turtle')


    if len(ontology) > 0 and len(shapes) > 0:
        print("✅ Ontology and SHACL shapes are valid")
    else:
        print("❌ Validation failed")
        sys.exit(1)


@task
def clean(c):
    """Clean test artifacts and build output."""
    patterns = ["tests/__pycache__", ".pytest_cache", "htmlcov", ".coverage", "site"]
    for pattern in patterns:
        c.run(f"rm -rf {pattern}", warn=True)
    print("🧹 Cleaned test artifacts and build output")


@task
def quick(c):
    """Quick validation (syntax + simple tests)."""
    validate(c)
    c.run("pytest --quick")


@task
def build_site(c):
    """Build the complete vocabulary site for deployment (v3 and v4)."""
    print("🏗️ Building vocabulary site for v3 and v4...")

    # Clean and recreate site structure
    c.run("rm -rf site")
    c.run(
        "mkdir -p site/vocab/actions/v3 site/vocab/actions/v4 site/vocab/actions/examples/v3/valid site/vocab/actions/examples/v3/invalid site/.well-known"
    )

    # Generate v3 formats
    print("🔄 Generating RDF formats from v3.1.0 ontology...")
    c.run(
        '''python -c "
import rdflib
g = rdflib.Graph()
g.parse('actions-vocabulary.owl', format='xml')
g.serialize('site/vocab/actions/v3/actions-vocabulary.ttl', format='turtle')
g.serialize('site/vocab/actions/v3/actions-vocabulary.rdf', format='xml')
g.serialize('site/vocab/actions/v3/actions-vocabulary.jsonld', format='json-ld')
print('✅ Generated v3 Turtle, RDF/XML, and JSON-LD formats')
"'''
    )

    # Copy v3.1.0 OWL ontology (canonical format)
    c.run("cp actions-vocabulary.owl site/vocab/actions/v3/")

    # Copy v3 SHACL shapes (from v3 directory)
    c.run("cp v3/actions-shapes-v3.ttl site/vocab/actions/v3/shapes.ttl")

    # Generate v4 formats
    print("🔄 Generating RDF formats from v4 ontology...")
    c.run(
        '''python -c "
import rdflib
g = rdflib.Graph()
g.parse('v4/actions-vocabulary.owl', format='xml')
g.serialize('site/vocab/actions/v4/actions-vocabulary.ttl', format='turtle')
g.serialize('site/vocab/actions/v4/actions-vocabulary.rdf', format='xml')
g.serialize('site/vocab/actions/v4/actions-vocabulary.jsonld', format='json-ld')
print('✅ Generated v4 Turtle, RDF/XML, and JSON-LD formats')
"'''
    )

    # Copy v4 OWL ontology (canonical format)
    c.run("cp v4/actions-vocabulary.owl site/vocab/actions/v4/")

    # Copy v4 SHACL shapes
    c.run("cp v4/actions-shapes-v4.ttl site/vocab/actions/v4/shapes.ttl")

    # Copy v4 JSON-LD context and JSON schema
    c.run("cp v4/actions.context.json site/vocab/actions/v4/")
    c.run("cp v4/actions.schema.json site/vocab/actions/v4/")

    # Copy v3 Turtle examples
    c.run(
        "cp examples/v3/valid/*.ttl site/vocab/actions/examples/v3/valid/ 2>/dev/null || true"
    )
    c.run(
        "cp examples/v3/invalid/*.ttl site/vocab/actions/examples/v3/invalid/ 2>/dev/null || true"
    )
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
    <title>Actions Vocabulary - Semantic Web Ontologies</title>
    <style>
        body { font-family: system-ui, -apple-system, sans-serif; max-width: 900px; margin: 0 auto; padding: 2rem; line-height: 1.6; color: #333; }
        h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 0.5rem; }
        h2 { color: #34495e; margin-top: 2rem; }
        .version { background: #3498db; color: white; padding: 0.25rem 0.75rem; border-radius: 4px; font-size: 0.9em; }
        .badge { display: inline-block; padding: 0.25rem 0.75rem; border-radius: 4px; font-size: 0.9em; margin-left: 0.5rem; }
        .v3 { background: #27ae60; }
        .v4 { background: #e67e22; }
        .format { background: #f8f9fa; padding: 1rem; margin: 0.5rem 0; border-radius: 4px; border-left: 4px solid #3498db; }
        .format h3 { margin-top: 0; color: #2c3e50; }
        code { background: #e9ecef; padding: 0.2rem 0.4rem; border-radius: 3px; font-size: 0.9em; }
        a { color: #3498db; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .info { background: #e8f4f8; border-left: 4px solid #3498db; padding: 1rem; margin: 1rem 0; }
        ul { line-height: 1.8; }
        .version-box { background: #f9f9f9; padding: 1.5rem; margin: 1rem 0; border-radius: 4px; border: 1px solid #ddd; }
    </style>
</head>
<body>
    <h1>Actions Vocabulary</h1>

    <p>BFO/CCO-aligned ontologies for personal and organizational productivity, task management, and workflow automation.</p>

    <div class="info">
        <strong>📦 Multiple Versions Available:</strong> Choose the version that fits your use case. See version comparisons below.
    </div>

    <h2>Available Versions</h2>

    <div class="version-box">
        <h3>Actions Vocabulary <span class="version v3">v3.1.0</span> <span class="badge v3">Stable</span></h3>
        <p>Full-featured ontology with Core + Context + Workflow + Roles extensions.</p>
        <p><strong>Best for:</strong> Complete productivity systems, complex workflows, GTD-style task management</p>
        <p><strong>URL:</strong> <a href="/vocab/actions/v3/">/vocab/actions/v3/</a></p>
    </div>

    <div class="version-box">
        <h3>Actions Vocabulary <span class="version v4">v4.0.0</span> <span class="badge v4">Minimal CCO Extension</span></h3>
        <p>Minimal extension to Common Core Ontologies. References CCO classes directly, adds only lifecycle phase tracking.</p>
        <p><strong>Best for:</strong> Interoperability with CCO ecosystem, semantic web applications, lightweight integrations</p>
        <p><strong>URL:</strong> <a href="/vocab/actions/v4/">/vocab/actions/v4/</a></p>
    </div>

    <h2>v3.1.0 Formats</h2>

    <div class="format">
        <h3>OWL/XML (Canonical)</h3>
        <p>Industry-standard format, compatible with Protégé and reasoning tools.</p>
        <p>🔗 <a href="/vocab/actions/v3/actions-vocabulary.owl">Download OWL/XML</a></p>
    </div>

    <div class="format">
        <h3>Turtle (RDF)</h3>
        <p>Human-readable RDF format, perfect for version control and manual editing.</p>
        <p>🔗 <a href="/vocab/actions/v3/actions-vocabulary.ttl">Download Turtle</a></p>
    </div>

    <div class="format">
        <h3>SHACL Shapes</h3>
        <p>Validation constraints and data quality rules for Action instances.</p>
        <p>🔗 <a href="/vocab/actions/v3/shapes.ttl">Download SHACL Shapes</a></p>
    </div>

    <h2>v4.0.0 Formats</h2>

    <div class="format">
        <h3>OWL/XML (Canonical)</h3>
        <p>Industry-standard format, compatible with Protégé and reasoning tools.</p>
        <p>🔗 <a href="/vocab/actions/v4/actions-vocabulary.owl">Download OWL/XML</a></p>
    </div>

    <div class="format">
        <h3>Turtle (RDF)</h3>
        <p>Human-readable RDF format, perfect for version control and manual editing.</p>
        <p>🔗 <a href="/vocab/actions/v4/actions-vocabulary.ttl">Download Turtle</a></p>
    </div>

    <div class="format">
        <h3>SHACL Shapes</h3>
        <p>Validation constraints and data quality rules for Action instances.</p>
        <p>🔗 <a href="/vocab/actions/v4/shapes.ttl">Download SHACL Shapes</a></p>
    </div>

    <div class="format">
        <h3>JSON-LD Context</h3>
        <p>Context map for ontology-out JSON exports.</p>
        <p>🔗 <a href="/vocab/actions/v4/actions.context.json">Download JSON-LD Context</a></p>
    </div>

    <div class="format">
        <h3>JSON Schema</h3>
        <p>Structural validation for ontology-out JSON exports.</p>
        <p>🔗 <a href="/vocab/actions/v4/actions.schema.json">Download JSON Schema</a></p>
    </div>

    <h2>Version Comparison</h2>

    <table style="border-collapse: collapse; width: 100%; margin: 1rem 0;">
        <thead>
            <tr style="background: #f8f9fa;">
                <th style="padding: 0.75rem; border: 1px solid #ddd; text-align: left;">Feature</th>
                <th style="padding: 0.75rem; border: 1px solid #ddd; text-align: left;">v3.1.0</th>
                <th style="padding: 0.75rem; border: 1px solid #ddd; text-align: left;">v4.0.0</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td style="padding: 0.75rem; border: 1px solid #ddd;">Core Classes</td>
                <td style="padding: 0.75rem; border: 1px solid #ddd;">ActionPlan ActionProcess</td>
                <td style="padding: 0.75rem; border: 1px solid #ddd;">CCO Plan, PlannedAct</td>
            </tr>
            <tr>
                <td style="padding: 0.75rem; border: 1px solid #ddd;">State Tracking</td>
                <td style="padding: 0.75rem; border: 1px solid #ddd;">ActionState class</td>
                <td style="padding: 0.75rem; border: 1px solid #ddd;">ActPhase quality</td>
            </tr>
            <tr>
                <td style="padding: 0.75rem; border: 1px solid #ddd;">Contexts</td>
                <td style="padding: 0.75rem; border: 1px solid #ddd;">Built-in (GTDTM)</td>
                <td style="padding: 0.75rem; border: 1px solid #ddd;">Application layer</td>
            </tr>
            <tr>
                <td style="padding: 0.75rem; border: 1px solid #ddd;">Dependencies</td>
                <td style="padding: 0.75rem; border: 1px solid #ddd;">Built-in</td>
                <td style="padding: 0.75rem; border: 1px solid #ddd;">Application layer</td>
            </tr>
            <tr>
                <td style="padding: 0.75rem; border: 1px solid #ddd;">CCO Integration</td>
                <td style="padding: 0.75rem; border: 1px solid #ddd;">Wraps CCO concepts</td>
                <td style="padding: 0.75rem; border: 1px solid #ddd;">References CCO directly</td>
            </tr>
            <tr>
                <td style="padding: 0.75rem; border: 1px solid #ddd;">Size</td>
                <td style="padding: 0.75rem; border: 1px solid #ddd;">~260 triples</td>
                <td style="padding: 0.75rem; border: 1px solid #ddd;">~50 triples</td>
            </tr>
        </tbody>
    </table>

    <h2>Resources</h2>
    <ul>
        <li>📖 <a href="https://github.com/your-org/ontology">GitHub Repository</a></li>
        <li>📄 <a href="/vocab/actions/examples/">Example Data</a></li>
        <li>🔍 <a href="/.well-known/vocab-catalog.json">Vocabulary Catalog (DCAT)</a></li>
    </ul>

    <footer style="margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #ddd; color: #777; font-size: 0.9em;">
        <p>Actions Vocabulary | Licensed under MIT | <a href="https://clearhead.us">Clearhead Platform</a></p>
    </footer>
</body>
</html>"""

    c.run(f"cat > site/index.html << 'EOF'\n{main_index}\nEOF")
    c.run(f"cat > site/vocab/index.html << 'EOF'\n{main_index}\nEOF")

    # v3-specific index
    v3_index = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Actions Vocabulary v3.1.0 - BFO/CCO-Aligned Ontology</title>
    <style>
        body { font-family: system-ui, -apple-system, sans-serif; max-width: 900px; margin: 0 auto; padding: 2rem; line-height: 1.6; color: #333; }
        h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 0.5rem; }
        h2 { color: #34495e; margin-top: 2rem; }
        code { background: #e9ecef; padding: 0.2rem 0.4rem; border-radius: 3px; font-size: 0.9em; }
        a { color: #3498db; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .badge { background: #27ae60; color: white; padding: 0.25rem 0.75rem; border-radius: 4px; font-size: 0.9em; }
    </style>
</head>
<body>
    <h1>Actions Vocabulary <span class="badge">v3.1.0</span></h1>

    <p>A BFO/CCO-aligned ontology for personal and organizational productivity, task management, and workflow automation.</p>

    <h2>Available Formats</h2>

    <ul>
        <li>🔗 <a href="actions-vocabulary.owl">OWL/XML (Canonical)</a> - Compatible with Protégé</li>
        <li>🔗 <a href="actions-vocabulary.ttl">Turtle (RDF)</a> - Human-readable, version control friendly</li>
        <li>🔗 <a href="actions-vocabulary.jsonld">JSON-LD</a> - Web applications, JavaScript</li>
        <li>🔗 <a href="shapes.ttl">SHACL Shapes</a> - Validation constraints</li>
        <li>🔗 <a href="actions.context.json">JSON-LD Context</a></li>
        <li>🔗 <a href="actions.schema.json">JSON Schema</a></li>
    </ul>

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

    <p><a href="/">← Back to all versions</a></p>
</body>
</html>"""
    c.run(f"cat > site/vocab/actions/v3/index.html << 'EOF'\n{v3_index}\nEOF")

    # v4-specific index
    v4_index = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Actions Vocabulary v4.1.0 - CCO Extension for Intention Information Entities</title>
    <style>
        body { font-family: system-ui, -apple-system, sans-serif; max-width: 900px; margin: 0 auto; padding: 2rem; line-height: 1.6; color: #333; }
        h1 { color: #2c3e50; border-bottom: 3px solid #e67e22; padding-bottom: 0.5rem; }
        h2 { color: #34495e; margin-top: 2rem; }
        code { background: #e9ecef; padding: 0.2rem 0.4rem; border-radius: 3px; font-size: 0.9em; }
        a { color: #3498db; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .badge { background: #e67e22; color: white; padding: 0.25rem 0.75rem; border-radius: 4px; font-size: 0.9em; }
    </style>
</head>
<body>
    <h1>Actions Vocabulary <span class="badge">v4.1.0</span></h1>

    <p>A CCO Extension for Intention Information Entities — a disciplined extension to CCO for modeling intentional planning and execution.</p>

    <p><strong>Philosophy:</strong> Reuse CCO directly. Only add what CCO provably lacks — Charter (scope declarations) and inServiceOf (teleological relation).</p>

    <h2>Available Formats</h2>

    <ul>
        <li>🔗 <a href="actions-vocabulary.owl">OWL/XML (Canonical)</a> - Compatible with Protégé</li>
        <li>🔗 <a href="actions-vocabulary.ttl">Turtle (RDF)</a> - Human-readable, version control friendly</li>
        <li>🔗 <a href="actions-vocabulary.jsonld">JSON-LD</a> - Web applications, JavaScript</li>
        <li>🔗 <a href="shapes.ttl">SHACL Shapes</a> - Validation constraints</li>
    </ul>

    <h2>Core Concepts</h2>

    <p>Three Directive ICE siblings (Charter is new, Plan and Objective are CCO):</p>
    <ul>
        <li><strong>Charter (actions:Charter):</strong> Scope of directed concern</li>
        <li><strong>Plan (CCO ont00000974):</strong> Action definitions / task templates</li>
        <li><strong>Planned Act (CCO ont00000228):</strong> Action instances / executions</li>
        <li><strong>Objective (CCO ont00000476):</strong> Projects / desired outcomes</li>
    </ul>

    <h2>Genuine Extensions</h2>

    <ul>
        <li><strong>Charter:</strong> Directive ICE declaring scope of directed concern (CCO lacks this)</li>
        <li><strong>inServiceOf:</strong> Teleological relation linking Directive ICEs to Objectives (CCO lacks this)</li>
    </ul>

    <h2>Key Properties</h2>

    <ul>
        <li><strong>inServiceOf (custom):</strong> Directive ICE → Objective teleological linkage</li>
        <li><strong>is_measured_by_nominal (CCO):</strong> Planned Act → Event Status</li>
        <li><strong>is_successor_of (CCO):</strong> Plan dependency ordering</li>
        <li><strong>prescribes (CCO):</strong> Plan → Planned Act</li>
        <li><strong>part_of (BFO):</strong> Plan/Charter hierarchy</li>
    </ul>

    <h2>Using the Vocabulary</h2>

    <h3>Import in Your Ontology</h3>
    <pre><code>&lt;owl:Ontology rdf:about="https://example.com/my-ontology"&gt;
  &lt;owl:imports rdf:resource="https://clearhead.us/vocab/actions/v4"/&gt;
&lt;/owl:Ontology&gt;</code></pre>

    <h3>Load in Protégé</h3>
    <p>File → Open from URL → <code>https://clearhead.us/vocab/actions/v4/actions-vocabulary.owl</code></p>

    <h2>Design Rationale</h2>

    <p>For full design documentation, see <a href="/">V4_DESIGN.md</a> in the repository.</p>

    <p><a href="/">← Back to all versions</a></p>
</body>
</html>"""
    c.run(f"cat > site/vocab/actions/v4/index.html << 'EOF'\n{v4_index}\nEOF")
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

/vocab/actions/v4/*.owl
  Content-Type: application/rdf+xml
  Cache-Control: public, max-age=3600

/vocab/actions/v3/*.ttl
  Content-Type: text/turtle; charset=utf-8
  Cache-Control: public, max-age=3600

/vocab/actions/v4/*.ttl
  Content-Type: text/turtle; charset=utf-8
  Cache-Control: public, max-age=3600

/vocab/actions/v3/*.rdf
  Content-Type: application/rdf+xml
  Cache-Control: public, max-age=3600

/vocab/actions/v4/*.rdf
  Content-Type: application/rdf+xml
  Cache-Control: public, max-age=3600

/vocab/actions/v3/*.jsonld
  Content-Type: application/ld+json
  Cache-Control: public, max-age=3600

/vocab/actions/v4/*.jsonld
  Content-Type: application/ld+json
  Cache-Control: public, max-age=3600

 /vocab/actions/v4/actions.context.json
  Content-Type: application/ld+json
  Cache-Control: public, max-age=3600

 /vocab/actions/v4/actions.schema.json
  Content-Type: application/schema+json
  Cache-Control: public, max-age=3600

# No cache for HTML
/*.html
  Cache-Control: no-cache, must-revalidate
 """

    # _redirects file for content negotiation
    redirects = """# Content negotiation for Actions Vocabulary
# Cloudflare Pages uses format: [from] [to] [status] [condition]

# Root redirects to vocab
/  /vocab/  302

# Content negotiation for /vocab/actions/v3/
/vocab/actions/v3  /vocab/actions/v3/actions-vocabulary.owl  200  Accept: application/rdf+xml
/vocab/actions/v3  /vocab/actions/v3/actions-vocabulary.owl  200  Accept: application/xml
/vocab/actions/v3  /vocab/actions/v3/actions-vocabulary.ttl  200  Accept: text/turtle
/vocab/actions/v3  /vocab/actions/v3/actions-vocabulary.jsonld  200  Accept: application/ld+json
/vocab/actions/v3  /vocab/actions/v3/actions-vocabulary.jsonld  200  Accept: application/json
/vocab/actions/v3  /vocab/actions/index.html  200

# Content negotiation for /vocab/actions/v4/
/vocab/actions/v4  /vocab/actions/v4/actions-vocabulary.owl  200  Accept: application/rdf+xml
/vocab/actions/v4  /vocab/actions/v4/actions-vocabulary.owl  200  Accept: application/xml
/vocab/actions/v4  /vocab/actions/v4/actions-vocabulary.ttl  200  Accept: text/turtle
/vocab/actions/v4  /vocab/actions/v4/actions-vocabulary.jsonld  200  Accept: application/ld+json
/vocab/actions/v4  /vocab/actions/v4/actions-vocabulary.jsonld  200  Accept: application/json
/vocab/actions/v4  /vocab/actions/index.html  200

# Trailing slash variants for v3
/vocab/actions/v3/  /vocab/actions/v3/actions-vocabulary.owl  200  Accept: application/rdf+xml
/vocab/actions/v3/  /vocab/actions/v3/actions-vocabulary.owl  200  Accept: application/xml
/vocab/actions/v3/  /vocab/actions/v3/actions-vocabulary.ttl  200  Accept: text/turtle
/vocab/actions/v3/  /vocab/actions/v3/actions-vocabulary.jsonld  200  Accept: application/ld+json
/vocab/actions/v3/  /vocab/actions/v3/actions-vocabulary.jsonld  200  Accept: application/json
/vocab/actions/v3/  /vocab/actions/v3/index.html  200

# Trailing slash variants for v4
/vocab/actions/v4/  /vocab/actions/v4/actions-vocabulary.owl  200  Accept: application/rdf+xml
/vocab/actions/v4/  /vocab/actions/v4/actions-vocabulary.owl  200  Accept: application/xml
/vocab/actions/v4/  /vocab/actions/v4/actions-vocabulary.ttl  200  Accept: text/turtle
/vocab/actions/v4/  /vocab/actions/v4/actions-vocabulary.jsonld  200  Accept: application/ld+json
/vocab/actions/v4/  /vocab/actions/v4/actions-vocabulary.jsonld  200  Accept: application/json
/vocab/actions/v4/  /vocab/actions/v4/index.html  200

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
        ("text/turtle", "actions-vocabulary.ttl", "Turtle format"),
        ("application/rdf+xml", "actions-vocabulary.owl", "OWL/XML format"),
        ("application/ld+json", "actions-vocabulary.jsonld", "JSON-LD format"),
        ("text/html", "index.html", "HTML documentation"),
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
        "site/vocab/actions/v3/actions-vocabulary.owl",
        "site/vocab/actions/v3/actions-vocabulary.ttl",
        "site/vocab/actions/v3/shapes.ttl",
        "site/vocab/actions/v4/actions-vocabulary.owl",
        "site/vocab/actions/v4/actions-vocabulary.ttl",
        "site/vocab/actions/v4/shapes.ttl",
        "site/vocab/actions/v4/actions.context.json",
        "site/vocab/actions/v4/actions.schema.json",
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

    # Check Turtle/OWL validity
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
    - Custom domain: https://clearhead.us/vocab/actions/ (if configured in dashboard)
    - Includes both v3 and v4 ontologies

    For Worker deployment, see: workers/content-negotiation/README.md
    """
    print("🚀 Deploying vocabulary site to Cloudflare Pages...")
    print("📍 Target: actions-vocabulary project")
    print("🌐 Production URLs:")
    print("   - v3: https://clearhead.us/vocab/actions/v3/")
    print("   - v4: https://clearhead.us/vocab/actions/v4/")
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
        print("🌐 Production URLs:")
        print("   - v3 (Full-featured): https://clearhead.us/vocab/actions/v3/")
        print("   - v4 (Minimal CCO): https://clearhead.us/vocab/actions/v4/")
        print()
        print("💡 To update Worker (if content negotiation changed):")
        print("   cd workers/content-negotiation && wrangler deploy")
    else:
        print("❌ Deployment failed!")
        print("💡 Check wrangler authentication: wrangler whoami")
        print("💡 Ensure site is built: uv run invoke build-site")
        sys.exit(1)
