# Hosting Modular Ontology Extensions

**Problem:** The Phase 2 extensions use `owl:imports` which requires hosted ontologies with stable URIs.

**Current Setup:** You have `https://vocab.clearhead.io/actions/` configured for GitHub Pages.

**Goal:** Host core + extensions with proper import resolution and content negotiation.

---

## 🎯 Recommended URI Strategy

### Option 1: Versioned Namespace Pattern (Recommended)

```
https://vocab.clearhead.io/
├── actions/
│   ├── v3/
│   │   ├── core                          # Core vocabulary
│   │   ├── context                       # Context extension
│   │   ├── workflow                      # Workflow extension
│   │   ├── roles                         # Roles extension
│   │   └── agile                         # Agile extension
│   └── latest/                           # Redirects to current version
```

**Import URIs in OWL:**
```turtle
# In actions-context.owl
<owl:Ontology rdf:about="https://vocab.clearhead.io/actions/v3/context">
  <owl:imports rdf:resource="https://vocab.clearhead.io/actions/v3/core"/>
</owl:Ontology>

# In actions-workflow.owl
<owl:Ontology rdf:about="https://vocab.clearhead.io/actions/v3/workflow">
  <owl:imports rdf:resource="https://vocab.clearhead.io/actions/v3/core"/>
</owl:Ontology>

# In actions-agile.owl (imports multiple)
<owl:Ontology rdf:about="https://vocab.clearhead.io/actions/v3/agile">
  <owl:imports rdf:resource="https://vocab.clearhead.io/actions/v3/core"/>
  <owl:imports rdf:resource="https://vocab.clearhead.io/actions/v3/workflow"/>
  <owl:imports rdf:resource="https://vocab.clearhead.io/actions/v3/roles"/>
</owl:Ontology>
```

**Why This Works:**
- ✅ Version stability (v3 never changes even when v4 is released)
- ✅ Clear separation of core and extensions
- ✅ Content negotiation per module
- ✅ Users can import specific extensions

---

### Option 2: Flat Extension Pattern

```
https://vocab.clearhead.io/actions/
├── core                               # Main vocabulary
├── context-extension                  # Context module
├── workflow-extension                 # Workflow module
├── roles-extension                    # Roles module
└── agile-extension                    # Agile module
```

**Simpler but:**
- ⚠️ No version isolation
- ⚠️ Breaking changes affect all users
- ⚠️ Harder to migrate to new versions

---

## 📁 File Structure on Server

### Recommended Layout

```
/var/www/vocab.clearhead.io/
├── actions/
│   ├── v3/
│   │   ├── core/
│   │   │   ├── index.html                    # Human-readable docs
│   │   │   ├── vocabulary.ttl                # Turtle format
│   │   │   ├── vocabulary.owl                # OWL/XML format
│   │   │   ├── vocabulary.rdf                # RDF/XML format
│   │   │   └── vocabulary.jsonld             # JSON-LD format
│   │   │
│   │   ├── context/
│   │   │   ├── index.html
│   │   │   ├── extension.ttl
│   │   │   ├── extension.owl
│   │   │   ├── extension.rdf
│   │   │   └── extension.jsonld
│   │   │
│   │   ├── workflow/
│   │   │   └── [same structure]
│   │   │
│   │   ├── roles/
│   │   │   └── [same structure]
│   │   │
│   │   └── agile/
│   │       └── [same structure]
│   │
│   └── latest/                              # Symbolic links to current version
│       ├── core -> ../v3/core
│       ├── context -> ../v3/context
│       └── ...
│
├── .well-known/
│   └── vocab-catalog.json                   # Discovery metadata
│
└── index.html                               # Landing page
```

---

## 🔧 Content Negotiation Configuration

### Apache .htaccess (per module)

Create in each module directory (e.g., `/actions/v3/context/.htaccess`):

```apache
# Content Negotiation for actions/v3/context/

Options +FollowSymLinks +MultiViews
DirectoryIndex index.html

# Turtle format
AddType text/turtle .ttl

# OWL/XML format
AddType application/rdf+xml .owl
AddType application/rdf+xml .rdf

# JSON-LD format
AddType application/ld+json .jsonld

# Content negotiation rules
RewriteEngine On
RewriteBase /actions/v3/context/

# If requesting the vocabulary root
RewriteCond %{REQUEST_URI} ^/actions/v3/context/?$
RewriteCond %{HTTP_ACCEPT} text/turtle [NC]
RewriteRule ^$ extension.ttl [L]

RewriteCond %{REQUEST_URI} ^/actions/v3/context/?$
RewriteCond %{HTTP_ACCEPT} application/rdf\+xml [NC,OR]
RewriteCond %{HTTP_ACCEPT} application/owl\+xml [NC]
RewriteRule ^$ extension.owl [L]

RewriteCond %{REQUEST_URI} ^/actions/v3/context/?$
RewriteCond %{HTTP_ACCEPT} application/ld\+json [NC]
RewriteRule ^$ extension.jsonld [L]

RewriteCond %{REQUEST_URI} ^/actions/v3/context/?$
RewriteCond %{HTTP_ACCEPT} text/html [NC]
RewriteRule ^$ index.html [L]

# Default to HTML for browsers
RewriteCond %{REQUEST_URI} ^/actions/v3/context/?$
RewriteRule ^$ index.html [L]
```

### Nginx Configuration

Add to your Nginx server block:

```nginx
server {
    listen 80;
    server_name vocab.clearhead.io;
    root /var/www/vocab.clearhead.io;

    # Actions vocabulary modules
    location ~ ^/actions/v3/(core|context|workflow|roles|agile)/?$ {
        set $module $1;

        # Turtle
        if ($http_accept ~* "text/turtle") {
            rewrite ^ /actions/v3/$module/extension.ttl break;
        }

        # OWL/XML or RDF/XML
        if ($http_accept ~* "application/(rdf|owl)\+xml") {
            rewrite ^ /actions/v3/$module/extension.owl break;
        }

        # JSON-LD
        if ($http_accept ~* "application/ld\+json") {
            rewrite ^ /actions/v3/$module/extension.jsonld break;
        }

        # HTML (default)
        rewrite ^ /actions/v3/$module/index.html break;
    }

    # CORS headers for RDF access
    location ~ \.(ttl|owl|rdf|jsonld)$ {
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods "GET, OPTIONS";
        add_header Access-Control-Allow-Headers "Accept, Content-Type";
    }
}
```

---

## 🚀 Deployment Strategies

### Strategy 1: GitHub Pages (Easiest)

**Pros:**
- ✅ Free hosting
- ✅ Automatic HTTPS
- ✅ GitHub Actions for CI/CD
- ✅ Custom domain support

**Cons:**
- ⚠️ Basic content negotiation (Jekyll limitations)
- ⚠️ No server-side configuration
- ⚠️ Requires client-side detection

**Setup:**

1. **Update file structure:**
```bash
cd /home/primary_desktop/Products/platform/ontology

mkdir -p site/actions/v3/{core,context,workflow,roles,agile}

# Core
cp actions-vocabulary.owl site/actions/v3/core/vocabulary.owl
# Generate other formats...

# Extensions
cp actions-context.owl site/actions/v3/context/extension.owl
cp actions-workflow.owl site/actions/v3/workflow/extension.owl
cp actions-roles.owl site/actions/v3/roles/extension.owl
```

2. **Create `_config.yml` for Jekyll:**
```yaml
# site/_config.yml
title: Actions Vocabulary
url: https://vocab.clearhead.io
baseurl: ""

include:
  - .well-known
  - actions

defaults:
  - scope:
      path: "**/*.ttl"
    values:
      layout: null
      content-type: text/turtle
  - scope:
      path: "**/*.owl"
    values:
      layout: null
      content-type: application/rdf+xml
```

3. **Update imports to use deployed URIs:**
```xml
<!-- actions-context.owl (local development) -->
<owl:imports rdf:resource="file:///path/to/actions-vocabulary.owl"/>

<!-- actions-context.owl (deployed version) -->
<owl:imports rdf:resource="https://vocab.clearhead.io/actions/v3/core"/>
```

4. **Deploy:**
```bash
# Push to GitHub
git add site/
git commit -m "Add v3 modular ontology structure"
git push

# GitHub Actions will deploy to Pages
```

---

### Strategy 2: Netlify (Better Content Negotiation)

**Pros:**
- ✅ Free tier available
- ✅ Excellent content negotiation via `_redirects`
- ✅ Custom domains
- ✅ Automatic HTTPS

**Setup:**

1. **Create `_redirects` file:**
```
# site/_redirects

# Core vocabulary
/actions/v3/core    /actions/v3/core/vocabulary.ttl    200  Accept: text/turtle
/actions/v3/core    /actions/v3/core/vocabulary.owl    200  Accept: application/rdf+xml
/actions/v3/core    /actions/v3/core/vocabulary.owl    200  Accept: application/owl+xml
/actions/v3/core    /actions/v3/core/vocabulary.jsonld 200  Accept: application/ld+json
/actions/v3/core    /actions/v3/core/index.html        200

# Context extension
/actions/v3/context    /actions/v3/context/extension.ttl    200  Accept: text/turtle
/actions/v3/context    /actions/v3/context/extension.owl    200  Accept: application/rdf+xml
/actions/v3/context    /actions/v3/context/extension.jsonld 200  Accept: application/ld+json
/actions/v3/context    /actions/v3/context/index.html       200

# Repeat for workflow, roles, agile...

# Latest version (redirects)
/actions/latest/core      /actions/v3/core      302
/actions/latest/context   /actions/v3/context   302
```

2. **Deploy to Netlify:**
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login
netlify login

# Deploy
cd site
netlify deploy --prod
```

---

### Strategy 3: Custom Server (Full Control)

**Pros:**
- ✅ Complete control over content negotiation
- ✅ Can add advanced features (SPARQL endpoint, etc.)
- ✅ Performance optimization

**Cons:**
- ❌ Requires server management
- ❌ Need to configure HTTPS
- ❌ Cost (VPS/cloud instance)

**Recommended Stack:**
- **Server:** DigitalOcean Droplet ($6/month)
- **Web Server:** Nginx
- **SSL:** Let's Encrypt (free)
- **Domain:** `vocab.clearhead.io`

**Setup:**
```bash
# On server
sudo apt update
sudo apt install nginx certbot python3-certbot-nginx

# Copy ontology files
rsync -avz site/ user@server:/var/www/vocab.clearhead.io/

# Configure Nginx (see config above)
sudo nano /etc/nginx/sites-available/vocab.clearhead.io

# Enable site
sudo ln -s /etc/nginx/sites-available/vocab.clearhead.io /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Get SSL certificate
sudo certbot --nginx -d vocab.clearhead.io
```

---

## 🔄 Import Resolution Strategies

### Problem: Local Development vs Deployed URIs

**Challenge:**
```xml
<!-- In OWL file, what URI to use? -->
<owl:imports rdf:resource="???"/>

<!-- Option A: Local file path -->
<owl:imports rdf:resource="file:///home/.../actions-vocabulary.owl"/>
❌ Won't work for other users

<!-- Option B: Deployed URL -->
<owl:imports rdf:resource="https://vocab.clearhead.io/actions/v3/core"/>
❌ Doesn't work during local development before deployment
```

### Solution 1: Catalog Files (Recommended for Protégé)

Create `catalog-v001.xml` in each directory:

```xml
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<catalog prefer="public" xmlns="urn:oasis:names:tc:entity:xmlns:xml:catalog">

    <!-- Map deployed URLs to local files -->
    <uri name="https://vocab.clearhead.io/actions/v3/core"
         uri="actions-vocabulary.owl"/>

    <uri name="https://vocab.clearhead.io/actions/v3/context"
         uri="actions-context.owl"/>

    <uri name="https://vocab.clearhead.io/actions/v3/workflow"
         uri="actions-workflow.owl"/>

    <uri name="https://vocab.clearhead.io/actions/v3/roles"
         uri="actions-roles.owl"/>

    <uri name="https://vocab.clearhead.io/actions/v3/agile"
         uri="actions-agile.owl"/>

</catalog>
```

**How It Works:**
- Protégé reads `catalog-v001.xml`
- When it sees `owl:imports https://vocab.clearhead.io/...`
- It maps to local file instead
- Best of both worlds: deployed URIs in OWL, local resolution for dev

**Usage:**
1. Keep deployed URIs in OWL files
2. Protégé automatically uses catalog for local development
3. Deployed server serves from actual URLs
4. No code changes needed between dev and production

### Solution 2: Environment-Based URIs (For Scripts)

```python
# scripts/resolve_imports.py
import os
from owlready2 import *

# Set up import mapping
IMPORT_MAP = {
    "https://vocab.clearhead.io/actions/v3/core":
        "./actions-vocabulary.owl",
    "https://vocab.clearhead.io/actions/v3/context":
        "./actions-context.owl",
    # ...
}

# Use in Python
onto = get_ontology("https://vocab.clearhead.io/actions/v3/context")

# Override IRI resolution
def custom_iri_mapper(iri):
    return IMPORT_MAP.get(iri, iri)

onto.load()
```

### Solution 3: Dual-Format Files

Keep two versions during development:

```
actions-context.owl           # Production (deployed URIs)
actions-context-dev.owl       # Development (local file URIs)
```

**Build script converts:**
```python
# tasks.py
@task
def prepare_deployment(c):
    """Convert local imports to deployed URIs"""
    for owl_file in ["actions-context.owl", "actions-workflow.owl", ...]:
        content = open(owl_file).read()

        # Replace local paths with deployed URLs
        content = content.replace(
            'file:///home/.../actions-vocabulary.owl',
            'https://vocab.clearhead.io/actions/v3/core'
        )

        # Write to deployment directory
        with open(f"site/actions/v3/{module}/{owl_file}", "w") as f:
            f.write(content)
```

---

## 📝 Recommended Workflow

### Step 1: Update OWL Files with Deployed URIs

```xml
<!-- actions-context.owl -->
<owl:Ontology rdf:about="https://vocab.clearhead.io/actions/v3/context">
    <owl:versionIRI rdf:resource="https://vocab.clearhead.io/actions/v3.1.0/context"/>
    <owl:imports rdf:resource="https://vocab.clearhead.io/actions/v3/core"/>
</owl:Ontology>
```

### Step 2: Create Catalog for Local Development

```xml
<!-- catalog-v001.xml -->
<?xml version="1.0"?>
<catalog xmlns="urn:oasis:names:tc:entity:xmlns:xml:catalog">
    <uri name="https://vocab.clearhead.io/actions/v3/core"
         uri="actions-vocabulary.owl"/>
    <uri name="https://vocab.clearhead.io/actions/v3/context"
         uri="actions-context.owl"/>
    <!-- ... -->
</catalog>
```

### Step 3: Build Deployment Site

```bash
# Use existing tasks.py or create new build script
uv run invoke build-extensions

# This should:
# 1. Convert OWL to multiple formats (TTL, RDF/XML, JSON-LD)
# 2. Generate HTML documentation
# 3. Create directory structure
# 4. Copy files to site/
```

### Step 4: Deploy

**Option A: GitHub Pages**
```bash
git add site/
git commit -m "Deploy v3.1 with extensions"
git push origin main
# GitHub Actions deploys automatically
```

**Option B: Netlify**
```bash
cd site
netlify deploy --prod
```

**Option C: Custom Server**
```bash
rsync -avz --delete site/ user@server:/var/www/vocab.clearhead.io/
```

### Step 5: Test

```bash
# Test core
curl -H "Accept: text/turtle" https://vocab.clearhead.io/actions/v3/core

# Test extension
curl -H "Accept: text/turtle" https://vocab.clearhead.io/actions/v3/context

# Test import resolution (in Protégé)
# File → Open → actions-context.owl
# Should load core via catalog
```

---

## 🎯 Quick Start: Deploy Extensions Now

### Immediate Steps

1. **Create catalog file:**
```bash
cd /home/primary_desktop/Products/platform/ontology

cat > catalog-v001.xml <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<catalog xmlns="urn:oasis:names:tc:entity:xmlns:xml:catalog">
    <uri name="https://vocab.clearhead.io/actions/v3/core"
         uri="actions-vocabulary.owl"/>
    <uri name="https://vocab.clearhead.io/actions/v3/context"
         uri="actions-context.owl"/>
    <uri name="https://vocab.clearhead.io/actions/v3/workflow"
         uri="actions-workflow.owl"/>
    <uri name="https://vocab.clearhead.io/actions/v3/roles"
         uri="actions-roles.owl"/>
</catalog>
EOF
```

2. **Update imports in extension files:**
```bash
# I'll create a script to update the imports
```

3. **Test in Protégé:**
```bash
# Protégé will use catalog to resolve imports locally
```

4. **Build deployment:**
```bash
# Use existing build system or create minimal build script
```

---

## 📚 Resources

- **W3C Best Practices:** https://www.w3.org/TR/swbp-vocab-pub/
- **OWL Import Resolution:** https://www.w3.org/TR/owl2-syntax/#Imports
- **Catalog Specification:** https://www.oasis-open.org/committees/entity/spec.html
- **Netlify Redirects:** https://docs.netlify.com/routing/redirects/

---

**Next Steps:**
1. Choose deployment strategy (GitHub Pages recommended for start)
2. Create catalog file for local development
3. Update build scripts to handle extensions
4. Deploy and test import resolution

Would you like me to:
1. Create the catalog file?
2. Update the extension OWL files with deployed URIs?
3. Create a build script for the modular deployment?
4. Set up the directory structure?
