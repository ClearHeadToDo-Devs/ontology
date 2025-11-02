# Content Negotiation Worker for Actions Vocabulary

This Cloudflare Worker provides proper HTTP content negotiation for the Actions Vocabulary v3, following W3C Semantic Web best practices.

## What It Does

The worker intercepts requests to `/vocab/actions/v3/` and serves different RDF formats based on the `Accept` header:

- `Accept: application/rdf+xml` → OWL/XML format
- `Accept: text/turtle` → Turtle format
- `Accept: application/ld+json` → JSON-LD format
- `Accept: text/html` → HTML documentation
- Default → OWL/XML (canonical format)

## Deployment

### 1. Deploy the Worker

```bash
cd workers/content-negotiation
wrangler deploy
```

This creates a worker named `vocab-content-negotiation` in your Cloudflare account.

### 2. Configure Routes

**Option A: Via Cloudflare Dashboard (Recommended)**

1. Go to Cloudflare Dashboard → Workers & Pages
2. Select the `vocab-content-negotiation` worker
3. Go to **Triggers** tab → **Routes** → **Add route**
4. Add route:
   - **Route:** `clearhead.us/vocab/actions/v3*`
   - **Zone:** clearhead.us
   - **Worker:** vocab-content-negotiation

**Option B: Via CLI**

```bash
# Note: Requires zone_id for your clearhead.us domain
wrangler route add "clearhead.us/vocab/actions/v3*" \
  --name vocab-content-negotiation \
  --zone-id YOUR_ZONE_ID
```

### 3. Test Content Negotiation

Once deployed and routed:

```bash
# Request Turtle format
curl -H "Accept: text/turtle" https://clearhead.us/vocab/actions/v3/

# Request JSON-LD
curl -H "Accept: application/ld+json" https://clearhead.us/vocab/actions/v3/

# Request OWL/XML (or use default)
curl -H "Accept: application/rdf+xml" https://clearhead.us/vocab/actions/v3/
curl https://clearhead.us/vocab/actions/v3/

# Browser access (gets HTML)
open https://clearhead.us/vocab/actions/v3/
```

## How It Works

1. **Request** comes to `clearhead.us/vocab/actions/v3/`
2. **Worker** inspects the `Accept` header
3. **Worker** fetches the appropriate file from the Pages deployment
4. **Response** includes `Vary: Accept` header for proper caching
5. **Client** receives the requested format

## Architecture

```
┌─────────────┐
│   Client    │
│ (curl/wget) │
└──────┬──────┘
       │ GET /vocab/actions/v3/
       │ Accept: text/turtle
       ▼
┌─────────────────────┐
│  Cloudflare Worker  │  ◄── Content negotiation logic
│ (this worker)       │
└──────┬──────────────┘
       │ Fetches: /vocab/actions/v3/actions-vocabulary.ttl
       ▼
┌─────────────────────┐
│  Cloudflare Pages   │  ◄── Static files hosting
│ (actions-vocabulary)│
└─────────────────────┘
```

## Alternative: Direct File URLs

If you prefer not to deploy the worker, users can access files directly:

- `https://clearhead.us/vocab/actions/v3/actions-vocabulary.owl`
- `https://clearhead.us/vocab/actions/v3/actions-vocabulary.ttl`
- `https://clearhead.us/vocab/actions/v3/actions-vocabulary.jsonld`

This is a common pattern in the semantic web community and is perfectly acceptable.

## Updating the Worker

```bash
cd workers/content-negotiation

# Edit worker.js as needed

# Deploy updates
wrangler deploy
```

Changes are live immediately after deployment.

## Monitoring

View worker analytics in Cloudflare Dashboard:
- Requests per second
- Error rates
- CPU time
- Cache hit rates

## Troubleshooting

### Worker not being triggered

- Check that the route pattern matches your URL
- Verify the zone (clearhead.us) is correct
- Ensure the worker is deployed successfully

### Wrong format being returned

- Check the `Accept` header being sent
- Test with explicit Accept headers using curl
- Review worker logs in Cloudflare dashboard

### 500 errors

- Check worker logs in Cloudflare dashboard
- Verify the VOCAB_BASE URL in worker.js is correct
- Ensure the Pages deployment is accessible

## Cost

Cloudflare Workers free tier includes:
- 100,000 requests per day
- 10ms CPU time per request

The Actions Vocabulary should comfortably fit within free tier limits.
