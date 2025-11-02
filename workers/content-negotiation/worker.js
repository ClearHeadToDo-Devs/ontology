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

    // Only handle /vocab/actions/v3 and /vocab/actions/v3/ paths
    if (url.pathname === '/vocab/actions/v3' || url.pathname === '/vocab/actions/v3/') {
      let targetPath = null;

      // Content negotiation based on Accept header
      // Note: More sophisticated parsing would handle q-values
      if (accept.includes('application/rdf+xml') || accept.includes('application/xml')) {
        targetPath = '/vocab/actions/v3/actions-vocabulary.owl';
      } else if (accept.includes('text/turtle')) {
        targetPath = '/vocab/actions/v3/actions-vocabulary.ttl';
      } else if (accept.includes('application/ld+json')) {
        targetPath = '/vocab/actions/v3/actions-vocabulary.jsonld';
      } else if (accept.includes('application/json')) {
        targetPath = '/vocab/actions/v3/actions-vocabulary.jsonld';
      } else if (accept.includes('text/html')) {
        targetPath = '/vocab/actions/index.html';
      } else {
        // Default to OWL/XML (canonical format) for tools like curl without Accept header
        targetPath = '/vocab/actions/v3/actions-vocabulary.owl';
      }

      // Fetch from Pages deployment
      const targetUrl = new URL(targetPath, VOCAB_BASE);
      const response = await fetch(targetUrl);

      // Add Vary header for caching
      const newResponse = new Response(response.body, response);
      newResponse.headers.set('Vary', 'Accept');

      return newResponse;
    }

    // For all other paths, proxy to Pages deployment
    const targetUrl = new URL(url.pathname + url.search, VOCAB_BASE);
    return fetch(targetUrl);
  }
};
