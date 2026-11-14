// storeurbannest.in/api/admin-analytics?days=7|30
// Traffic numbers for the admin dashboard, read from Cloudflare Web Analytics
// (the beacon Cloudflare Pages already injects on every page) through the
// GraphQL Analytics API.
//
// The Cloudflare token never reaches the browser: the dashboard sends the
// admin's Supabase session, this function checks it is_admin(), and only then
// asks Cloudflare. Settings (Cloudflare dashboard → Pages → storeurbannest →
// Settings → Variables and secrets):
//   CF_API_TOKEN   a token with Account › Account Analytics › Read, nothing else
//   CF_ACCOUNT_ID  the account id (right sidebar of the Cloudflare dashboard)
//   CF_SITE_TAG    Web Analytics → the site → the siteTag in the page URL
// SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are already set for the shop.

const json = (body, status = 200) => new Response(JSON.stringify(body), {
  status, headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' },
});

async function isAdmin(env, token) {
  if (!token || !env.SUPABASE_URL) return false;
  const r = await fetch(env.SUPABASE_URL + '/rest/v1/rpc/is_admin', {
    method: 'POST',
    headers: {
      apikey: env.SUPABASE_ANON_KEY || env.SUPABASE_SERVICE_ROLE_KEY,
      Authorization: 'Bearer ' + token,
      'Content-Type': 'application/json',
    },
    body: '{}',
  });
  if (!r.ok) return false;
  return (await r.json()) === true;
}

// One dimension per alias; every alias shares the same filter.
const DIMS = {
  series:    { by: 'date',              limit: 100, order: 'date_ASC' },
  pages:     { by: 'requestPath',       limit: 300 },
  countries: { by: 'countryName',       limit: 15 },
  devices:   { by: 'deviceType',        limit: 6 },
  referrers: { by: 'refererHost',       limit: 15 },
  browsers:  { by: 'userAgentBrowser',  limit: 8 },
};

function buildQuery() {
  const parts = Object.entries(DIMS).map(([alias, d]) =>
    `${alias}: rumPageloadEventsAdaptiveGroups(limit: ${d.limit}, filter: $f, orderBy: [${d.order || 'count_DESC'}]) { count sum { visits } dimensions { ${d.by} } }`);
  return `query($acct: string, $f: AccountRumPageloadEventsAdaptiveGroupsFilter_InputObject, $p: AccountRumPageloadEventsAdaptiveGroupsFilter_InputObject) {
    viewer { accounts(filter: { accountTag: $acct }) {
      total: rumPageloadEventsAdaptiveGroups(limit: 1, filter: $f) { count sum { visits } }
      prev:  rumPageloadEventsAdaptiveGroups(limit: 1, filter: $p) { count sum { visits } }
      ${parts.join('\n      ')}
    } }
  }`;
}

const filterFor = (siteTag, from, to) => ({ AND: [
  { datetime_geq: from.toISOString(), datetime_lt: to.toISOString() },
  { siteTag },
  { bot: 0 },                           // same as "exclude bots" on Cloudflare's own page
  { requestPath_notlike: '/admin%' },   // his own admin visits are not traffic
  { requestPath_notlike: '/studio%' },
]});

export async function onRequestGet({ request, env }) {
  const token = (request.headers.get('Authorization') || '').replace(/^Bearer\s+/i, '');
  if (!(await isAdmin(env, token))) return json({ error: 'not-admin' }, 401);

  const missing = ['CF_API_TOKEN', 'CF_ACCOUNT_ID', 'CF_SITE_TAG'].filter(k => !env[k]);
  if (missing.length) return json({ error: 'not-configured', missing }, 503);

  const days = new URL(request.url).searchParams.get('days') === '30' ? 30 : 7;
  const to = new Date();
  const from = new Date(to.getTime() - days * 864e5);
  const prevFrom = new Date(from.getTime() - days * 864e5);

  const r = await fetch('https://api.cloudflare.com/client/v4/graphql', {
    method: 'POST',
    headers: { Authorization: 'Bearer ' + env.CF_API_TOKEN, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query: buildQuery(),
      variables: {
        acct: env.CF_ACCOUNT_ID,
        f: filterFor(env.CF_SITE_TAG, from, to),
        p: filterFor(env.CF_SITE_TAG, prevFrom, from),
      },
    }),
  });
  const out = await r.json().catch(() => ({}));
  if (!r.ok || out.errors?.length) {
    return json({ error: 'cloudflare', detail: (out.errors || []).map(e => e.message).join('; ') || ('HTTP ' + r.status) }, 502);
  }
  const a = out.data?.viewer?.accounts?.[0] || {};
  const tot = g => ({ pageviews: g?.[0]?.count || 0, visits: g?.[0]?.sum?.visits || 0 });
  const rows = (alias) => (a[alias] || []).map(g => ({
    key: g.dimensions[DIMS[alias].by] || '',
    pageviews: g.count, visits: g.sum.visits,
  }));

  return json({
    days, from: from.toISOString(), to: to.toISOString(),
    total: tot(a.total), prev: tot(a.prev),
    series: rows('series'), pages: rows('pages'), countries: rows('countries'),
    devices: rows('devices'), referrers: rows('referrers'), browsers: rows('browsers'),
  });
}
