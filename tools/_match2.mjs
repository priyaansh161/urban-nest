import { readFileSync } from 'node:fs';
const env = Object.fromEntries(readFileSync('.env', 'utf8').split(/\r?\n/).filter(l => l.includes('=')).map(l => [l.slice(0, l.indexOf('=')).trim(), l.slice(l.indexOf('=') + 1).trim()]));
const H = { apikey: env.SUPABASE_SERVICE_ROLE_KEY, Authorization: 'Bearer ' + env.SUPABASE_SERVICE_ROLE_KEY };
const L = await (await fetch(`${env.SUPABASE_URL}/rest/v1/collection_items?select=id,name,published,model_url,buy_link,image_url,section,category,gallery`, { headers: H })).json();
const asin = s => ((s || '').match(/\/dp\/([A-Z0-9]{10})/) || [])[1];
const word = s => (s || '').split(/[\s|®]+/)[0].toLowerCase();
for (const room of ['quiet-bath', 'sunday-bedroom']) {
  const p = JSON.parse(readFileSync(`rooms/${room}/placements.json`, 'utf8'));
  for (const d of p.products) {
    const own = L.find(x => x.id === d.id); if (!own || own.section !== 'essentials') continue;
    const a = asin(d.link), brand = word(d.listing);
    console.log(`\n${d.name} [room listing ${own.id.slice(0,8)} ${own.published ? 'live' : 'draft'} photos:${own.image_url ? 'y' : 'n'}/${(own.gallery||[]).length} name:"${own.name.slice(0,40)}"] ASIN ${a} brand ${brand}`);
    for (const x of L) if (x.id !== own.id && ((a && asin(x.buy_link) === a) || (brand.length > 3 && x.name.toLowerCase().startsWith(brand))))
      console.log(`    candidate ${x.id.slice(0,8)} ${x.published ? 'live ' : 'draft'} ${x.model_url ? '3D   ' : 'NO-3D'} ${x.section}/${x.category} ${x.name.slice(0, 70)} | ${(x.buy_link||'').slice(0,45)}`);
  }
}
