import { readFileSync } from 'node:fs';
const env = Object.fromEntries(readFileSync('.env', 'utf8').split(/\r?\n/).filter(l => l.includes('=')).map(l => [l.slice(0, l.indexOf('=')).trim(), l.slice(l.indexOf('=') + 1).trim()]));
const H = { apikey: env.SUPABASE_SERVICE_ROLE_KEY, Authorization: 'Bearer ' + env.SUPABASE_SERVICE_ROLE_KEY, 'Content-Type': 'application/json', Prefer: 'return=representation' };
const pre = ['4c8fd823', 'fcedc362', '51237009', 'bc4469b7', '9696ae59', 'b8a357f5', '9f6d1dc3', '59a91b48'];
const L = await (await fetch(`${env.SUPABASE_URL}/rest/v1/collection_items?select=id,name,published,image_url,section,category`, { headers: H })).json();
for (const p of pre) {
  const x = L.find(r => r.id.startsWith(p)); if (!x) { console.log('missing', p); continue; }
  if (!x.image_url) { console.log('no photo, skipped', x.name); continue; }
  const r = await (await fetch(`${env.SUPABASE_URL}/rest/v1/collection_items?id=eq.${x.id}`, { method: 'PATCH', headers: H, body: JSON.stringify({ published: true }) })).json();
  console.log('published', r[0].published, x.section + '/' + x.category, x.name.slice(0, 70));
}
