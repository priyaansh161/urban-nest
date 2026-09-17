/* The contributor's login, handled from Admin → Contributors so the admin
 * never has to open the Supabase dashboard.
 *
 *   POST { action: 'invite', email }   send the invite email (or, if they
 *                                      already have a login, a set-password
 *                                      email instead)
 *   POST { action: 'status' }          for every contributor: invited,
 *                                      signed up, last signed in
 *
 * WHY THIS IS SERVER CODE: inviting a user needs Supabase's service-role
 * key, which can do anything to the database. It must never be in a page.
 *
 * WHO MAY CALL IT: only the admin. The page sends its own Supabase session
 * token; this asks Supabase, as that token, whether is_admin() is true —
 * the same check every admin table already uses, so there is one
 * definition of "the admin" (lock-down-rls.sql), not two.
 *
 * Needs SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in Netlify's
 * environment variables, the same two the checkout functions use.
 */
import { json, fail, sb, env, cors, originAllowed } from './lib/shared.mjs';

const STUDIO = 'https://storeurbannest.in/studio/';

async function auth(path, options = {}) {
  const key = env('SUPABASE_SERVICE_ROLE_KEY');
  const res = await fetch(env('SUPABASE_URL') + '/auth/v1/' + path, {
    ...options,
    headers: { apikey: key, Authorization: 'Bearer ' + key, 'Content-Type': 'application/json', ...(options.headers || {}) },
  });
  const text = await res.text();
  let data = null;
  try { data = text ? JSON.parse(text) : null; } catch {}
  return { ok: res.ok, status: res.status, data, message: data?.msg || data?.message || data?.error_description || text };
}

async function callerIsAdmin(req) {
  const token = (req.headers.get('authorization') || '').replace(/^Bearer\s+/i, '');
  if (!token) return false;
  const res = await fetch(env('SUPABASE_URL') + '/rest/v1/rpc/is_admin', {
    method: 'POST',
    headers: { apikey: env('SUPABASE_SERVICE_ROLE_KEY'), Authorization: 'Bearer ' + token, 'Content-Type': 'application/json' },
    body: '{}',
  });
  return res.ok && (await res.json().catch(() => false)) === true;
}

// Every login in the project, keyed by lower-case email. A small site: one page of 1000 is plenty.
async function usersByEmail() {
  const r = await auth('admin/users?page=1&per_page=1000');
  if (!r.ok) throw new Error('Could not list logins: ' + r.message);
  const map = {};
  (r.data?.users || []).forEach(u => { if (u.email) map[u.email.toLowerCase()] = u; });
  return map;
}

export default async (req) => {
  const origin = req.headers.get('origin') || '';
  const headers = { ...cors(origin), 'Access-Control-Allow-Headers': 'Content-Type, Authorization' };
  if (req.method === 'OPTIONS') return new Response(null, { status: 204, headers });
  if (req.method !== 'POST') return fail(405, 'Method not allowed', origin);
  if (!originAllowed(origin)) return fail(403, 'Not allowed from here', origin);

  let body;
  try { body = await req.json(); } catch { return fail(400, 'Malformed request', origin); }

  try {
    if (!(await callerIsAdmin(req))) return fail(403, 'Only the admin can do this', origin);

    if (body?.action === 'status') {
      const [contributors, users] = await Promise.all([sb('contributors?select=id,email'), usersByEmail()]);
      const out = {};
      contributors.forEach(c => {
        const u = users[c.email];
        out[c.id] = !u ? { state: 'none' }
          : u.last_sign_in_at ? { state: 'active', last: u.last_sign_in_at }
          : { state: 'invited', sent: u.invited_at || u.recovery_sent_at || u.created_at };
      });
      return json(200, { status: out }, origin);
    }

    if (body?.action === 'invite') {
      const email = String(body.email || '').trim().toLowerCase();
      if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return fail(400, 'That email does not look right', origin);
      // Only people already on the Contributors list: this is not a way to create logins for anyone.
      const rows = await sb('contributors?select=id,active&email=eq.' + encodeURIComponent(email));
      if (!rows.length) return fail(404, 'Add them as a contributor first', origin);
      if (!rows[0].active) return fail(400, 'This contributor is switched off. Tick Active first', origin);

      const invite = await auth('invite?redirect_to=' + encodeURIComponent(STUDIO), {
        method: 'POST', body: JSON.stringify({ email }),
      });
      if (invite.ok) return json(200, { result: 'invited' }, origin);

      // Already has a login (signed up before, or invited earlier and the link expired):
      // send a "choose a password" email instead, which lands in the same studio screen.
      if (/already been registered|already registered|exists/i.test(invite.message)) {
        const users = await usersByEmail();
        if (users[email]?.last_sign_in_at) return json(200, { result: 'already-active' }, origin);
        const rec = await auth('recover?redirect_to=' + encodeURIComponent(STUDIO), {
          method: 'POST', body: JSON.stringify({ email }),
        });
        if (rec.ok) return json(200, { result: 'reminder' }, origin);
        return rateLimited(rec) || fail(502, 'Could not send the email: ' + rec.message, origin);
      }
      return rateLimited(invite) || fail(502, 'Could not send the invite: ' + invite.message, origin);
    }

    return fail(400, 'Unknown action', origin);
  } catch (err) {
    console.error('contributor-login:', err);
    return fail(500, /Missing environment variable/.test(err.message)
      ? 'The site is missing its Supabase settings on Netlify'
      : 'Something went wrong. Try again in a minute', origin);
  }

  // Supabase's built-in email sender allows only a few emails an hour.
  function rateLimited(r) {
    return r.status === 429 || /rate limit/i.test(r.message)
      ? fail(429, 'Supabase only sends a few emails an hour. Try again in an hour', origin)
      : null;
  }
};
