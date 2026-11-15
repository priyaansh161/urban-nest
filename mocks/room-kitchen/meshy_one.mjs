// Meshy for a staging piece that has no listing (the kitchen's chimney, mixer): photo -> raw .glb -> tools/shrink-model.mjs.
// Same settings as tools/list-product.mjs (meshy-7.1, 4K geometry + textures, no remesh, ~35 credits).
//   node mocks/room-kitchen/meshy_one.mjs <photo.jpg> <out.glb>
import { readFileSync, writeFileSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { resolve } from 'node:path';
import { createRequire } from 'node:module';
const require = createRequire(new URL('../../tools/package.json', import.meta.url)); const sharp = require('sharp');
const KEY = Object.fromEntries(readFileSync('.env', 'utf8').split(/\r?\n/).filter(l => l.includes('=')).map(l => { const i = l.indexOf('='); return [l.slice(0, i).trim(), l.slice(i + 1).trim().replace(/^"|"$/g, '')]; })).MESHY_API_KEY;
const [photo, out] = process.argv.slice(2);
const jpg = await sharp(photo).flatten({ background: '#ffffff' }).resize(1024, 1024, { fit: 'contain', background: '#ffffff' }).jpeg({ quality: 92 }).toBuffer();
const H = { Authorization: 'Bearer ' + KEY, 'Content-Type': 'application/json' };
const mj = await (await fetch('https://api.meshy.ai/openapi/v1/image-to-3d', { method: 'POST', headers: H, body: JSON.stringify({ image_url: 'data:image/jpeg;base64,' + jpg.toString('base64'), ai_model: 'meshy-7.1', geometry_resolution: '4k', texture_resolution: '4k', should_texture: true, enable_pbr: true, should_remesh: false, target_formats: ['glb'] }) })).json();
if (!mj.result) throw new Error(JSON.stringify(mj));
let t; for (let i = 0; i < 180; i++) { await new Promise(r => setTimeout(r, 10000)); t = await (await fetch('https://api.meshy.ai/openapi/v1/image-to-3d/' + mj.result, { headers: H })).json(); if (['SUCCEEDED', 'FAILED', 'CANCELED'].includes(t.status)) break; }
if (t.status !== 'SUCCEEDED') throw new Error('Meshy: ' + t.status);
const raw = out.replace(/\.glb$/, '-raw.glb'); writeFileSync(raw, Buffer.from(await (await fetch(t.model_urls.glb)).arrayBuffer()));
const c = spawnSync(process.execPath, ['tools/shrink-model.mjs', resolve(raw), resolve(out)], { stdio: 'inherit' });
console.log('done', out, t.consumed_credits, 'credits', c.status);
