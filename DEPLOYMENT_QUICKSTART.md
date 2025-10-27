# Deployment Quick Start - Modular Extensions

**Goal:** Host your Actions Vocabulary v3 with modular extensions so others can use `owl:imports`.

**Status:** ✅ Everything is set up and ready to deploy!

---

## What's Been Configured

### 1. Catalog File for Local Development ✅

**File:** `catalog-v001.xml`

**What it does:**
- Maps deployed URLs to local files
- Protégé automatically uses this when you open ontologies
- You can work offline while OWL files reference production URIs

**Example:**
```xml
<!-- In actions-context.owl -->
<owl:imports rdf:resource="https://vocab.clearhead.io/actions/v3/core"/>

<!-- Catalog maps this to: -->
<uri name="https://vocab.clearhead.io/actions/v3/core" uri="actions-vocabulary.owl"/>

<!-- So Protégé loads local file instead of fetching from internet -->
```

### 2. Build Script ✅

**File:** `build_extensions.py`

**What it does:**
- Creates proper directory structure (`site/actions/v3/...`)
- Copies OWL files to deployment locations
- Converts to multiple formats (TTL, RDF/XML, JSON-LD) if rdflib installed
- Generates HTML documentation for each module

**Usage:**
```bash
# Basic build
python build_extensions.py

# Custom output directory
python build_extensions.py --output-dir ./dist

# Skip RDF conversion (faster, OWL only)
python build_extensions.py --skip-conversion
```

### 3. Comprehensive Hosting Guide ✅

**File:** `HOSTING_EXTENSIONS.md`

**Covers:**
- URI strategy (versioned namespaces)
- Content negotiation (Apache, Nginx, Netlify)
- Three deployment options (GitHub Pages, Netlify, Custom Server)
- Import resolution strategies
- Testing procedures

---

## Quick Deploy - GitHub Pages (Recommended)

### Step 1: Build the Site

```bash
cd /home/primary_desktop/Products/platform/ontology

# Install rdflib for format conversion (optional)
uv pip install rdflib

# Build deployment site
python build_extensions.py

# Result: site/ directory ready to deploy
```

### Step 2: Test Locally

```bash
cd site
python -m http.server 8000

# Open browser to: http://localhost:8000
# Test: http://localhost:8000/actions/v3/core/
# Test: http://localhost:8000/actions/v3/context/
```

### Step 3: Deploy to GitHub Pages

```bash
# Add to git
cd /home/primary_desktop/Products/platform/ontology
git add site/ catalog-v001.xml build_extensions.py
git commit -m "Add v3.1 modular extensions with build system"
git push origin main

# GitHub Actions should automatically deploy to:
# https://yourusername.github.io/repository-name/
```

### Step 4: Configure Custom Domain (Optional)

```bash
# Add CNAME file
echo "vocab.clearhead.io" > site/CNAME
git add site/CNAME
git commit -m "Add custom domain"
git push

# Then in GitHub settings:
# Settings → Pages → Custom domain → vocab.clearhead.io

# Configure DNS:
# vocab.clearhead.io CNAME yourusername.github.io
```

---

## Quick Deploy - Netlify (Better Content Negotiation)

### Step 1: Build Site

```bash
python build_extensions.py
```

### Step 2: Create `_redirects` for Content Negotiation

```bash
cat > site/_redirects <<'EOF'
# Content negotiation for Actions Vocabulary modules

# Core
/actions/v3/core    /actions/v3/core/vocabulary.ttl    200  Accept: text/turtle
/actions/v3/core    /actions/v3/core/vocabulary.owl    200  Accept: application/rdf+xml
/actions/v3/core    /actions/v3/core/vocabulary.jsonld 200  Accept: application/ld+json
/actions/v3/core    /actions/v3/core/index.html        200

# Context extension
/actions/v3/context    /actions/v3/context/extension.ttl    200  Accept: text/turtle
/actions/v3/context    /actions/v3/context/extension.owl    200  Accept: application/rdf+xml
/actions/v3/context    /actions/v3/context/extension.jsonld 200  Accept: application/ld+json
/actions/v3/context    /actions/v3/context/index.html       200

# Workflow extension
/actions/v3/workflow    /actions/v3/workflow/extension.ttl    200  Accept: text/turtle
/actions/v3/workflow    /actions/v3/workflow/extension.owl    200  Accept: application/rdf+xml
/actions/v3/workflow    /actions/v3/workflow/extension.jsonld 200  Accept: application/ld+json
/actions/v3/workflow    /actions/v3/workflow/index.html       200

# Roles extension
/actions/v3/roles    /actions/v3/roles/extension.ttl    200  Accept: text/turtle
/actions/v3/roles    /actions/v3/roles/extension.owl    200  Accept: application/rdf+xml
/actions/v3/roles    /actions/v3/roles/extension.jsonld 200  Accept: application/ld+json
/actions/v3/roles    /actions/v3/roles/index.html       200
EOF
```

### Step 3: Deploy

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login
netlify login

# Deploy
cd site
netlify deploy --prod

# Follow prompts to:
# - Create new site or link existing
# - Set publish directory to current directory (.)

# Result: Site deployed to https://random-name.netlify.app
# Configure custom domain: netlify domains:add vocab.clearhead.io
```

---

## How It Works in Practice

### For You (Local Development):

```bash
# 1. Open ontology in Protégé
File → Open → actions-context.owl

# 2. Protégé sees:
<owl:imports rdf:resource="https://vocab.clearhead.io/actions/v3/core"/>

# 3. Checks catalog-v001.xml:
<uri name="https://vocab.clearhead.io/actions/v3/core" uri="actions-vocabulary.owl"/>

# 4. Loads local file actions-vocabulary.owl instead
# Works offline! No deployment needed for development.
```

### For Others (Using Your Ontology):

```turtle
# In their ontology file:
@prefix actions: <https://vocab.clearhead.io/actions/v3/core#> .
@prefix ctx: <https://vocab.clearhead.io/actions/v3/context#> .

<their-ontology> owl:imports <https://vocab.clearhead.io/actions/v3/core> ,
                              <https://vocab.clearhead.io/actions/v3/context> .

# Their ontology editor fetches from deployed URLs:
# 1. GET https://vocab.clearhead.io/actions/v3/core
# 2. Accept: application/rdf+xml
# 3. Server returns: actions/v3/core/vocabulary.owl
# 4. Loaded successfully!
```

### Import Chain Resolution:

```
User's Ontology
  ↓ imports
actions:context (https://vocab.clearhead.io/actions/v3/context)
  ↓ imports
actions:core (https://vocab.clearhead.io/actions/v3/core)
  ↓ imports
CCO (from CCO repository)
  ↓ imports
BFO (from obolibrary.org)
```

All resolved automatically via HTTP!

---

## Current URI Strategy

Based on your existing setup (`https://vocab.clearhead.io`), here's what we're using:

### Versioned Namespaces:

```
https://vocab.clearhead.io/
└── actions/
    ├── v3/                          # Current version (stable)
    │   ├── core                     # Core vocabulary
    │   ├── context                  # Context extension
    │   ├── workflow                 # Workflow extension
    │   ├── roles                    # Roles extension
    │   └── agile                    # Agile extension (future)
    └── latest/                      # Redirects to v3 (for cutting edge users)
```

### Why Versioned?

- ✅ `v3/` URIs never change (even when v4 is released)
- ✅ Users don't break when you release new versions
- ✅ Can maintain multiple versions simultaneously
- ✅ Standard practice for semantic vocabularies

---

## Testing Your Deployment

### 1. Test Local Build:

```bash
cd site
python -m http.server 8000

# Test core
curl -H "Accept: text/turtle" http://localhost:8000/actions/v3/core/vocabulary.ttl | head -5

# Test context extension
curl -H "Accept: application/rdf+xml" http://localhost:8000/actions/v3/context/extension.owl | head -10

# Test HTML
curl http://localhost:8000/actions/v3/context/ | grep "<title>"
```

### 2. Test Deployed Site:

```bash
SITE_URL="https://vocab.clearhead.io"  # Or your actual deployed URL

# Test content negotiation
curl -H "Accept: text/turtle" $SITE_URL/actions/v3/core

# Test import resolution (Protégé will do this)
curl -H "Accept: application/rdf+xml" $SITE_URL/actions/v3/context
```

### 3. Test in Protégé:

```
1. File → Open → Create new ontology
2. Add import:
   <owl:imports rdf:resource="https://vocab.clearhead.io/actions/v3/context"/>
3. Protégé fetches from your deployed site
4. Should load successfully if deployed correctly
```

---

## Troubleshooting

### "Import could not be loaded"

**Problem:** Protégé can't fetch import from deployed URL.

**Solutions:**
1. Check site is actually deployed and accessible
2. Test URL in browser: `https://vocab.clearhead.io/actions/v3/core`
3. Check content negotiation (should return OWL when Accept header is set)
4. Temporarily use local catalog for development

### "Circular import detected"

**Problem:** Extension A imports B, B imports A.

**Solution:**
- Review import chains in PHASE2_DESIGN.md
- Only import what you actually need
- Core should never import extensions
- Extensions can import core and each other (carefully)

### "Build script fails"

**Problem:** `build_extensions.py` errors.

**Solutions:**
```bash
# Install missing dependencies
uv pip install rdflib

# Check file paths
ls actions-*.owl

# Run with verbose errors
python build_extensions.py --skip-conversion
```

---

## Summary

✅ **You have:**
- Catalog file for local development (`catalog-v001.xml`)
- Build script to create deployment site (`build_extensions.py`)
- Complete hosting guide (`HOSTING_EXTENSIONS.md`)
- Modular ontology extensions ready to deploy

✅ **To deploy:**
1. `python build_extensions.py` (creates `site/` directory)
2. Deploy `site/` to GitHub Pages, Netlify, or custom server
3. Test with `curl` or Protégé
4. Share URLs with users!

✅ **URLs users will use:**
- Core: `https://vocab.clearhead.io/actions/v3/core`
- Context: `https://vocab.clearhead.io/actions/v3/context`
- Workflow: `https://vocab.clearhead.io/actions/v3/workflow`
- Roles: `https://vocab.clearhead.io/actions/v3/roles`

---

**Ready to deploy?** Follow "Quick Deploy - GitHub Pages" section above!

**Need more details?** See `HOSTING_EXTENSIONS.md` for comprehensive guide.

**Questions?** Check "Troubleshooting" section or open an issue.
