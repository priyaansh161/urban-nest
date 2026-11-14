// Pulls every kitchen-essentials listing (id, name, links, description, model) from Supabase into kitchen_items.json and
// downloads each attached model into products/final/ (what is LIVE, so the room shows exactly what the listing shows).
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
const env = Object.fromEntries(readFileSync('.env', 'utf8').split(/\r?\n/).filter(l => l.includes('=')).map(l => { const i = l.indexOf('='); return [l.slice(0, i).trim(), l.slice(i + 1).trim().replace(/^"|"$/g, '')]; }));
const H = { apikey: env.SUPABASE_SERVICE_ROLE_KEY, Authorization: 'Bearer ' + env.SUPABASE_SERVICE_ROLE_KEY };
const rows = await (await fetch(env.SUPABASE_URL + '/rest/v1/collection_items?category=eq.kitchen-essentials&select=*', { headers: H })).json();
const D = 'mocks/room-kitchen/';
writeFileSync(D + 'kitchen_items.json', JSON.stringify(rows, null, 1));
for (const r of rows) {
  const f = D + 'products/final/' + r.id.slice(0, 8) + '.glb';
  if (r.model_url) { const b = Buffer.from(await (await fetch(r.model_url.replace(/ /g, '%20'))).arrayBuffer()); writeFileSync(f, b); }
  console.log(r.id.slice(0, 8), r.published ? 'pub ' : 'draft', r.model_url ? (existsSync(f) ? 'model' : '?') : '--   ', (r.name || '').slice(0, 60));
}
