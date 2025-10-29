# Vocabulary Deployment Guide

This document explains how to deploy the Actions Vocabulary as a hosted semantic vocabulary with proper content negotiation and discovery.

## 🎯 Quick Start

The Actions Vocabulary v3 is now consolidated into a single OWL file for easier deployment and use.

### Build and Test Locally

```bash
cd ontology

# Install dependencies
uv sync

# Validate the ontology
uv run python tests/test_poc.py

# Build the complete site (if needed for web hosting)
uv run invoke build-site

# Serve locally for testing
uv run invoke serve-local
```

## 📁 Current Structure

The v3 ontology is now **consolidated** for simplicity:

```
/
├── actions-vocabulary.owl          # Complete v3 ontology (core + extensions)
├── imports/                        # BFO and CCO ontology files
│   ├── bfo.owl
│   ├── cco-event.owl
│   └── cco-information.owl
├── tests/                          # Validation tests
├── docs/                          # Human documentation
├── examples/                       # Example data
└── v2/                            # Legacy v2 ontology (archived)
```

### What's Included in actions-vocabulary.owl

The consolidated ontology includes:

**Core Classes:**
- ActionPlan, ActionProcess
- RootActionPlan, ChildActionPlan, LeafActionPlan
- ActionState (NotStarted, InProgress, Completed, Blocked, Cancelled)

**Context Extension:**
- ActionContext, LocationContext, ToolContext, EnergyContext, SocialContext
- requiresContext, requiresFacility, requiresArtifact, requiresAgent

**Workflow Extension:**
- Milestone class
- dependsOn, cannotStartUntil, mustCompleteBefore, preferredAfter
- blockedBy, canRunInParallel

**Role Integration:**
- assignedToAgent, performedBy, delegatedBy, inRoleContext
- Integration with CCO Agent and Role infrastructure

## 🚀 Hosting Options

### Option 1: GitHub Pages (Recommended for Simple Hosting)

```bash
# In your repository
mkdir -p docs/actions/v3
cp actions-vocabulary.owl docs/actions/v3/

# Commit and push
git add docs/
git commit -m "Add consolidated v3 ontology"
git push

# Enable GitHub Pages in repository settings
# Set source to "docs" folder
```

**Access URL:**
```
https://[username].github.io/[repo]/actions/v3/actions-vocabulary.owl
```

### Option 2: Custom Domain with Content Negotiation

For production deployments with w3id.org or custom domains:

**URI Strategy:**
```
https://vocab.clearhead.io/
└── actions/
    └── v3/                           # Version 3.1.0
        ├── actions-vocabulary.owl     # OWL/XML format (canonical)
        ├── actions-vocabulary.ttl     # Turtle format
        ├── actions-vocabulary.rdf     # RDF/XML format
        └── actions-vocabulary.jsonld  # JSON-LD format
```

**Content Negotiation (.htaccess example):**
```apache
# Serve appropriate format based on Accept header
RewriteEngine On
RewriteBase /actions/v3/

# OWL/XML (default)
RewriteCond %{HTTP_ACCEPT} application/rdf\+xml [NC,OR]
RewriteCond %{HTTP_ACCEPT} application/xml [NC]
RewriteRule ^$ actions-vocabulary.owl [L]

# Turtle
RewriteCond %{HTTP_ACCEPT} text/turtle [NC]
RewriteRule ^$ actions-vocabulary.ttl [L]

# JSON-LD
RewriteCond %{HTTP_ACCEPT} application/ld\+json [NC]
RewriteRule ^$ actions-vocabulary.jsonld [L]

# Default to OWL
RewriteRule ^$ actions-vocabulary.owl [L]
```

### Option 3: w3id.org Permanent Identifier

For permanent, community-maintained URIs:

1. Fork https://github.com/perma-id/w3id.org
2. Create `.htaccess` in `/actions/`:
   ```apache
   # Redirect to your hosted vocabulary
   RewriteRule ^v3$ https://vocab.clearhead.io/actions/v3/ [R=302,L]
   ```
3. Submit pull request to w3id.org
4. Once merged, use `https://w3id.org/actions/v3` in your ontologies

## 🔍 Content Negotiation Testing

Test that your deployment serves the correct format:

```bash
# Request OWL/XML
curl -H "Accept: application/rdf+xml" https://vocab.clearhead.io/actions/v3/

# Request Turtle
curl -H "Accept: text/turtle" https://vocab.clearhead.io/actions/v3/

# Request JSON-LD
curl -H "Accept: application/ld+json" https://vocab.clearhead.io/actions/v3/
```

## 📦 Generating Alternative Formats

If you need to generate TTL, RDF/XML, or JSON-LD formats from the OWL file:

```bash
# Using rdflib (Python)
uv run python -c "
from rdflib import Graph

g = Graph()
g.parse('actions-vocabulary.owl', format='xml')

# Generate Turtle
g.serialize('actions-vocabulary.ttl', format='turtle')

# Generate RDF/XML
g.serialize('actions-vocabulary.rdf', format='pretty-xml')

# Generate JSON-LD
g.serialize('actions-vocabulary.jsonld', format='json-ld')
"
```

## 🔗 Using in Protégé

For local development with Protégé, use the provided catalog file:

**File: `catalog-v001.xml`**
```xml
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<catalog prefer="public" xmlns="urn:oasis:names:tc:entity:xmlns:xml:catalog">
  <uri name="https://vocab.clearhead.io/actions/v3" uri="actions-vocabulary.owl"/>
</catalog>
```

This allows you to:
- Work offline with the ontology
- Reference production URIs in your ontology files
- Protégé automatically resolves to local files

## 📝 Importing in Other Ontologies

To use the Actions Vocabulary in your ontology:

```xml
<owl:Ontology rdf:about="https://example.com/my-ontology">
  <!-- Import the consolidated vocabulary -->
  <owl:imports rdf:resource="https://vocab.clearhead.io/actions/v3"/>
</owl:Ontology>
```

The consolidated vocabulary includes all core classes and extensions, so you only need one import.

## 🔄 Version Management

### Current Version: 3.1.0

The consolidated ontology includes:
- v3.0.0 core (POC) → INTEGRATED
- v3.1.0 extensions (context, workflow, roles) → INTEGRATED

### Version URIs

```
https://vocab.clearhead.io/actions/v3         # Current version (3.1.0)
https://vocab.clearhead.io/actions/v3/3.1.0   # Specific version
https://vocab.clearhead.io/actions/latest     # Always redirects to current
```

**Best Practice:** Use version-specific URIs in production imports for stability.

## 🧪 Validation

After deployment, validate your vocabulary:

```bash
# Test loading
uv run python tests/test_poc.py

# Test reasoning (requires Protégé or owlready2)
# Open in Protégé → Reasoner → HermiT → Start reasoner
```

**Expected Results:**
- ✅ 12 classes loaded
- ✅ 20 properties defined
- ✅ Logically consistent (no reasoning errors)
- ✅ ~229 RDF triples

## 📚 Additional Resources

### W3C Best Practices
- [Cool URIs for the Semantic Web](https://www.w3.org/TR/cooluris/)
- [Best Practices for Publishing Linked Data](https://www.w3.org/TR/ld-bp/)
- [Content Negotiation by Profile](https://www.w3.org/TR/dx-prof-conneg/)

### Tools
- **Protégé**: https://protege.stanford.edu/
- **RDFLib**: https://rdflib.readthedocs.io/
- **w3id.org**: https://github.com/perma-id/w3id.org

### Documentation
- [README.md](./README.md) - User guide and quick start
- [BFO_CCO_ALIGNMENT.md](./BFO_CCO_ALIGNMENT.md) - Technical BFO/CCO mapping
- [SCHEMA_ORG_ALIGNMENT.md](./SCHEMA_ORG_ALIGNMENT.md) - Schema.org integration
- [CLAUDE.md](./CLAUDE.md) - Development guide

## 🆘 Troubleshooting

### Issue: Ontology won't load in Protégé

**Solution:** Uncomment the BFO/CCO import statements in `actions-vocabulary.owl` and ensure you have the import files in the `imports/` directory.

### Issue: Content negotiation not working

**Solution:** Check that:
1. `.htaccess` file is in the correct directory
2. `mod_rewrite` is enabled on your server
3. Files have correct MIME types

### Issue: Imports fail in other ontologies

**Solution:** Ensure:
1. The vocabulary is hosted at the exact URI used in the import statement
2. Content negotiation returns OWL/XML by default
3. The server supports CORS if loading from JavaScript

## 📧 Support

For issues or questions:
- Open an issue on GitHub
- Consult [CLAUDE.md](./CLAUDE.md) for development guidance
- Review [BFO_CCO_ALIGNMENT.md](./BFO_CCO_ALIGNMENT.md) for semantic questions

---

**Last Updated:** 2025-10-29
**Ontology Version:** 3.1.0 (consolidated)
