import { readFileSync } from 'node:fs';
const env = Object.fromEntries(readFileSync('.env', 'utf8').split(/\r?\n/).filter(l => l.includes('=')).map(l => [l.slice(0, l.indexOf('=')).trim(), l.slice(l.indexOf('=') + 1).trim()]));
const H = { apikey: env.SUPABASE_SERVICE_ROLE_KEY, Authorization: 'Bearer ' + env.SUPABASE_SERVICE_ROLE_KEY };
const L = await (await fetch(`${env.SUPABASE_URL}/rest/v1/collection_items?section=eq.essentials&select=id,name,published,model_url,buy_link,category`, { headers: H })).json();
for (const room of ['quiet-bath', 'sunday-bedroom']) {
  const p = JSON.parse(readFileSync(`rooms/${room}/placements.json`, 'utf8'));
  for (const d of p.products) {
    const own = L.find(x => x.id === d.id); if (!own) continue;
    const same = L.filter(x => x.id !== d.id && x.buy_link && d.link && (x.buy_link === d.link || x.buy_link === own.buy_link));
    console.log(room, '|', d.name.padEnd(22), '| link', (d.link || '').slice(0, 42), '| listing', own.published ? 'live' : 'DRAFT', (own.buy_link || '').slice(0, 40), '| listing name:', (d.listing || '').slice(0, 50));
    for (const s of same) console.log('     SAME LINK ->', s.id.slice(0, 8), s.published ? 'live' : 'draft', s.model_url ? '3D' : 'NO-3D', s.name.slice(0, 60));
  }
}
