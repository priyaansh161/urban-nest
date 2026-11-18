// storeurbannest.in/api/check-amazon   POST { url }   (admin only)  ->  { status, price, title, ... }
// One Amazon link per call, for the admin's "Run full check" on Amazon Links (admin/amazon-links.html), which calls it
// once per piece with a pause between. See _amazon-check.js for what each status means. Only a signed-in admin can
// use it: the page sends its Supabase session and this checks is_admin(), as admin-analytics.js does.
import { checkAmazon } from './_amazon-check.js';

const json = (body, status = 200) => new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' } });

async function isAdmin(env, token) {
  if (!token || !env.SUPABASE_URL) return false;
  const r = await fetch(env.SUPABASE_URL + '/rest/v1/rpc/is_admin', {
    method: 'POST',
    headers: { apikey: env.SUPABASE_ANON_KEY || env.SUPABASE_SERVICE_ROLE_KEY, Authorization: 'Bearer ' + token, 'Content-Type': 'application/json' },
    body: '{}',
  });
  return r.ok && (await r.json()) === true;
}

export async function onRequestPost({ request, env }) {
  const token = (request.headers.get('Authorization') || '').replace(/^Bearer\s+/i, '');
  if (!(await isAdmin(env, token))) return json({ error: 'not-admin' }, 401);
  let body; try { body = await request.json(); } catch { return json({ error: 'bad request' }, 400); }
  const url = String(body.url || '').trim();
  if (!url) return json({ error: 'no url' }, 400);
  return json(await checkAmazon(url));
}
export const onRequest = () => json({ error: 'POST only' }, 405);
