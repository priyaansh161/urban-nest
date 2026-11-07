// storeurbannest.in/api/country: which country is this visitor in?
// Cloudflare already knows (it sits in front of every request), so there is no lookup service,
// no key, and nothing is stored. market.js asks once per visit and decides India or US from it.
export async function onRequestGet({ request }) {
  const country = (request.cf && request.cf.country) || request.headers.get('CF-IPCountry') || '';
  return new Response(JSON.stringify({ country: String(country).toUpperCase() }), {
    headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' },
  });
}
