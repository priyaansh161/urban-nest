// Pulls the listings the hall places (id, name, links, description, specs, model) into hall_items.json and downloads each
// model into products/final/<id8>.glb, so the room shows exactly what the listing shows.
//   node mocks/room-hall/fetch_hall.mjs
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
const env = Object.fromEntries(readFileSync('.env', 'utf8').split(/\r?\n/).filter(l => l.includes('=')).map(l => { const i = l.indexOf('='); return [l.slice(0, i).trim(), l.slice(i + 1).trim().replace(/^"|"$/g, '')]; }));
const H = { apikey: env.SUPABASE_SERVICE_ROLE_KEY, Authorization: 'Bearer ' + env.SUPABASE_SERVICE_ROLE_KEY };
const IDS = ['8ff6fee2', 'e716af29', 'aef51ee7', 'e570aa03', '9677aca6', '872070ef', '91771cce', 'bd5ca151', '395cbcd3', '553c88f9', '271ce125', 'ade2831e', '8ff79f13'];
const all = await (await fetch(env.SUPABASE_URL + '/rest/v1/collection_items?select=*', { headers: H })).json();
const rows = IDS.map(p => all.find(r => r.id.startsWith(p))).filter(Boolean);
const D = 'mocks/room-hall/';
mkdirSync(D + 'products/final', { recursive: true });
writeFileSync(D + 'hall_items.json', JSON.stringify(rows, null, 1));
for (const r of rows) {
  const f = D + 'products/final/' + r.id.slice(0, 8) + '.glb';
  if (r.model_url) writeFileSync(f, Buffer.from(await (await fetch(r.model_url.replace(/ /g, '%20'))).arrayBuffer()));
  console.log(r.id.slice(0, 8), r.published ? 'pub ' : 'draft', r.model_url ? 'model' : '--   ', (r.name || '').slice(0, 60));
}
