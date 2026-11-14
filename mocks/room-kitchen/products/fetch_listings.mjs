// Pull the kitchen listings (names, specs, photos) into products/src/<id8>/ to model from.
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'fs';
const env = Object.fromEntries(readFileSync(new URL('../../../.env', import.meta.url), 'utf8').split(/\r?\n/).filter(l => l.includes('=')).map(l => [l.slice(0, l.indexOf('=')).trim(), l.slice(l.indexOf('=') + 1).trim().replace(/^"|"$/g, '')]));
const H = { apikey: env.SUPABASE_SERVICE_ROLE_KEY, Authorization: 'Bearer ' + env.SUPABASE_SERVICE_ROLE_KEY };
const rows = await (await fetch(env.SUPABASE_URL + '/rest/v1/collection_items?select=id,name,category,section,published,model_url,image_url,gallery,description,specs&order=created_at.desc&limit=400', { headers: H })).json();
const k = rows.filter(r => /kitchen|dining|cook/i.test((r.category || '') + ' ' + r.name));
const out = [];
for (const r of k) {
  const d = new URL('src/' + r.id.slice(0, 8) + '/', import.meta.url); mkdirSync(d, { recursive: true });
  const imgs = [r.image_url].concat(Array.isArray(r.gallery) ? r.gallery : []).filter(Boolean).slice(0, 6);
  for (const [i, u] of imgs.entries()) { const f = new URL(i + '.webp', d); if (!existsSync(f)) try { writeFileSync(f, Buffer.from(await (await fetch(u)).arrayBuffer())); } catch {} }
  out.push({ id: r.id, name: r.name, category: r.category, published: r.published, model: !!r.model_url, specs: r.specs, description: (r.description || '').slice(0, 400), photos: imgs.length });
}
writeFileSync(new URL('listings.json', import.meta.url), JSON.stringify(out, null, 1));
for (const o of out) console.log(o.id.slice(0, 8), o.published ? 'LIVE ' : 'draft', o.model ? '3D' : '--', o.category, '|', o.name.slice(0, 90));
