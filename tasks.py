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
from htpy import (
    a, body, code, div, footer, h1, h2, h3, head, html, li, meta, p, pre, style, title, ul,
)
from markupsafe import Markup


# ---------------------------------------------------------------------------
# Site data
# ---------------------------------------------------------------------------

FORMATS = [
    {
        "label": "OWL/XML (Canonical)",
        "href": "actions-vocabulary.owl",
        "desc": "Industry-standard format, compatible with Protege and reasoning tools.",
    },
    {
        "label": "Turtle (RDF)",
        "href": "actions-vocabulary.ttl",
        "desc": "Human-readable RDF format, perfect for version control and manual editing.",
    },
    {
        "label": "JSON-LD",
        "href": "actions-vocabulary.jsonld",
        "desc": "Web applications, JavaScript, REST APIs.",
    },
    {
        "label": "RDF/XML",
        "href": "actions-vocabulary.rdf",
        "desc": "Legacy RDF tools and broad compatibility.",
    },
    {
        "label": "SHACL Shapes",
        "href": "shapes.ttl",
        "desc": "Validation constraints and data quality rules for Action instances.",
    },
    {
        "label": "JSON-LD Context",
        "href": "actions.context.json",
        "desc": "Context map for ontology-out JSON exports.",
    },
    {
        "label": "JSON Schema",
        "href": "actions.schema.json",
        "desc": "Structural validation for ontology-out JSON exports.",
    },
]

CSS = """
body {
    font-family: system-ui, -apple-system, sans-serif;
    max-width: 900px; margin: 0 auto; padding: 2rem;
    line-height: 1.6; color: #333;
}
h1 { color: #2c3e50; border-bottom: 3px solid #e67e22; padding-bottom: 0.5rem; }
h2 { color: #34495e; margin-top: 2rem; }
code { background: #e9ecef; padding: 0.2rem 0.4rem; border-radius: 3px; font-size: 0.9em; }
pre { background: #f8f9fa; padding: 1rem; border-radius: 4px; overflow-x: auto; }
a { color: #3498db; text-decoration: none; }
a:hover { text-decoration: underline; }
.badge { background: #e67e22; color: white; padding: 0.25rem 0.75rem; border-radius: 4px; font-size: 0.9em; }
.format { background: #f8f9fa; padding: 1rem; margin: 0.5rem 0; border-radius: 4px; border-left: 4px solid #e67e22; }
.format h3 { margin-top: 0; color: #2c3e50; }
.info { background: #e8f4f8; border-left: 4px solid #3498db; padding: 1rem; margin: 1rem 0; }
footer { margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #ddd; color: #777; font-size: 0.9em; }
ul { line-height: 1.8; }
"""


def _page(page_title: str, *children) -> str:
    """Wrap content in a full HTML document with shared styling."""
    doc = html(lang="en")[
        head[
            meta(charset="UTF-8"),
            meta(name="viewport", content="width=device-width, initial-scale=1.0"),
            title[page_title],
            style[CSS],
        ],
        body[children],
    ]
    return str(doc)


def _landing_page() -> str:
    return _page(
        "Actions Vocabulary — CCO Extension for Intentional Planning",
        h1["Actions Vocabulary"],
        p[
            "A disciplined extension to ",
            a(href="https://github.com/CommonCoreOntology/CommonCoreOntologies")["Common Core Ontologies"],
            " for modeling intentional planning and execution.",
        ],
        div(".info")[
            p[
                Markup("<strong>Philosophy:</strong> "),
                "Reuse CCO directly. Only add what CCO provably lacks — ",
                "Charter (scope declarations) and inServiceOf (teleological relation).",
            ],
        ],
        h2["Available Formats"],
        [
            div(".format")[
                h3[fmt["label"]],
                p[fmt["desc"]],
                p[a(href=fmt["href"])[f"Download {fmt['label']}"]],
            ]
            for fmt in FORMATS
        ],
        h2["Core Concepts"],
        p["Three Directive ICE siblings (Charter is new, Plan and Objective are CCO):"],
        ul[
            li[Markup("<strong>Charter</strong> — Scope of directed concern")],
            li[Markup("<strong>Plan</strong> (CCO) — Action definitions / task templates")],
            li[Markup("<strong>Planned Act</strong> (CCO) — Action instances / executions")],
            li[Markup("<strong>Objective</strong> (CCO) — Projects / desired outcomes")],
        ],
        h2["Genuine Extensions"],
        ul[
            li[Markup("<strong>Charter:</strong> Directive ICE declaring scope of directed concern (CCO lacks this)")],
            li[Markup("<strong>inServiceOf:</strong> Teleological relation linking Directive ICEs to Objectives (CCO lacks this)")],
        ],
        h2["Using the Vocabulary"],
        h3["Import in Your Ontology"],
        pre[code[Markup(
            '&lt;owl:Ontology rdf:about="https://example.com/my-ontology"&gt;\n'
            '  &lt;owl:imports rdf:resource="https://clearhead.us/vocab/actions"/&gt;\n'
            '&lt;/owl:Ontology&gt;'
        )]],
        h3["Load in Protege"],
        p[
            "File ", Markup("&rarr;"), " Open from URL ", Markup("&rarr;"), " ",
            code["https://clearhead.us/vocab/actions/actions-vocabulary.owl"],
        ],
        h2["Resources"],
        ul[
            li[a(href="https://github.com/your-org/ontology")["GitHub Repository"]],
            li[a(href="/.well-known/vocab-catalog.json")["Vocabulary Catalog (DCAT)"]],
        ],
        footer[
            p[
                "Actions Vocabulary | Licensed under MIT | ",
                a(href="https://clearhead.us")["Clearhead Platform"],
            ],
        ],
    )


# ---------------------------------------------------------------------------
# Cloudflare config (plain text, not HTML)
# ---------------------------------------------------------------------------

CLOUDFLARE_HEADERS = """\
# Content negotiation and security headers for Actions Vocabulary

# CORS headers for all files
/*
  Access-Control-Allow-Origin: *
  Access-Control-Allow-Methods: GET, OPTIONS
  Access-Control-Allow-Headers: Accept, Content-Type
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  X-XSS-Protection: 1; mode=block

/vocab/actions/*.owl
  Content-Type: application/rdf+xml
  Cache-Control: public, max-age=3600

/vocab/actions/*.ttl
  Content-Type: text/turtle; charset=utf-8
  Cache-Control: public, max-age=3600

/vocab/actions/*.rdf
  Content-Type: application/rdf+xml
  Cache-Control: public, max-age=3600

/vocab/actions/*.jsonld
  Content-Type: application/ld+json
  Cache-Control: public, max-age=3600

/vocab/actions/actions.context.json
  Content-Type: application/ld+json
  Cache-Control: public, max-age=3600

/vocab/actions/actions.schema.json
  Content-Type: application/schema+json
  Cache-Control: public, max-age=3600

/*.html
  Cache-Control: no-cache, must-revalidate
"""

CLOUDFLARE_REDIRECTS = """\
# Content negotiation for Actions Vocabulary

# Root redirects to vocab
/  /vocab/actions/  302

# Content negotiation for /vocab/actions/
/vocab/actions  /vocab/actions/actions-vocabulary.owl  200  Accept: application/rdf+xml
/vocab/actions  /vocab/actions/actions-vocabulary.owl  200  Accept: application/xml
/vocab/actions  /vocab/actions/actions-vocabulary.ttl  200  Accept: text/turtle
/vocab/actions  /vocab/actions/actions-vocabulary.jsonld  200  Accept: application/ld+json
/vocab/actions  /vocab/actions/actions-vocabulary.jsonld  200  Accept: application/json
/vocab/actions  /vocab/actions/index.html  200

# Trailing slash variant
/vocab/actions/  /vocab/actions/actions-vocabulary.owl  200  Accept: application/rdf+xml
/vocab/actions/  /vocab/actions/actions-vocabulary.owl  200  Accept: application/xml
/vocab/actions/  /vocab/actions/actions-vocabulary.ttl  200  Accept: text/turtle
/vocab/actions/  /vocab/actions/actions-vocabulary.jsonld  200  Accept: application/ld+json
/vocab/actions/  /vocab/actions/actions-vocabulary.jsonld  200  Accept: application/json
/vocab/actions/  /vocab/actions/index.html  200

# Legacy v4 path redirects
/vocab/actions/v4  /vocab/actions/  301
/vocab/actions/v4/  /vocab/actions/  301
/vocab/actions/v4/*  /vocab/actions/:splat  301

# Convenience URLs
/vocab  /vocab/actions/  301
/actions  /vocab/actions/  301
/ontology  /vocab/actions/  301
"""


# ---------------------------------------------------------------------------
# Invoke tasks
# ---------------------------------------------------------------------------

@task
def test(c):
    """Run all SHACL validation tests """
    c.run("pytest")


@task
def validate_ontology_and_SHACL_syntax(c):
    """Validate ontology and SHACL shapes syntax."""
    print("Validating ontology (OWL/XML)...")

    ontology = rdf.Graph().parse('v4/actions-vocabulary.owl', format='xml')
    shapes = rdf.Graph().parse('v4/actions-shapes-v4.ttl', format='turtle')

    if len(ontology) > 0 and len(shapes) > 0:
        print("Ontology and SHACL shapes are valid")
    else:
        print("Validation failed")
        sys.exit(1)


@task
def clean(c):
    """Clean test artifacts and build output."""
    patterns = ["tests/__pycache__", ".pytest_cache", "htmlcov", ".coverage", "site"]
    for pattern in patterns:
        c.run(f"rm -rf {pattern}", warn=True)
    print("Cleaned test artifacts and build output")


@task
def build_site(c):
    """Build the complete vocabulary site for deployment."""
    print("Building vocabulary site...")

    # Clean and recreate site structure
    c.run("rm -rf site")
    c.run("mkdir -p site/vocab/actions site/.well-known")

    # Generate RDF formats from OWL source
    print("Generating RDF formats from ontology...")
    g = rdf.Graph()
    g.parse('v4/actions-vocabulary.owl', format='xml')
    g.serialize('site/vocab/actions/actions-vocabulary.ttl', format='turtle')
    g.serialize('site/vocab/actions/actions-vocabulary.rdf', format='xml')
    g.serialize('site/vocab/actions/actions-vocabulary.jsonld', format='json-ld')
    print('Generated Turtle, RDF/XML, and JSON-LD formats')

    # Copy OWL ontology (canonical format)
    c.run("cp v4/actions-vocabulary.owl site/vocab/actions/")

    # Copy SHACL shapes
    c.run("cp v4/actions-shapes-v4.ttl site/vocab/actions/shapes.ttl")

    # Copy JSON-LD context and JSON schema
    c.run("cp v4/actions.context.json site/vocab/actions/")
    c.run("cp v4/actions.schema.json site/vocab/actions/")

    # Copy well-known files
    c.run("cp .well-known/vocab-catalog.json site/.well-known/")

    # Create HTML landing page
    landing = _landing_page()
    with open("site/index.html", "w") as f:
        f.write(landing)
    with open("site/vocab/actions/index.html", "w") as f:
        f.write(landing)

    # Create Cloudflare Pages configuration
    with open("site/_headers", "w") as f:
        f.write(CLOUDFLARE_HEADERS)
    with open("site/_redirects", "w") as f:
        f.write(CLOUDFLARE_REDIRECTS)

    print("Site built in ./site/ directory")
    print("Ready for Cloudflare Pages deployment")


@task
def serve_local(c, port=8000):
    """Serve the vocabulary site locally for testing."""
    print(f"Starting local server on port {port}...")
    print(f"Visit: http://localhost:{port}")
    print("Test content negotiation with curl:")
    print(f"   curl -H 'Accept: text/turtle' http://localhost:{port}/vocab/actions/")
    print(f"   curl -H 'Accept: application/json' http://localhost:{port}/vocab/actions/")
    print("\nPress Ctrl+C to stop")

    try:
        c.run(f"python -m http.server {port} --directory site")
    except KeyboardInterrupt:
        print("\nServer stopped")


@task
def test_content_negotiation(c):
    """Test content negotiation locally (requires site to be running)."""
    print("Testing content negotiation...")
    base_url = "http://localhost:8000"

    tests = [
        ("text/turtle", "Turtle format"),
        ("application/rdf+xml", "OWL/XML format"),
        ("application/ld+json", "JSON-LD format"),
        ("text/html", "HTML documentation"),
    ]

    for accept_header, description in tests:
        print(f"  Testing {description}...")
        result = c.run(
            f"curl -s -H 'Accept: {accept_header}' {base_url}/vocab/actions/ -w '%{{content_type}}'",
            warn=True,
            hide=True,
        )
        if result.ok:
            print(f"    {description}: {result.stdout.split()[-1] if result.stdout else 'OK'}")
        else:
            print(f"    FAIL {description}")


@task
def deploy_check(c):
    """Validate deployment readiness."""
    print("Checking deployment readiness...")

    required_files = [
        "site/vocab/actions/actions-vocabulary.owl",
        "site/vocab/actions/actions-vocabulary.ttl",
        "site/vocab/actions/shapes.ttl",
        "site/vocab/actions/actions.context.json",
        "site/vocab/actions/actions.schema.json",
        "site/.well-known/vocab-catalog.json",
        "site/index.html",
    ]

    all_good = True
    for file_path in required_files:
        if c.run(f"test -f {file_path}", warn=True).ok:
            print(f"  OK: {file_path}")
        else:
            print(f"  MISSING: {file_path}")
            all_good = False

    # Check Turtle/OWL validity
    ttl_files = c.run("find site -name '*.ttl'", hide=True).stdout.strip().split("\n")
    for ttl_file in ttl_files:
        if ttl_file:
            if c.run(
                f"python -c 'import rdflib; rdflib.Graph().parse(\"{ttl_file}\")'",
                warn=True,
            ).ok:
                print(f"  Valid TTL: {ttl_file}")
            else:
                print(f"  Invalid TTL: {ttl_file}")
                all_good = False

    if all_good:
        print("\nDeployment ready!")
        return True
    else:
        print("\nDeployment not ready - fix issues above")
        sys.exit(1)


@task
def deploy(c):
    """Deploy the vocabulary site to Cloudflare Pages.

    Prerequisites:
    - Wrangler CLI installed and authenticated (wrangler whoami)
    - Site built (uv run invoke build-site)

    Deploys to:
    - Pages URL: https://actions-vocabulary.pages.dev
    - Custom domain: https://clearhead.us/vocab/actions/ (if configured)
    """
    print("Deploying vocabulary site to Cloudflare Pages...")
    print("Target: actions-vocabulary project")
    print("Production URL: https://clearhead.us/vocab/actions/")
    print()

    result = c.run(
        "wrangler pages deploy site --project-name actions-vocabulary --branch main",
        warn=True,
    )

    if result.ok:
        print()
        print("Deployment successful!")
        print("Production URL: https://clearhead.us/vocab/actions/")
    else:
        print("Deployment failed!")
        print("Check wrangler authentication: wrangler whoami")
        print("Ensure site is built: uv run invoke build-site")
        sys.exit(1)
