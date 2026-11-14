import { readFileSync } from 'node:fs';
import { createRequire } from 'module'; const require = createRequire(import.meta.url); const sharp = require('./node_modules/sharp');
const env = Object.fromEntries(readFileSync('.env', 'utf8').split(/\r?\n/).filter(l => l.includes('=')).map(l => [l.slice(0, l.indexOf('=')).trim(), l.slice(l.indexOf('=') + 1).trim()]));
const H = { apikey: env.SUPABASE_SERVICE_ROLE_KEY, Authorization: 'Bearer ' + env.SUPABASE_SERVICE_ROLE_KEY };
const ids = process.argv[2].split(',');
const L = await (await fetch(`${env.SUPABASE_URL}/rest/v1/collection_items?select=id,name,image_url&id=in.(${ids.join(',')})`, { headers: H })).json();
const comps = []; let i = 0;
for (const id of ids) {
  const x = L.find(r => r.id === id); if (!x) continue;
  const buf = Buffer.from(await (await fetch(x.image_url)).arrayBuffer());
  const t = await sharp(buf).resize(300, 300, { fit: 'contain', background: '#fff' }).toBuffer();
  comps.push({ input: t, left: (i % 5) * 300, top: Math.floor(i / 5) * 340 + 40 });
  comps.push({ input: { text: { text: `<span size="small">${i}: ${id.slice(0, 8)} ${x.name.slice(0, 28).replace(/&/g, 'and')}</span>`, rgba: true, width: 290 } }, left: (i % 5) * 300 + 4, top: Math.floor(i / 5) * 340 + 6 });
  i++;
}
await sharp({ create: { width: 1500, height: Math.ceil(i / 5) * 340, channels: 3, background: '#ddd' } }).composite(comps).jpeg({ quality: 80 }).toFile(process.argv[3]);
console.log('sheet', i);
