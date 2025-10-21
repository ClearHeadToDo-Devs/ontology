# Vocabulary Deployment Guide

This document explains how to deploy the Actions Vocabulary as a hosted semantic vocabulary with proper content negotiation and discovery.

## 🎯 Architecture

The deployment implements W3C best practices for vocabulary hosting:

```
https://vocab.clearhead.io/
├── actions/                          # Vocabulary namespace  
│   ├── vocabulary.ttl                # OWL ontology (Turtle)
│   ├── shapes.ttl                    # SHACL constraints
│   ├── vocabulary.rdf                # RDF/XML format
│   ├── vocabulary.jsonld             # JSON-LD format
│   ├── schemas/                      # Generated JSON schemas
│   │   ├── action.schema.json
│   │   ├── rootaction.schema.json
│   │   ├── childaction.schema.json
│   │   ├── leafaction.schema.json
│   │   └── actions-combined.schema.json
│   └── examples/                     # Example data
├── docs/                            # Human documentation
├── .well-known/                     # Discovery metadata
│   └── vocab-catalog.json
└── index.html                       # Landing page
```

## 🚀 Quick Start

### Build and Test Locally

```bash
cd ontology

# Install dependencies
uv sync

# Build the complete site
uv run invoke build-site

# Serve locally for testing
uv run invoke serve-local

# Test content negotiation (in another terminal)
uv run invoke test-content-negotiation
```

### Manual Testing

```bash
# Test different Accept headers
curl -H "Accept: text/turtle" http://localhost:8000/actions/
curl -H "Accept: application/json" http://localhost:8000/actions/
curl -H "Accept: text/html" http://localhost:8000/actions/
curl -H "Accept: application/rdf+xml" http://localhost:8000/actions/
curl -H "Accept: application/ld+json" http://localhost:8000/actions/
```

## 🤖 Automated Deployment

### GitHub Actions (Recommended)

The repository includes a complete GitHub Actions workflow at `.github/workflows/deploy-vocab.yml` that:

1. **Validates** ontology and SHACL constraints
2. **Generates** JSON schemas and additional formats  
3. **Builds** the complete site structure
4. **Deploys** to GitHub Pages automatically

#### Setup GitHub Pages

1. Enable GitHub Pages in repository settings
2. Set source to "GitHub Actions"
3. Push changes to main branch
4. Site will be available at: `https://yourusername.github.io/yourrepo/`

#### Custom Domain Setup

1. Add CNAME file: `echo "vocab.clearhead.io" > ontology/docs/vocab-site/CNAME`
2. Configure DNS: `vocab.clearhead.io CNAME yourusername.github.io`
3. Enable custom domain in GitHub Pages settings

### Manual Deployment

```bash
# Build site
cd ontology
uv run invoke build-site

# Deploy to server (example with rsync)
rsync -avz --delete site/ user@server:/var/www/vocab.clearhead.io/
```

## 🌐 Content Negotiation

The deployment supports automatic format selection based on HTTP Accept headers:

| Accept Header | Response | Format |
|---------------|----------|--------|
| `text/turtle` | `vocabulary.ttl` | RDF Turtle |
| `application/rdf+xml` | `vocabulary.rdf` | RDF/XML |
| `application/ld+json` | `vocabulary.jsonld` | JSON-LD |
| `application/json` | `actions-combined.schema.json` | JSON Schema |
| `text/html` | `index.html` | HTML Documentation |

### Implementation Options

#### Apache (.htaccess)
```apache
# Copy docs/vocab-site/_htaccess to your web root as .htaccess
cp ontology/docs/vocab-site/_htaccess /var/www/.htaccess
```

#### Nginx
```nginx
# Use the provided nginx.conf
sudo cp ontology/docs/vocab-site/nginx.conf /etc/nginx/sites-available/vocab.clearhead.io
sudo ln -s /etc/nginx/sites-available/vocab.clearhead.io /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

#### GitHub Pages + Jekyll
GitHub Pages handles basic content negotiation, but for full semantic web support, consider using a custom solution or Netlify.

## 📋 Validation & Testing

### Pre-deployment Checks

```bash
# Run full validation pipeline
uv run invoke full-pipeline

# Check deployment readiness
uv run invoke deploy-check

# Validate site structure
find site -type f | head -20
```

### Post-deployment Testing

```bash
VOCAB_URL="https://vocab.clearhead.io"

# Test ontology accessibility
curl -H "Accept: text/turtle" $VOCAB_URL/actions/ | head -10

# Test JSON schema  
curl -H "Accept: application/json" $VOCAB_URL/actions/ | jq '.title'

# Test discovery metadata
curl $VOCAB_URL/.well-known/vocab-catalog.json | jq '.title'

# Test HTML documentation
curl -H "Accept: text/html" $VOCAB_URL/actions/ | grep -o '<title>.*</title>'
```

## 🔧 Customization

### Branding & Styling

Edit the HTML templates in `docs/vocab-site/`:
- `index.html` - Main landing page
- `actions/index.html` - Actions vocabulary page  
- `docs/integration.html` - Integration guide

### Additional Formats

Add support for more formats by extending `generate_additional_formats()` in `tasks.py`:

```python
@task
def generate_additional_formats(c):
    # Add N-Triples format
    c.run('''python -c "
import rdflib
g = rdflib.Graph()
g.parse('actions-vocabulary.ttl', format='turtle')
g.serialize('actions-vocabulary.nt', format='nt')
"''')
```

### Custom Deployment Targets

Enable custom deployment in `.github/workflows/deploy-vocab.yml`:

```yaml
deploy-custom:
  name: Deploy to Custom Host
  if: github.ref == 'refs/heads/main' && true  # Change to 'true'
```

Add secrets to your repository:
- `DEPLOY_HOST` - Your server hostname
- `DEPLOY_USER` - SSH username  
- `DEPLOY_KEY` - SSH private key
- `DEPLOY_PATH` - Target directory path

## 🔍 Monitoring & Maintenance

### Analytics

Add web analytics to track vocabulary usage:

```html
<!-- Add to HTML templates -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_TRACKING_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_TRACKING_ID');
</script>
```

### Access Logs

Monitor access patterns to understand usage:

```bash
# Analyze Nginx access logs
grep "GET /actions" /var/log/nginx/access.log | \
  awk '{print $7 " " $9}' | sort | uniq -c | sort -nr

# Monitor Accept headers
grep "GET /actions" /var/log/nginx/access.log | \
  grep -o 'text/turtle\|application/json\|text/html' | \
  sort | uniq -c
```

### Health Checks

Set up monitoring for vocabulary availability:

```bash
#!/bin/bash
# health-check.sh

VOCAB_URL="https://vocab.clearhead.io"
TIMEOUT=10

# Test core endpoints
endpoints=(
  "actions/vocabulary.ttl:text/turtle"
  "actions/schemas/actions-combined.schema.json:application/json"
  ".well-known/vocab-catalog.json:application/json"
)

for endpoint in "${endpoints[@]}"; do
  url="${endpoint%:*}"
  type="${endpoint#*:}"
  
  status=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Accept: $type" \
    --max-time $TIMEOUT \
    "$VOCAB_URL/$url")
  
  if [ "$status" = "200" ]; then
    echo "✅ $url ($type)"
  else
    echo "❌ $url ($type) - Status: $status"
    exit 1
  fi
done

echo "🎉 All vocabulary endpoints healthy"
```

## 📚 Resources

- [W3C Best Practices for Publishing Vocabularies](https://www.w3.org/TR/swbp-vocab-pub/)
- [Content Negotiation Guidelines](https://www.w3.org/DesignIssues/Negotiation.html)
- [JSON Schema Best Practices](https://json-schema.org/understanding-json-schema/)
- [SHACL Specification](https://www.w3.org/TR/shacl/)

## ❓ Troubleshooting

### Common Issues

#### Content Negotiation Not Working
- Check server configuration (Apache/Nginx)
- Verify MIME types are set correctly
- Test with explicit Accept headers

#### Schemas Not Loading
- Ensure CORS headers are configured
- Check schema URLs are accessible
- Validate JSON schema syntax

#### GitHub Pages Deployment Fails
- Verify GitHub Pages is enabled
- Check workflow permissions
- Review build logs for errors

#### SSL Certificate Issues
- Use Let's Encrypt for free SSL
- Ensure certificate covers subdomain
- Check certificate chain completion

For additional support, please open an issue in the repository.