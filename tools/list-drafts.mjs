// Lists every unpublished listing (Collection and Essentials) with its category, photo count and whether it has a 3D model.
//   node tools/list-drafts.mjs            -> table
//   node tools/list-drafts.mjs --json     -> drafts.json in the scratch folder given as the next argument
import { readFileSync, writeFileSync } from 'node:fs';
const env = Object.fromEntries(readFileSync('.env', 'utf8').split(/\r?\n/).filter(l => l.includes('=')).map(l => { const i = l.indexOf('='); return [l.slice(0, i).trim(), l.slice(i + 1).trim().replace(/^"|"$/g, '')]; }));
const H = { apikey: env.SUPABASE_SERVICE_ROLE_KEY, Authorization: 'Bearer ' + env.SUPABASE_SERVICE_ROLE_KEY };
const rows = await (await fetch(env.SUPABASE_URL + '/rest/v1/collection_items?published=eq.false&select=*&order=created_at.desc', { headers: H })).json();
if (!Array.isArray(rows)) { console.log(rows); process.exit(1); }
for (const r of rows) {
  const photos = (r.photos || r.images || []).length;
  console.log(r.id.slice(0, 8), (r.section || '').padEnd(10), (r.category || '').padEnd(22), r.model_url ? '3D ' : '-- ', String(photos).padStart(2), 'ph ', (r.created_at || '').slice(0, 10), (r.name || '').slice(0, 70));
}
console.log(rows.length, 'drafts');
const i = process.argv.indexOf('--json'); if (i > 0) writeFileSync(process.argv[i + 1], JSON.stringify(rows, null, 1));
