// Audit: every piece placed in a published 3D room vs its listing (exists? live? section? has a 3D model?).
//   node tools/room-listing-audit.mjs            (reads rooms/*/placements.json, Supabase via .env service key)
import { readFileSync, readdirSync, existsSync } from 'node:fs';
const env = Object.fromEntries(readFileSync('.env', 'utf8').split(/\r?\n/).filter(l => l.includes('=')).map(l => [l.slice(0, l.indexOf('=')).trim(), l.slice(l.indexOf('=') + 1).trim()]));
const H = { apikey: env.SUPABASE_SERVICE_ROLE_KEY, Authorization: 'Bearer ' + env.SUPABASE_SERVICE_ROLE_KEY };
const rows = [];
for (const r of readdirSync('rooms')) {
  const f = `rooms/${r}/placements.json`; if (!existsSync(f)) continue;
  const p = JSON.parse(readFileSync(f, 'utf8'));
  for (const d of p.products || []) rows.push({ room: r, kind: 'dot', id: d.id || '', name: d.name, file: d.file || '(in room)' });
  for (const d of p.staging || []) rows.push({ room: r, kind: 'staging', id: d.id || '', name: d.name, file: d.file || '(in room)' });
}
const ids = [...new Set(rows.filter(r => r.id).map(r => r.id))];
const L = await (await fetch(`${env.SUPABASE_URL}/rest/v1/collection_items?id=in.(${ids.join(',')})&select=id,name,section,category,published,model_url`, { headers: H })).json();
for (const r of rows) {
  const l = L.find(x => x.id === r.id);
  console.log([r.room.padEnd(14), r.kind.padEnd(7), r.file.padEnd(38), r.name.slice(0, 28).padEnd(28),
    l ? `${l.section}/${l.category} ${l.published ? 'live' : 'DRAFT'} ${l.model_url ? '3D' : 'NO-3D'}` : (r.id ? 'LISTING NOT FOUND' : 'no listing id')].join(' | '));
}
