// One staging item: photo -> Meshy (same settings as tools/list-product.mjs) -> raw GLB.
//   node meshy_staging.mjs <photo.jpg> <out-raw.glb>
// Uses MESHY_API_KEY from the project's .env. Spends Meshy credits (~35).
import { readFileSync, writeFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
const HERE = dirname(fileURLToPath(import.meta.url));
const env = readFileSync(resolve(HERE, '../../.env'), 'utf8');
const KEY = (env.match(/^MESHY_API_KEY\s*=\s*(.+)$/m) || [])[1]?.trim().replace(/^["']|["']$/g, '');
if (!KEY) { console.error('No MESHY_API_KEY in .env'); process.exit(1); }
const [photo, out] = process.argv.slice(2);
const image_url = 'data:image/jpeg;base64,' + readFileSync(photo).toString('base64');
const r = await fetch('https://api.meshy.ai/openapi/v1/image-to-3d', {
  method: 'POST', headers: { Authorization: 'Bearer ' + KEY, 'Content-Type': 'application/json' },
  body: JSON.stringify({ image_url, ai_model: 'meshy-7.1', geometry_resolution: '4k', texture_resolution: '4k', should_texture: true, enable_pbr: true, should_remesh: false, target_formats: ['glb'] }),
});
const j = await r.json();
if (!r.ok || !j.result) { console.error('Meshy refused:', JSON.stringify(j).slice(0, 300)); process.exit(1); }
console.log('task', j.result);
let t, last = -1;
for (let i = 0; i < 180; i++) {
  await new Promise((s) => setTimeout(s, 10000));
  t = await (await fetch('https://api.meshy.ai/openapi/v1/image-to-3d/' + j.result, { headers: { Authorization: 'Bearer ' + KEY } })).json();
  if (t.progress !== last) { last = t.progress; console.log(t.status, t.progress + '%'); }
  if (['SUCCEEDED', 'FAILED', 'CANCELED'].includes(t.status)) break;
}
if (t?.status !== 'SUCCEEDED' || !t.model_urls?.glb) { console.error('Meshy did not finish:', t?.status, JSON.stringify(t?.task_error || '')); process.exit(1); }
writeFileSync(out, Buffer.from(await (await fetch(t.model_urls.glb)).arrayBuffer()));
console.log('SAVED', out, 'credits', t.consumed_credits ?? '?');
