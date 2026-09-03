/* Shared by every checkout function.
 *
 * No npm dependencies on purpose — the rest of this project has none, and
 * Razorpay and Supabase both speak plain HTTP. `fetch` and `node:crypto`
 * are built in, so there is nothing to install, bundle or keep patched.
 *
 * This file sits in lib/ rather than beside the functions because Netlify
 * treats every file in the functions root as its own endpoint.
 */
import { createHmac, timingSafeEqual } from 'node:crypto';

/* ── WHO MAY CALL THESE ──
   The site's own pages and nothing else. netlify.toml opens CORS to * for
   the static files, which is fine for a .glb and not fine for an endpoint
   that creates payments — so these check the origin themselves. */
const ALLOWED = [
  'https://storeurbannest.netlify.app',
  'http://localhost:3000',   // npx serve
  'http://localhost:4322',   // npx serve, older port
  'http://localhost:8888'    // netlify dev
];

/* The list above only shaped the response header, which stops another
   website calling these from a browser but stops nothing else: curl sends
   no Origin at all and was served happily, so anyone could sit there
   creating orders. Browsers send Origin on every POST, so requiring one
   costs a real visitor nothing and costs a script everything. */
export function originAllowed(origin) {
  return ALLOWED.includes(origin);
}

export function cors(origin) {
  const ok = ALLOWED.includes(origin) ? origin : ALLOWED[0];
  return {
    'Access-Control-Allow-Origin': ok,
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Vary': 'Origin'
  };
}

export function json(status, body, origin) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json', ...cors(origin) }
  });
}

/* Anything the visitor is allowed to see. Never an internal message: a
   failed lookup should not tell a stranger which ids exist. */
export function fail(status, message, origin) {
  return json(status, { error: message }, origin);
}

export function env(name) {
  const v = process.env[name];
  if (!v) throw new Error('Missing environment variable: ' + name);
  return v;
}

/* ── SUPABASE, VIA POSTGREST ──
   Using the service-role key, which bypasses row-level security. That is
   the point: orders have no insert policy at all, so nothing in a browser
   can write one — only this server code can. */
export async function sb(path, options = {}) {
  const key = env('SUPABASE_SERVICE_ROLE_KEY');
  const res = await fetch(env('SUPABASE_URL') + '/rest/v1/' + path, {
    ...options,
    headers: {
      apikey: key,
      Authorization: 'Bearer ' + key,
      'Content-Type': 'application/json',
      ...(options.headers || {})
    }
  });
  const text = await res.text();
  const data = text ? JSON.parse(text) : null;
  if (!res.ok) {
    const err = new Error('Supabase ' + res.status + ': ' + (data?.message || text));
    err.status = res.status;
    throw err;
  }
  return data;
}

/* ── RAZORPAY REST ──
   Basic auth, key id as the username and the secret as the password. The
   secret never leaves this process. */
export async function razorpay(path, options = {}) {
  const auth = Buffer.from(env('RAZORPAY_KEY_ID') + ':' + env('RAZORPAY_KEY_SECRET')).toString('base64');
  const res = await fetch('https://api.razorpay.com/v1/' + path, {
    ...options,
    headers: {
      Authorization: 'Basic ' + auth,
      'Content-Type': 'application/json',
      ...(options.headers || {})
    }
  });
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    const err = new Error('Razorpay ' + res.status + ': ' + (data?.error?.description || 'request failed'));
    err.status = res.status;
    err.detail = data;
    throw err;
  }
  return data;
}

/* Constant-time compare. A plain === leaks, through how long it takes to
   fail, roughly how much of a forged signature was correct. */
export function signatureMatches(expectedHex, gotHex) {
  if (typeof gotHex !== 'string' || gotHex.length !== expectedHex.length) return false;
  try {
    return timingSafeEqual(Buffer.from(expectedHex, 'hex'), Buffer.from(gotHex, 'hex'));
  } catch {
    return false;
  }
}

export function hmacHex(secret, payload) {
  return createHmac('sha256', secret).update(payload).digest('hex');
}

/* Guards against a test key being swapped for a live one by accident.
   Every function calls this, so going live is a deliberate act rather
   than something that happens because a variable changed. */
export function assertTestMode() {
  if (!env('RAZORPAY_KEY_ID').startsWith('rzp_test_')) {
    throw new Error('Refusing to run: RAZORPAY_KEY_ID is not a test key.');
  }
}
