#!/usr/bin/env node
/**
 * Admitad helper — talks to the Admitad publisher API.
 *
 *   node tools/admitad.mjs check                       log in, show your ad spaces
 *   node tools/admitad.mjs programs [pending|active|all]   programs on your ad space
 *   node tools/admitad.mjs link <program-id> <product-url> [subid]   make an affiliate link
 *
 * Keys, from the project's .env (never committed):
 *   ADMITAD_CLIENT_ID, ADMITAD_CLIENT_SECRET
 *
 * Nothing here changes your Admitad account: it only reads, and builds links.
 */
import { readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const env = {};
try { for (const l of readFileSync(join(ROOT, '.env'), 'utf8').split(/\r?\n/)) { const m = l.match(/^([A-Z0-9_]+)=(.*)$/); if (m) env[m[1]] = m[2].trim().replace(/^["']|["']$/g, ''); } } catch {}

const ID = env.ADMITAD_CLIENT_ID, SECRET = env.ADMITAD_CLIENT_SECRET;
const API = 'https://api.admitad.com';
const SCOPE = 'advcampaigns advcampaigns_for_website websites deeplink_generator public_data statistics';

async function token() {
  if (!ID || !SECRET) throw new Error('ADMITAD_CLIENT_ID / ADMITAD_CLIENT_SECRET missing in .env');
  const basic = Buffer.from(ID + ':' + SECRET).toString('base64');
  const r = await fetch(API + '/token/', {
    method: 'POST',
    headers: { Authorization: 'Basic ' + basic, 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ grant_type: 'client_credentials', client_id: ID, scope: SCOPE }),
  });
  const j = await r.json().catch(() => ({}));
  if (!r.ok || !j.access_token) throw new Error('Login refused (' + r.status + '): ' + (j.error_description || j.error || JSON.stringify(j)).slice(0, 200));
  return j.access_token;
}

async function get(path, tok) {
  const r = await fetch(API + path, { headers: { Authorization: 'Bearer ' + tok } });
  const j = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(path + ' → ' + r.status + ' ' + JSON.stringify(j).slice(0, 250));
  return j;
}

async function websites(tok) {
  const j = await get('/websites/?limit=50', tok);
  return j.results || [];
}

const [cmd = 'check', a, b, c] = process.argv.slice(2);

try {
  const tok = await token();
  console.log('Login OK.');
  const sites = await websites(tok);
  if (!sites.length) throw new Error('No ad spaces found on this account.');
  for (const s of sites) console.log(`  Ad space ${s.id}: ${s.name} — ${s.status} — ${s.site_url}`);
  const site = sites.find(s => /storeurbannest/i.test(s.site_url || '')) || sites[0];

  if (cmd === 'programs') {
    const filter = (a || 'all').toLowerCase();
    const q = filter === 'all' ? '' : '&connection_status=' + (filter === 'pending' ? 'pending' : 'active');
    const j = await get(`/advcampaigns/website/${site.id}/?limit=100&language=en${q}`, tok);
    const rows = j.results || [];
    console.log(`\n${rows.length} program(s) (${filter}) for ad space ${site.id}:`);
    for (const p of rows) console.log(`  [${p.id}] ${p.name} — ${p.connection_status || p.status} — ${p.site_url}`);
  } else if (cmd === 'link') {
    if (!a || !b) throw new Error('Usage: node tools/admitad.mjs link <program-id> <product-url> [subid]');
    const qs = new URLSearchParams({ ulp: b });
    if (c) qs.set('subid', c);
    const j = await get(`/deeplink/${site.id}/advcampaign/${a}/?${qs}`, tok);
    console.log('\nAffiliate link:\n' + (Array.isArray(j) ? j[0] : JSON.stringify(j)));
  } else if (cmd !== 'check') {
    throw new Error('Unknown command "' + cmd + '". Use check, programs, or link.');
  }
} catch (e) {
  console.error('\nProblem: ' + e.message);
  process.exit(1);
}
