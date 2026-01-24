/**
 * Cloudflare Worker for Content Negotiation
 * Routes requests to Actions Vocabulary based on Accept headers
 *
 * Deploy this worker and configure it as a Custom Domain Worker
 * or use Cloudflare's routing to direct requests through this worker.
 */

const VOCAB_BASE = 'https://actions-vocabulary.pages.dev';

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const accept = request.headers.get('Accept') || '';

    // Handle /vocab/actions/v3 and /vocab/actions/v3/ paths
    if (url.pathname === '/vocab/actions/v3' || url.pathname === '/vocab/actions/v3/') {
      return handleVersionNegotiation('v3', accept);
    }

    // Handle /vocab/actions/v4 and /vocab/actions/v4/ paths
    if (url.pathname === '/vocab/actions/v4' || url.pathname === '/vocab/actions/v4/') {
      return handleVersionNegotiation('v4', accept);
    }

    // For all other paths, proxy to Pages deployment
    const targetUrl = new URL(url.pathname + url.search, VOCAB_BASE);
    return fetch(targetUrl);
  }
};

function handleVersionNegotiation(version, accept) {
  let targetPath = null;

  // Content negotiation based on Accept header
  // Note: More sophisticated parsing would handle q-values
  if (accept.includes('application/rdf+xml') || accept.includes('application/xml')) {
    targetPath = `/vocab/actions/${version}/actions-vocabulary.owl`;
  } else if (accept.includes('text/turtle')) {
    targetPath = `/vocab/actions/${version}/actions-vocabulary.ttl`;
  } else if (accept.includes('application/ld+json')) {
    targetPath = `/vocab/actions/${version}/actions-vocabulary.jsonld`;
  } else if (accept.includes('application/json')) {
    targetPath = `/vocab/actions/${version}/actions-vocabulary.jsonld`;
  } else if (accept.includes('text/html')) {
    targetPath = `/vocab/actions/${version}/index.html`;
  } else {
    // Default to OWL/XML (canonical format) for tools like curl without Accept header
    targetPath = `/vocab/actions/${version}/actions-vocabulary.owl`;
  }

  // Fetch from Pages deployment
  const targetUrl = new URL(targetPath, VOCAB_BASE);
  return fetch(targetUrl);
}
