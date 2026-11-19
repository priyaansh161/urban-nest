// Pulls the listings the hall places (id, name, links, description, specs, model) into hall_items.json and downloads each
// model into products/final/<id8>.glb, so the room shows exactly what the listing shows.
//   node mocks/room-hall/fetch_hall.mjs
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
const env = Object.fromEntries(readFileSync('.env', 'utf8').split(/\r?\n/).filter(l => l.includes('=')).map(l => { const i = l.indexOf('='); return [l.slice(0, i).trim(), l.slice(i + 1).trim().replace(/^"|"$/g, '')]; }));
const H = { apikey: env.SUPABASE_SERVICE_ROLE_KEY, Authorization: 'Bearer ' + env.SUPABASE_SERVICE_ROLE_KEY };
const IDS = ['8ff6fee2', 'e716af29', '91771cce', '395cbcd3', '7fbfd698', '13e166b8', 'cbee0eaf', '2278822e', '9f32d7bc', '3a02a4b4', '0c9ab81d', '6f883f83', '1ff58ff3', '088bb117', '9e634a2b', '1e947d6f', '9fb4a2b2', '0193738b', '5b371767', 'd3cee741', '8ff79f13', '8a23c448', '4c2926dd', '1de21753', '39c8d0fd'];
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
